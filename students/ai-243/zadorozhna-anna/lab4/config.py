"""Налаштування кулінарного агента."""
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

LAB_LOGFILE_NAME = "lab4"

MODEL = "llama32-3k"
MAX_STEPS = 6
TEMPERATURE = 0

SYSTEM = """Ти кухонний помічник. Допомагаєш підібрати страву
та розрахувати інгредієнти.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською.""" 

MAX_RETRIES = 2

ALLOWED = ["search_recipes", "product_info", "scale_amount"]

RUN_TAG = "ctx-control"

NUM_CTX = 3072
MAX_STEPS_LONG = 25


COMPRESS = "none"       # "none" або "trim": скорочувати історію чи ні
COMPRESS_AT = 1000    # скорочуємо, коли prompt_tokens перевищив це число
KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні

USE_STATE = False
STATE_RESULT_CHARS = 200

USE_CACHE = False       # чи кешувати виклики моделі