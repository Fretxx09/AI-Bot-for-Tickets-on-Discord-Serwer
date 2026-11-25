import asyncio
import json
import logging
import os
from collections import defaultdict

import anthropic
import discord

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("ticket-ai")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = discord.Client(intents=intents)
ai = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY or None)

state = {"tracked": set(), "paused": set()}
locks = defaultdict(asyncio.Lock)
pending = set()


def load_state():
    path = config.TRACKED_CHANNELS_FILE
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        state["tracked"] = set(int(x) for x in data.get("tracked", []))
        state["paused"] = set(int(x) for x in data.get("paused", []))
    except (OSError, ValueError) as e:
        log.warning("Nie udało się wczytać %s: %s", path, e)


def save_state():
    path = config.TRACKED_CHANNELS_FILE
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"tracked": sorted(state["tracked"]), "paused": sorted(state["paused"])}, f, indent=2)
    os.replace(tmp, path)


def category_id_of(channel):
    if isinstance(channel, discord.Thread):
        parent = channel.parent
        return getattr(parent, "category_id", None) if parent else None
    return getattr(channel, "category_id", None)


def matches_new_channel_filters(channel):
    if config.NEW_CHANNEL_CATEGORY_IDS and category_id_of(channel) not in config.NEW_CHANNEL_CATEGORY_IDS:
        return False
    if config.NEW_CHANNEL_NAME_PREFIXES:
        name = channel.name.lower()
        if not any(name.startswith(p.lower()) for p in config.NEW_CHANNEL_NAME_PREFIXES):
            return False
    return True


def is_active_channel(channel):
    if channel.id in state["paused"]:
        return False
    if channel.id in config.CHANNEL_IDS or channel.id in state["tracked"]:
        return True
    if isinstance(channel, discord.Thread) and channel.parent_id in config.CHANNEL_IDS:
        return True
    return False


def is_staff(member):
    if not isinstance(member, discord.Member) or not config.STAFF_ROLE_IDS:
        return False
    return any(role.id in config.STAFF_ROLE_IDS for role in member.roles)


def message_text(message):
    parts = []
    if message.content:
        parts.append(message.content)
    for embed in message.embeds:
        if embed.title:
            parts.append(embed.title)
        if embed.description:
            parts.append(embed.description)
        for field in embed.fields:
            parts.append(f"{field.name}: {field.value}")
    for attachment in message.attachments:
        parts.append(f"[załącznik: {attachment.filename}]")
    return "\n".join(parts).strip()


async def build_conversation(channel):
    history = [m async for m in channel.history(limit=config.HISTORY_LIMIT)]
    history.reverse()
    messages = []
    for m in history:
        text = message_text(m)
        if not text:
            continue
        if m.author.id == bot.user.id:
            role = "assistant"
        else:
            role = "user"
            label = "[bot] " if m.author.bot else ("[support] " if is_staff(m.author) else "")
            text = f"{label}{m.author.display_name}: {text}"
        if messages and messages[-1]["role"] == role:
            messages[-1]["content"] += "\n\n" + text
        else:
            messages.append({"role": role, "content": text})
    while messages and messages[0]["role"] == "assistant":
        messages.pop(0)
    if messages and messages[-1]["role"] == "assistant":
        messages.pop()
    return messages


async def ask_ai(channel):
    messages = await build_conversation(channel)
    if not messages:
        return None
    system = config.SYSTEM_PROMPT + f"\n\nKanał ticketu: #{channel.name}"
    try:
        response = await ai.beta.messages.create(
            model=config.MODEL,
            max_tokens=config.MAX_TOKENS,
            system=system,
            messages=messages,
            output_config={"effort": config.EFFORT},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.RateLimitError as e:
        log.warning("Limit zapytań API: %s", e)
        return config.ERROR_MESSAGE
    except anthropic.APIStatusError as e:
        log.error("Błąd API (%s): %s", e.status_code, e.message)
        return config.ERROR_MESSAGE
    except anthropic.APIConnectionError as e:
        log.error("Brak połączenia z API: %s", e)
        return config.ERROR_MESSAGE
    if response.stop_reason == "refusal":
        return config.ERROR_MESSAGE
    text = "".join(block.text for block in response.content if block.type == "text").strip()
    return text or config.ERROR_MESSAGE


def split_message(text, limit=2000):
    chunks = []
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut <= 0:
            cut = text.rfind(" ", 0, limit)
        if cut <= 0:
            cut = limit
        chunks.append(text[:cut])
        text = text[cut:].lstrip()
    if text:
        chunks.append(text)
    return chunks


def try_track(channel):
    if not config.RESPOND_IN_NEW_CHANNELS:
        return
    if not matches_new_channel_filters(channel):
        return
    state["tracked"].add(channel.id)
    save_state()
    log.info("Nowy kanał ticketu: #%s (%s)", channel.name, channel.id)


@bot.event
async def on_ready():
    log.info("Zalogowano jako %s (%s)", bot.user, bot.user.id)
    log.info("Kanały z configu: %s | śledzone nowe: %d", config.CHANNEL_IDS, len(state["tracked"]))


@bot.event
async def on_guild_channel_create(channel):
    if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.StageChannel)):
        try_track(channel)


@bot.event
async def on_thread_create(thread):
    try_track(thread)
    if thread.id in state["tracked"] and not thread.me:
        try:
            await thread.join()
        except discord.HTTPException:
            pass


@bot.event
async def on_guild_channel_delete(channel):
    forget(channel.id)


@bot.event
async def on_thread_delete(thread):
    forget(thread.id)


def forget(channel_id):
    if channel_id in state["tracked"] or channel_id in state["paused"]:
        state["tracked"].discard(channel_id)
        state["paused"].discard(channel_id)
        save_state()


@bot.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return
    channel = message.channel
    if not is_active_channel(channel):
        return
    if is_staff(message.author):
        if config.STOP_WHEN_STAFF_REPLIES:
            state["paused"].add(channel.id)
            save_state()
            log.info("Support przejął kanał #%s", channel.name)
            if config.STAFF_TAKEOVER_MESSAGE:
                await channel.send(config.STAFF_TAKEOVER_MESSAGE)
            return
        if config.IGNORE_STAFF_MESSAGES:
            return
    lock = locks[channel.id]
    if lock.locked():
        pending.add(channel.id)
        return
    async with lock:
        target = message
        while True:
            pending.discard(channel.id)
            async with channel.typing():
                reply = await ask_ai(channel)
            if reply:
                chunks = split_message(reply)
                await target.reply(chunks[0], mention_author=False)
                for chunk in chunks[1:]:
                    await channel.send(chunk)
            if channel.id not in pending or not is_active_channel(channel):
                break
            target = channel.last_message or message


def main():
    if not config.DISCORD_TOKEN:
        raise SystemExit("Brak DISCORD_TOKEN w config.py lub zmiennych środowiskowych.")
    if not config.ANTHROPIC_API_KEY and not os.getenv("ANTHROPIC_AUTH_TOKEN"):
        raise SystemExit("Brak ANTHROPIC_API_KEY w config.py lub zmiennych środowiskowych.")
    load_state()
    bot.run(config.DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
