"""Налаштування агента. Лабораторна робота №3, варіант 2."""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

# Логування
LAB_LOGFILE_NAME = "lab5"

# Ollama
BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

# Параметри з ЛР2 — не змінювати між прогонами
MODEL = "qwen25-culinary-4k"
MAX_STEPS = 6
TEMPERATURE = 0

# Оригінальний системний промпт ЛР2
SYSTEM = """Ти кухонний помічник. Допомагаєш підібрати страву
та розрахувати інгредієнти.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

# Ліміт послідовних помилок моделі
MAX_RETRIES = 2

# Дозволені інструменти
ALLOWED = [
    "search_docs",
    "product_info",
    "scale_amount",
]

# Перший прогін
RUN_TAG = "lab5-rag"

NUM_CTX = 4096
MAX_STEPS_LONG = 25
COMPRESS = "none"
COMPRESS_AT = 2600
KEEP_LAST = 6
USE_STATE = False
STATE_RESULT_CHARS = 120
USE_CACHE = False

EMBED_MODEL = "bge-m3"
DOC_DIRS = ["data/corpus", "data/docs"]
INDEX_DIR = "index"
CHUNK_METHOD = "paragraphs"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 0
WITH_TITLE = False
MAX_OUTPUT_TOKENS = 192
TOP_K = 3
MIN_SCORE = 0.48
DOCS_DESCRIPTION = "B"
