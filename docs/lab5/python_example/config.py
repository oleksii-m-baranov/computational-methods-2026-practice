from dotenv import load_dotenv

load_dotenv()

LAB_LOGFILE_NAME = "lab5"

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

# MODEL = "qwen3:4b"
MODEL = "qwen3:4b-instruct-4k"
# MODEL = "qwen3:4b-instruct-3k"
# MODEL = "gemma4:26b-a4b-it-qat"
MAX_STEPS = 6
TEMPERATURE = 0

SYSTEM = """Ти помічник бібліотеки. Допомагаєш читачам знайти книжку
та дізнатися умови видачі.
Не вигадуй дані – усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2      # скільки помилок моделі поспіль допускаємо

# інструменти, які агентові дозволено викликати, приклад для варіанта 1
# ALLOWED = ["search_books", "book_info", "calculate"]
ALLOWED = ["search_docs", "book_info", "calculate"]

# мітка прогону: за нею в Langfuse відрізнятимемо прогони
# RUN_TAG = "baseline"
# RUN_TAG = "checks"
RUN_TAG = "ctx-control"

NUM_CTX = 4096          # розмір вікна, який ви задасте в кроці 2
# NUM_CTX = 3072          # розмір вікна, який ви задасте в кроці 2
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі (MAX_STEPS не змінюємо)

COMPRESS = "none"       # "none" або "trim": скорочувати історію чи ні
# COMPRESS_AT = 2800      # скорочуємо, коли prompt_tokens перевищив це число
# COMPRESS_AT = 2150      # скорочуємо, коли prompt_tokens перевищив це число
COMPRESS_AT = 1500      # скорочуємо, коли prompt_tokens перевищив це число
KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні

USE_STATE = False       # чи додавати в контекст збережені результати
STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини

USE_CACHE = False       # чи кешувати виклики моделі

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "paragraphs"              # "fixed" (за кількістю символів) або "paragraphs" (за абзацами)
CHUNK_SIZE = 800                         # розмір чанка в символах
CHUNK_OVERLAP = 0                        # перекриття чанків (для "fixed")
WITH_TITLE = False                       # дописувати назву документа до кожного чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.0                          # поріг схожості: у кроці 5 ви підберете значення
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"
