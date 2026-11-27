"""Configuration settings for Library RAG Agent (Variant 11, Lab 5)."""
from dotenv import load_dotenv

load_dotenv()

LAB_LOGFILE_NAME = "lab5"

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-4k"
MAX_STEPS = 6
TEMPERATURE = 0

SYSTEM = """Ти помічник бібліотеки. Допомагаєш читачам знайти книжку
та дізнатися умови видачі.
Не вигадуй дані – усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2      # скільки помилок моделі поспіль допускаємо

# інструменти, які агентові дозволено викликати (варіант 11)
ALLOWED = ["search_docs", "book_info", "calculate"]

# мітка прогону: за нею в Langfuse відрізнятимемо прогони
RUN_TAG = "rag"

NUM_CTX = 4096          # розмір вікна (4096 за методичкою ЛР №5)
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі (MAX_STEPS не змінюємо)

COMPRESS = "none"       # скорочення історії вимкнено (лабораторна № 4)
COMPRESS_AT = 1100
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
MIN_SCORE = 0.60                         # поріг схожості (підібрано в кроці 5: max(none)=0.553 < 0.60 < min(answerable)=0.642)
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"
