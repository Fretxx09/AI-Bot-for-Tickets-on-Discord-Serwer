import os

# ==========================================================
#  KONFIGURACJA BOTA AI DO TICKETÓW
# ==========================================================

# Token bota Discord (Discord Developer Portal -> Bot -> Reset Token).
# Najlepiej ustawić go jako zmienną środowiskową DISCORD_TOKEN,
# ale możesz też wkleić go bezpośrednio zamiast os.getenv(...).
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

# Klucz API Anthropic (https://console.anthropic.com -> API Keys).
# Najlepiej ustawić go jako zmienną środowiskową ANTHROPIC_API_KEY.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


# ----------------------------------------------------------
#  KANAŁY, NA KTÓRYCH BOT MA ODPOWIADAĆ
# ----------------------------------------------------------

# Lista ID kanałów, na których bot ma ZAWSZE odpowiadać.
# ID kopiujesz: Ustawienia Discord -> Zaawansowane -> Tryb dewelopera,
# potem PPM na kanał -> "Kopiuj ID kanału".
# Przykład: CHANNEL_IDS = [123456789012345678, 987654321098765432]
CHANNEL_IDS = []

# True  = bot odpowiada też na WSZYSTKICH NOWYCH kanałach (i wątkach),
#         które zostaną utworzone po uruchomieniu bota (np. nowe tickety).
# False = bot odpowiada tylko na kanałach z listy CHANNEL_IDS.
RESPOND_IN_NEW_CHANNELS = True

# (Opcjonalne) Ogranicza "nowe kanały" tylko do tych kategorii.
# Wpisz ID kategorii, w której bot od ticketów tworzy kanały.
# Pusta lista = nowe kanały z każdej kategorii.
# Przykład: NEW_CHANNEL_CATEGORY_IDS = [111111111111111111]
NEW_CHANNEL_CATEGORY_IDS = []

# (Opcjonalne) Ogranicza "nowe kanały" tylko do tych, których nazwa
# zaczyna się od jednego z podanych prefiksów.
# Pusta lista = dowolna nazwa.
# Przykład: NEW_CHANNEL_NAME_PREFIXES = ["ticket-", "zgloszenie-"]
NEW_CHANNEL_NAME_PREFIXES = []

# Plik, w którym bot zapisuje nowe kanały ticketów,
# żeby pamiętał je po restarcie.
TRACKED_CHANNELS_FILE = "data/tracked_channels.json"


# ----------------------------------------------------------
#  ADMINISTRACJA / SUPPORT
# ----------------------------------------------------------

# Lista ID ról supportu/administracji.
# Przykład: STAFF_ROLE_IDS = [222222222222222222]
STAFF_ROLE_IDS = []

# True = gdy ktoś z rolą z STAFF_ROLE_IDS napisze na tickecie,
#        bot przestaje odpowiadać na tym kanale (przejmuje człowiek).
STOP_WHEN_STAFF_REPLIES = True

# True = bot ignoruje wiadomości od osób z rolami supportu.
IGNORE_STAFF_MESSAGES = True


# ----------------------------------------------------------
#  USTAWIENIA AI
# ----------------------------------------------------------

# Model Claude używany do odpowiedzi.
MODEL = "claude-opus-5-5"

# Poziom wysiłku modelu: "low", "medium", "high", "xhigh", "max".
# "low" = szybkie i tańsze odpowiedzi, wyższe = dokładniejsze.
EFFORT = "low"

# Maksymalna długość odpowiedzi AI (w tokenach).
MAX_TOKENS = 4000

# Ile ostatnich wiadomości z ticketu bot bierze pod uwagę jako kontekst.
HISTORY_LIMIT = 30

# Nazwa Twojego serwera (używana w instrukcji dla AI).
SERVER_NAME = "Mój Serwer"

# Instrukcja dla AI - opisz tu swój serwer, zasady, FAQ, cennik itp.
# Im więcej informacji, tym lepsze odpowiedzi.
SYSTEM_PROMPT = f"""Jesteś pomocnym asystentem supportu na serwerze Discord "{SERVER_NAME}".
Odpowiadasz użytkownikom na ich ticketach (zgłoszeniach).
Odpowiadaj po polsku, uprzejmie, krótko i konkretnie.
Jeśli nie znasz odpowiedzi lub sprawa wymaga decyzji administracji
(np. zwroty pieniędzy, bany, odwołania), napisz, że przekazujesz sprawę
do administracji i ktoś z supportu wkrótce odpowie. Nie wymyślaj informacji.

Informacje o serwerze:
- (tu wpisz zasady, FAQ, godziny pracy supportu itd.)
"""

# Wiadomość wysyłana, gdy AI nie może odpowiedzieć (błąd lub odmowa).
ERROR_MESSAGE = "Przepraszam, nie mogę teraz odpowiedzieć. Ktoś z administracji wkrótce się odezwie."

# Wiadomość wysyłana jednorazowo, gdy support przejmie ticket
# (gdy STOP_WHEN_STAFF_REPLIES = True). Ustaw "" aby nic nie wysyłać.
STAFF_TAKEOVER_MESSAGE = ""
