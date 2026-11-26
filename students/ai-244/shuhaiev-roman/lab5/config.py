"""Налаштування агента."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# пакет utils з кореня репозиторію (якщо не встановлено через pip install -e .)
try:
    import utils.lab_logger  # noqa: F401
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

LAB_LOGFILE_NAME = "lab5"   # ім'я лога для agent.py і agent_runner.py: logs/lab5.log

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-4k"         # модель з ЛР4: qwen2.5:3b з вікном 4096
MAX_STEPS = 6
TEMPERATURE = 0

SYSTEM = """Ти помічник тренажерного залу. Підбираєш вправи,
повідомляєш розклад і рахуєш навантаження.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2      # скільки помилок моделі поспіль допускаємо

# інструменти, які агентові дозволено викликати (book_session – заборонена дія)
ALLOWED = ["search_docs", "schedule_info", "calc_calories"]   # старий search_exercises замінено

# мітка прогонів у Langfuse
RUN_TAG = "ctx-control"

NUM_CTX = 4096          # розмір вікна
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі (MAX_STEPS не змінюємо)

COMPRESS = "none"       # "none", "trim" або "summary": скорочувати історію чи ні
# скорочуємо, коли prompt_tokens перевищив це число (для вікна 3072 методичка радить 2150);
# можна перевизначити змінною середовища COMPRESS_AT для пробних прогонів
COMPRESS_AT = int(os.getenv("COMPRESS_AT", "2150"))
KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні

USE_STATE = False       # чи додавати в контекст збережені результати
STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини

USE_CACHE = False       # чи кешувати виклики моделі

COMPRESS = "none"           # скорочення історії вимкнено (лабораторна № 4)
USE_STATE = False
USE_CACHE = False

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "fixed"                   # обрано в кроці 5: fixed-200-0 (hit@3 = 1.00, найменший результат)
CHUNK_SIZE = 200                         # розмір чанка в символах
CHUNK_OVERLAP = 0                        # перекриття чанків (для "fixed")
WITH_TITLE = False                       # дописувати назву документа до кожного чанка
TOP_K = 3                                # скільки чанків повертає пошук
MIN_SCORE = 0.50                         # поріг схожості: вибрано в кроці 5
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"
