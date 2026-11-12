"""Налаштування RAG-агента."""
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

LAB_LOGFILE_NAME = "lab5"
BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
MODEL = "qwen25-4k"
MAX_STEPS = 6
MAX_STEPS_LONG = 25
TEMPERATURE = 0.2
NUM_CTX = 4096

SYSTEM = """Ти консультант з догляду за котами навчального центру «КотоЛаб».
Відповідай на питання тільки за доступними документами та інструментами.
Надані регламенти вигадані для лабораторної роботи і не є ветеринарними рекомендаціями.
Не вигадуй чисел і послуг; якщо питання стосується правил навчального центру, шукай їх через доступний пошук.
Не рахуй самостійно: для розрахунку корму є інструмент calc_food.
Якщо потрібного інструмента або факту немає, чесно повідом про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2
ALLOWED = ["search_docs", "vaccine_info", "calc_food"]
RUN_TAG = "rag"

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
WITH_TITLE = True
TOP_K = 3
MIN_SCORE = 0.5856
DOCS_DESCRIPTION = "B"
