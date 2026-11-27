from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-4k"
MAX_STEPS = 6
TEMPERATURE = 0

LAB_LOGFILE_NAME = "lab5"
MAX_RETRIES = 2
ALLOWED = ["search_docs", "schedule_info", "calc_calories"]
RUN_TAG = "ctx-control"

NUM_CTX = 4096
MAX_STEPS_LONG = 25

COMPRESS = "none"
COMPRESS_AT = 1650
KEEP_LAST = 6

USE_STATE = False
STATE_RESULT_CHARS = 200

USE_CACHE = False


SYSTEM = """Ти помічник тренажерного залу. Підбираєш вправи, повідомляєш розклад і рахуєш навантаження. 
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом. 
Не рахуй самостійно, для цього є окремий інструмент. 
Якщо потрібного інструмента немає, чесно скажи про це. 
Коли даних достатньо, дай коротку відповідь українською."""


SYSTEM = SYSTEM + (
    " ЗАБОРОНЕНО викликати більше одного інструмента за один крок — викликай рівно 1 інструмент і чекай відповідь. "
    "Приклади аргументів: search_docs(query='спина') без чисел; "
    "schedule_info(activity='кардіо') — назва заняття для поточної позиції. "
    "Порахуй калорії через calc_calories для всіх 6 позицій і назви точну суму в кінці."
) # Фікс для того, щоб агент не намагався викликати всі інструменти за один запит
# --- Налаштування RAG (Лабораторна № 5) ---
EMBED_MODEL = "bge-m3"
DOC_DIRS = ["data/corpus", "data/docs"]
INDEX_DIR = "index"
CHUNK_METHOD = "paragraphs"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 0
WITH_TITLE = False
TOP_K = 3
MIN_SCORE = 0.599
DOCS_DESCRIPTION = "B"
