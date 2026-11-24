"""Налаштування агента."""

from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-3k"
MAX_STEPS = 6
TEMPERATURE = 0.2

SYSTEM = """Ти консультант з догляду за кімнатними рослинами.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2

ALLOWED = ["search_docs", "fertilizer_info", "calc_dose"]

RUN_TAG = "ctx-control"

LAB_LOGFILE_NAME = "lab5"

NUM_CTX = 3072          # розмір вікна, який ви задасте в кроці 1
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі (MAX_STEPS не змінюємо)

COMPRESS = "none"       # "none" або "trim": скорочувати історію чи ні
COMPRESS_AT = 2150      # скорочуємо, коли prompt_tokens перевищив це число
KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні

USE_STATE = False
STATE_RESULT_CHARS = 200
USE_CACHE = False

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "fixed"              # "fixed" (за кількістю символів) або "paragraphs" (за абзацами)
CHUNK_SIZE = 500                         # розмір чанка в символах
CHUNK_OVERLAP = 100                        # перекриття чанків (для "fixed")
WITH_TITLE = False                       # дописувати назву документа до кожного чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.0                          # поріг схожості: у кроці 5 ви підберете значення
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"

## CHUNK_METHOD, CHUNK_SIZE, CHUNK_OVERLAP, WITH_TITLE
## "name": "fixed-500-100",     "method": "fixed",      "size": 500,  "overlap": 100, "title": False