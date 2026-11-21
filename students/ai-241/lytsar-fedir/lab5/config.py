from dotenv import load_dotenv
load_dotenv()

MAX_RETRIES = 2
ALLOWED = ["search_docs", "fertilizer_info", "calc_dose"]
RUN_TAG = "ctx-control"
LAB_LOGFILE_NAME = "lab5"

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

NUM_CTX = 3072
MAX_STEPS_LONG = 25

COMPRESS = "none"
COMPRESS_AT = 2150
KEEP_LAST = 6

USE_STATE = False
STATE_RESULT_CHARS = 200

USE_CACHE = False


EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "paragraphs"              # "fixed" (за кількістю символів) або "paragraphs" (за абзацами)
CHUNK_SIZE = 800                         # розмір чанка в символах
CHUNK_OVERLAP = 0                        # перекриття чанків (для "fixed")
WITH_TITLE = False                       # дописувати назву документа до кожного чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.55                         # поріг схожості: у кроці 5 ви підберете значення
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"