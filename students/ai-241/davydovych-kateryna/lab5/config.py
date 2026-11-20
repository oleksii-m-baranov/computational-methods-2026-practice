"""Налаштування агента."""
from dotenv import load_dotenv

load_dotenv()                     # ключі Langfuse з файлу .env

LAB_LOGFILE_NAME = "lab5"         # ім'я лога для agent.py і agent_runner.py: logs/lab5.log

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-3b-4k"            # копія qwen2.5:3b з вікном 4096 (Modelfile з лабораторної № 4)
MAX_STEPS = 8
TEMPERATURE = 0

SYSTEM = """Ти консультант магазину техніки. Підбираєш ноутбук
і рахуєш умови покупки.
Не вигадуй дані – усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2      # скільки помилок моделі поспіль допускаємо

# інструменти, які агентові дозволено викликати (варіант 9)
ALLOWED = ["search_docs", "laptop_info", "calc_installment"]   # search_laptops замінено векторним пошуком

# мітка прогонів у Langfuse
RUN_TAG = "rag"

NUM_CTX = 4096          # розмір вікна моделі qwen25-3b-4k
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі (MAX_STEPS не змінюємо)

COMPRESS_AT = 1500      # параметри скорочення з лаб. 4 (COMPRESS = "none", тож не використовуються)
KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні

STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини

COMPRESS = "none"           # скорочення історії вимкнено (лабораторна № 4)
USE_STATE = False
USE_CACHE = False

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "fixed"                   # "fixed" (за кількістю символів) або "paragraphs" (за абзацами); вибір у кроці 5: fixed-500-100
CHUNK_SIZE = 500                         # розмір чанка в символах
CHUNK_OVERLAP = 100                      # перекриття чанків (для "fixed")
WITH_TITLE = False                       # дописувати назву документа до кожного чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.60                         # поріг схожості (крок 5): компроміс, відсікає N2 (0.597), але й P3 (0.555)
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"
