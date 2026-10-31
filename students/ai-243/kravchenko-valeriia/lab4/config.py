"""Налаштування агента."""
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "llama32-4k"
MAX_STEPS = 8
TEMPERATURE = 0

SYSTEM = """Ти оператор служби доставки. Перевіряєш правила перевезення
та рахуєш вартість відправлення.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

LAB_LOGFILE_NAME = "lab4"

MAX_RETRIES = 2
ALLOWED = ["search_rules", "tariff_info", "calc_price"]
RUN_TAG = "ctx-control"

NUM_CTX = 4096
MAX_STEPS_LONG = 25

COMPRESS = "none"
COMPRESS_AT = 2800
KEEP_LAST = 6

USE_STATE = False       # чи додавати в контекст збережені результати
STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини

USE_CACHE = False       # чи кешувати виклики моделі