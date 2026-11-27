"""Налаштування агента."""
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-4k"
MAX_STEPS = 6
TEMPERATURE = 0

SYSTEM = """Ти помічник у спортзалі. Допомагаєш підібрати вправи,
перевірити розклад занять і порахувати витрату калорій.
Не вигадуй дані – усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2
ALLOWED = ["search_docs", "schedule_info", "calc_calories"]
RUN_TAG = "rag"
LAB_LOGFILE_NAME = "lab5"

NUM_CTX = 4096
MAX_STEPS_LONG = 25

COMPRESS = "none"
COMPRESS_AT = 2800
KEEP_LAST = 6
USE_STATE = False
STATE_RESULT_CHARS = 200
USE_CACHE = False

EMBED_MODEL = "bge-m3"
DOC_DIRS = ["data/corpus", "data/docs"]
INDEX_DIR = "index"
CHUNK_METHOD = "paragraphs"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 0
WITH_TITLE = False
TOP_K = 3
MIN_SCORE = 0.62
DOCS_DESCRIPTION = "B"