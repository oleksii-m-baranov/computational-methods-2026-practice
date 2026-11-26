
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
MODEL = "qwen25-3k"

MAX_STEPS = 6
TEMPERATURE = 0
MAX_RETRIES = 2

ALLOWED = [
    "search_recipes",
    "product_info",
    "scale_amount",
]

RUN_TAG = "ctx-control"

SYSTEM = """Ти кухонний помічник. Допомагаєш підібрати страву
та розрахувати інгредієнти.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

LAB_LOGFILE_NAME = "lab4"

NUM_CTX = 3072

MAX_STEPS_LONG = 25

SERIAL_TOOL_CALLS = True
COMPRESS = "none"
COMPRESS_AT = 2150
KEEP_LAST = 6
USE_STATE = False
STATE_RESULT_CHARS = 200

USE_CACHE = False
