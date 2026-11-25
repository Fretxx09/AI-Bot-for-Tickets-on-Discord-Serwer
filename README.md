# AI Bot for Tickets on Discord Serwer

Bot Discord, który automatycznie odpowiada na ticketach przy użyciu AI (Claude od Anthropic).

## Funkcje
- Odpowiada na kanałach podanych w `config.py` (`CHANNEL_IDS`)
- Opcjonalnie odpowiada na **wszystkich nowo tworzonych kanałach/wątkach** (`RESPOND_IN_NEW_CHANNELS = True`), z filtrem po kategorii lub prefiksie nazwy
- Pamięta nowe tickety po restarcie (`data/tracked_channels.json`)
- Czyta historię ticketu jako kontekst rozmowy
- Gdy support napisze na tickecie, bot przestaje tam odpowiadać (`STOP_WHEN_STAFF_REPLIES`)

## Instalacja
1. Python 3.10+
2. `pip install -r requirements.txt`
3. W [Discord Developer Portal](https://discord.com/developers/applications) -> Bot włącz **Message Content Intent** i **Server Members Intent**
4. Zaproś bota z uprawnieniami: View Channels, Send Messages, Read Message History, Send Messages in Threads
5. Ustaw zmienne środowiskowe `DISCORD_TOKEN` i `ANTHROPIC_API_KEY` (albo wpisz je w `config.py`)
6. Uzupełnij `config.py` (ID kanałów, role supportu, opis serwera w `SYSTEM_PROMPT`)
7. `python bot.py`
