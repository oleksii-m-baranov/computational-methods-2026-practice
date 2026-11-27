from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
MODEL = "qwen25-4k"
TEMPERATURE = 0.0
NUM_CTX = 4096

MAX_STEPS = 10
MAX_RETRIES = 3
ALLOWED = ["search_docs", "book_info", "calculate"]

SYSTEM = (
    "Ти помічник бібліотеки. Допомагаєш читачам знайти книжку та дізнатися умови видачі.\n"
    "Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.\n"
    "Не рахуй самостійно, для цього є окремий інструмент.\n"
    "Якщо потрібного інструмента немає, чесно скажи про це.\n"
    "Коли даних достатньо, дай коротку відповідь українською."
)

LAB_LOGFILE_NAME = "lab5"
RUN_TAG = "rag-tasks"

COMPRESS = "none"           # скорочення історії вимкнено (лабораторна № 4)
COMPRESS_AT = 2000
USE_STATE = False
USE_CACHE = False

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "fixed"                   # "fixed" (за кількістю символів) або "paragraphs" (за абзацами)
CHUNK_SIZE = 500                         # розмір чанка в символах
CHUNK_OVERLAP = 100                      # перекриття чанків (для "fixed")
WITH_TITLE = False                       # дописувати назву документа до кожного чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.60                         # підібраний поріг схожості
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"