"""Налаштування агента."""

from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-4k"       # локальна модель з вікном 4096
MAX_STEPS = 8
TEMPERATURE = 0

MAX_RETRIES = 2

# інструменти, які агентові дозволено викликати (варіант 9 - Вибір ноутбука)
# ALLOWED = ["search_laptops", "laptop_info", "calc_installment"]
ALLOWED = ["search_docs", "laptop_info", "calc_installment"]

RUN_TAG = "ctx-control"   # мітка прогонів у Langfuse

SYSTEM = """Ти консультант магазину техніки. Підбираєш ноутбук
і рахуєш умови покупки.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

LAB_LOGFILE_NAME = "lab5"   # ім'я лога для agent.py і agent_runner.py: logs/lab5.log

NUM_CTX = 4096          # розмір вікна
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі (MAX_STEPS не змінюємо)

COMPRESS = "none"           # скорочення історії вимкнено (лабораторна № 4)
COMPRESS_AT = 2800          # скорочуємо, коли prompt_tokens перевищив це число
KEEP_LAST = 6               # скільки останніх повідомлень лишати при обрізанні

USE_STATE = False
STATE_RESULT_CHARS = 200    # довші результати в стані скорочуються до цієї довжини

USE_CACHE = False

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "paragraphs"              # "fixed" (за кількістю символів) або "paragraphs" (за абзацами)
CHUNK_SIZE = 800                         # розмір чанка в символах
CHUNK_OVERLAP = 0                        # перекриття чанків (для "fixed")
WITH_TITLE = False                       # дописувати назву документа до кожного чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.58                         # поріг схожості: обрано у кроці 5 (між 0.560 і 0.662)
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"
