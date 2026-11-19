"""Налаштування агента."""
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-2k"
MAX_STEPS = 6
TEMPERATURE = 0

SYSTEM = """Ти помічник у спортзалі. Допомагаєш підібрати вправи,
перевірити розклад занять і порахувати витрату калорій.
Не вигадуй дані – усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2
ALLOWED = ["search_exercises", "schedule_info", "calc_calories"]
RUN_TAG = "ctx-control"
LAB_LOGFILE_NAME = "lab4"

NUM_CTX = 2048
MAX_STEPS_LONG = 25
COMPRESS = "none"
COMPRESS_AT = 1450
KEEP_LAST = 6
USE_STATE = False
STATE_RESULT_CHARS = 200
USE_CACHE = False