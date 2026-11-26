"""Налаштування агента."""
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-2k"
MAX_STEPS = 6
TEMPERATURE = 0.2

MAX_RETRIES = 2
ALLOWED = ["search_plants", "fertilizer_info", "calc_dose"]
RUN_TAG = "ctx-control"
LAB_LOGFILE_NAME = "lab4"

SYSTEM = """Ти консультант з догляду за кімнатними рослинами.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

NUM_CTX = 2048          # розмір вікна (звужено за випадком C)
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі

COMPRESS = "none"       # "none", "trim" або "summary"
COMPRESS_AT = 1150      # поріг стиснення для вікна 2048
KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні

USE_STATE = False       # чи додавати в контекст збережені результати
STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини

USE_CACHE = False       # чи кешувати виклики моделі