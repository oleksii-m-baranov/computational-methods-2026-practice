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

ALLOWED = ["tariff_info", "calc_price", "search_docs"]   # у кроці 6 search_rules -> search_docs

RUN_TAG = "ctx-control"

LAB_LOGFILE_NAME = "lab5"   # ім'я лога для agent.py і agent_runner.py: logs/lab5.log

NUM_CTX = 3072
MAX_STEPS_LONG = 25

KEEP_LAST = 6
COMPRESS_AT = 2150
STATE_RESULT_CHARS = 200

COMPRESS = "none"           # скорочення історії вимкнено (лабораторна № 4)
USE_STATE = False
USE_CACHE = False

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "paragraphs"              # "fixed" (за кількістю символів) або "paragraphs" (за абзацами)
CHUNK_SIZE = 800                         # розмір чанка в символах
CHUNK_OVERLAP = 0                        # перекриття чанків (для "fixed")
WITH_TITLE = False                       # дописувати назву документа до кожного чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.60
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"
