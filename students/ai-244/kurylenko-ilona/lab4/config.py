"""Налаштування агента."""

from dotenv import load_dotenv

load_dotenv()

LAB_LOGFILE_NAME = "lab4"

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-3k"
MAX_STEPS = 6
TEMPERATURE = 0.2

SYSTEM = """Ти консультант ветеринарної клініки. Відповідаєш на питання
про догляд за котом.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2

ALLOWED = ["search_articles", "vaccine_info", "calc_food"]

RUN_TAG = "ctx-control"

NUM_CTX = 3072
MAX_STEPS_LONG = 25

COMPRESS = "none"       # "none" або "trim": режим скорочення історії
COMPRESS_AT = 2150      # поріг скорочення для вікна 3072 токени
KEEP_LAST = 6           # кількість останніх повідомлень, які залишаємо

USE_STATE = False
STATE_RESULT_CHARS = 200

USE_CACHE = False  # Чи використовувати кеш відповідей моделі
