"""Налаштування агента."""

from dotenv import load_dotenv

load_dotenv()

LAB_LOGFILE_NAME = "lab5"   # ім'я лога для agent.py і agent_runner.py: logs/lab5.log

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-3k"
# MODEL = "qwen25-4k"
MAX_STEPS = 6
TEMPERATURE = 0.2

SYSTEM = """Ти консультант ветеринарної клініки. Відповідаєш на питання
про догляд за котом.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2

ALLOWED = ["search_docs", "vaccine_info", "calc_food"]

RUN_TAG = "rag-docs"

NUM_CTX = 3072
# NUM_CTX = 4096
MAX_STEPS_LONG = 25

COMPRESS = "none"           # скорочення історії вимкнено (лабораторна № 4)
COMPRESS_AT = 2150
KEEP_LAST = 6

USE_STATE = False
STATE_RESULT_CHARS = 200

USE_CACHE = False

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "fixed"                   # "fixed" (за кількістю символів) або "paragraphs" (за абзацами)
CHUNK_SIZE = 200                          # розмір чанка в символах
CHUNK_OVERLAP = 0                         # перекриття чанків (для "fixed")
WITH_TITLE = False                        # дописувати назву документа до кожного чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.597                          # поріг схожості: для fixed-200-0 між N1 (0.596) і P1 (0.598)
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"
