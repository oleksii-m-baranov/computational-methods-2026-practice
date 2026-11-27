"""Налаштування кулінарного агента."""
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

LAB_LOGFILE_NAME = "lab5"

MODEL = "qwen4b-3k"
MAX_STEPS = 6
TEMPERATURE = 0

SYSTEM = """Ти кухонний помічник. Допомагаєш підібрати страву
та розрахувати інгредієнти.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською.""" 

MAX_RETRIES = 2

ALLOWED = ["search_docs", "product_info", "scale_amount"]

RUN_TAG = "ctx-control"

NUM_CTX = 3072
MAX_STEPS_LONG = 25

COMPRESS_AT = 1000    # скорочуємо, коли prompt_tokens перевищив це число
KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні

STATE_RESULT_CHARS = 200

COMPRESS = "none"           # скорочення історії вимкнено (лабораторна № 4)
USE_STATE = False
USE_CACHE = False

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "fixed"                   # "fixed" (за кількістю символів) або "paragraphs" (за абзацами)
CHUNK_SIZE = 500                         # розмір чанка в символах
CHUNK_OVERLAP = 0                        # перекриття чанків (для "fixed")
WITH_TITLE = False                       # дописувати назву документа до кожного чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.5                          # поріг схожості: у кроці 5 ви підберете значення
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"