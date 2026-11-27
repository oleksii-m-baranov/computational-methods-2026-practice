"""Налаштування агента."""
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-4k"
MAX_STEPS = 8
TEMPERATURE = 0

SYSTEM = """Ти оператор служби доставки. Перевіряєш правила перевезення
та рахуєш вартість відправлення.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

LAB_LOGFILE_NAME = "lab5"

MAX_RETRIES = 2
ALLOWED = ["search_docs", "tariff_info", "calc_price"]
RUN_TAG = "ctx-control"

NUM_CTX = 4096
MAX_STEPS_LONG = 25

COMPRESS_AT = 2800
KEEP_LAST = 6

STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини

COMPRESS = "none"
USE_STATE = False
USE_CACHE = False

EMBED_MODEL = "bge-m3"
DOC_DIRS = ["data/corpus", "data/docs"]
INDEX_DIR = "index"
CHUNK_METHOD = "fixed"
CHUNK_SIZE = 200
CHUNK_OVERLAP = 0
WITH_TITLE = False
TOP_K = 3
MIN_SCORE = 0.595
DOCS_DESCRIPTION = "B"