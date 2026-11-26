"""Налаштування агента."""

from dotenv import load_dotenv
load_dotenv() 

LAB_LOGFILE_NAME = "lab5" 

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen3-4k"
MAX_STEPS = 6
TEMPERATURE = 0

SYSTEM = """Ти помічник тренажерного залу. Підбираєш вправи,
повідомляєш розклад і рахуєш навантаження.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2  

ALLOWED = ["search_docs", "schedule_info", "calc_calories"]

RUN_TAG = "ctx-control"  

NUM_CTX = 4096
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі

COMPRESS = "none"
COMPRESS_AT = 2150
KEEP_LAST = 6           # скільки останніх повідомлень лишати

USE_STATE = False       # чи додавати в контекст збережені результати
STATE_RESULT_CHARS = 200

USE_CACHE = False 

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "fixed"              # "fixed" або "paragraphs"
CHUNK_SIZE = 500                         # розмір чанка в символах
CHUNK_OVERLAP = 0                        # перекриття чанків (для "fixed")
WITH_TITLE = False                       # дописувати назву документа до чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.55                          # поріг схожості, підберемо в кроці 5
DOCS_DESCRIPTION = "B"                   # який опис search_docs: "A", "B" або "C"