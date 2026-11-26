import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
MODEL = "qwen25-3k"
MAX_STEPS = 6
TEMPERATURE = 0.0

LAB_LOGFILE_NAME = "lab5"
MAX_RETRIES = 2
ALLOWED = ["search_docs", "product_info", "scale_amount"]
RUN_TAG = "ctx-control"

SYSTEM = """Ти кухонний помічник. Допомагаєш підібрати страву
та розрахувати інгредієнти.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

NUM_CTX = 3072
MAX_STEPS_LONG = 25

COMPRESS = "none"
USE_STATE = False
USE_CACHE = False

EMBED_MODEL = "bge-m3"
DOC_DIRS = ["data/corpus", "data/docs"]
INDEX_DIR = "index"
CHUNK_METHOD = "fixed"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 0
WITH_TITLE = False
TOP_K = 3
MIN_SCORE = 0.62
DOCS_DESCRIPTION = "B"

COMPRESS_AT = 2000