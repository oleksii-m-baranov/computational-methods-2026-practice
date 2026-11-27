from dotenv import load_dotenv
load_dotenv()

"""Налаштування агента."""

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-3k"
MAX_STEPS = 8
TEMPERATURE = 0

SYSTEM = """Ти оператор служби доставки. Перевіряєш правила перевезення
та рахуєш вартість відправлення.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2

ALLOWED = ["tariff_info", "calc_price", "search_docs"]

RUN_TAG = "ctx-control"

LAB_LOGFILE_NAME = "lab5"

NUM_CTX = 3072
MAX_STEPS_LONG = 25

KEEP_LAST = 6
COMPRESS_AT = 2150
STATE_RESULT_CHARS = 200

COMPRESS = "none"
USE_STATE = False
USE_CACHE = False

EMBED_MODEL = "bge-m3"
DOC_DIRS = ["data/corpus", "data/docs"]
INDEX_DIR = "index"
CHUNK_METHOD = "paragraphs"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 0
WITH_TITLE = False
TOP_K = 3
MIN_SCORE = 0.60
DOCS_DESCRIPTION = "B"
