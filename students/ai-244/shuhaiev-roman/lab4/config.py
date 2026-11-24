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

LAB_LOGFILE_NAME = "lab4"   # ім'я лога для agent.py і agent_runner.py

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-3k"         # модель з малим вікном (qwen2.5:3b, num_ctx 3072); спершу була qwen25-4k
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
ALLOWED = ["search_exercises", "schedule_info", "calc_calories"]

# мітка прогонів у Langfuse
RUN_TAG = "ctx-control"

NUM_CTX = 3072          # розмір вікна (випадок C на 4096 -> зменшено до 3072)
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі (MAX_STEPS не змінюємо)

COMPRESS = "none"       # "none", "trim" або "summary": скорочувати історію чи ні
# скорочуємо, коли prompt_tokens перевищив це число (для вікна 3072 методичка радить 2150);
# можна перевизначити змінною середовища COMPRESS_AT для пробних прогонів
COMPRESS_AT = int(os.getenv("COMPRESS_AT", "2150"))
KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні

USE_STATE = False       # чи додавати в контекст збережені результати
STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини

USE_CACHE = False       # чи кешувати виклики моделі
