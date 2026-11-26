"""Налаштування агента (варіант 7 — Подорожі)."""
from dotenv import load_dotenv

load_dotenv()

LAB_LOGFILE_NAME = "lab5"   # ім'я лога для agent.py і agent_runner.py: logs/lab5.log

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

# та сама модель, що в лаб. 4 (qwen2.5:3b), з вікном 4096 (лаб. 5: «розмір вікна (4096)»).
# Вікно 2048 з лаб. 4 було потрібне лише для довгої задачі; тут один результат search_docs
# (3 чанки) разом з описами інструментів у 2048 не вміщується (див. звіт, питання 8).
MODEL = "qwen25-4k"      # Modelfile: FROM qwen2.5:3b, PARAMETER num_ctx 4096
MAX_STEPS = 6
TEMPERATURE = 0.2

SYSTEM = """Ти помічник турагента. Підбираєш маршрути вихідного дня
та рахуєш бюджет поїздки.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2      # скільки помилок моделі поспіль допускаємо

# інструменти, які агентові дозволено викликати (buy_ticket – заборонений)
# лаб. 5: старий пошук search_routes замінено на search_docs
ALLOWED = ["search_docs", "transport_info", "calc_budget"]

# мітка прогону: за нею в Langfuse відрізнятимемо прогони
# RUN_TAG = "baseline"
# RUN_TAG = "checks"
# RUN_TAG = "ctx-control"
RUN_TAG = "rag"           # лаб. 5, крок 9: прогін tasks.json з новим пошуком

NUM_CTX = 4096          # розмір вікна моделі qwen25-4k
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі (з лаб. 4, тут не використовується)

COMPRESS_AT = 1000      # з лаб. 4; при COMPRESS = "none" не діє
KEEP_LAST = 6           # з лаб. 4; при COMPRESS = "none" не діє
STATE_RESULT_CHARS = 200  # з лаб. 4; при USE_STATE = False не діє

COMPRESS = "none"           # скорочення історії вимкнено (лабораторна № 4)
USE_STATE = False
USE_CACHE = False

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "fixed"                   # "fixed" (за кількістю символів) або "paragraphs" (за абзацами)
CHUNK_SIZE = 500                         # розмір чанка в символах (крок 5: fixed-500-100)
CHUNK_OVERLAP = 100                      # перекриття чанків (для "fixed")
WITH_TITLE = False                       # дописувати назву документа до кожного чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.605                        # поріг схожості (крок 5): між N1 0.5997 і найнижчим потрібним чанком P2 0.6088
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"
