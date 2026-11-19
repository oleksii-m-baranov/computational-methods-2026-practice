"""Налаштування агента."""

from dotenv import load_dotenv
load_dotenv() 

LAB_LOGFILE_NAME = "lab4" 

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen3-3k"
MAX_STEPS = 6
TEMPERATURE = 0

SYSTEM = """Ти помічник тренажерного залу. Підбираєш вправи,
повідомляєш розклад і рахуєш навантаження.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2  

ALLOWED = ["search_exercises", "schedule_info", "calc_calories"]

RUN_TAG = "ctx-control"  

NUM_CTX = 3072
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі

COMPRESS = "none"       # "none", "trim" або "summary" (перемикає measure.py)
COMPRESS_AT = 2150
KEEP_LAST = 6           # скільки останніх повідомлень лишати

USE_STATE = False       # чи додавати в контекст збережені результати
STATE_RESULT_CHARS = 200

USE_CACHE = False       # чи кешувати виклики моделі