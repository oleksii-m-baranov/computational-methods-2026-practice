"""Налаштування агента (Варіант 7 — Подорожі)."""

from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

# Використовуємо створену модель з вузьким вікном через Modelfile (крок 1)
MODEL = "llama32-4k"
MAX_STEPS = 6
TEMPERATURE = 0

MAX_RETRIES = 2       # кількість помилок моделі поспіль
ALLOWED = ["search_docs", "route_info", "calculate_trip"]
RUN_TAG = "ctx-control"  # мітка прогону для Langfuse
LAB_LOGFILE_NAME = "lab5"
NUM_CTX = 4096          # розмір вікна, заданий у Modelfile (або 3072 за потреби)
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі
COMPRESS_AT = 2800      # скорочуємо, коли prompt_tokens перевищив цей поріг
KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні
STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини
COMPRESS = "none"           # скорочення історії вимкнено (лабораторна № 4)
USE_STATE = False
USE_CACHE = False

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "paragraphs"              # "fixed" (за кількістю символів) або "paragraphs" (за абзацами)
CHUNK_SIZE = 500                         # розмір чанка в символах
CHUNK_OVERLAP = 0                        # перекриття чанків (для "fixed")
WITH_TITLE = False                       # дописувати назву документа до кожного чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.59                          # поріг схожості: у кроці 5 ви підберете значення
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"

SYSTEM = """Ти помічник турагента. Підбираєш маршрути вихідного дня
та рахуєш бюджет поїздки.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""