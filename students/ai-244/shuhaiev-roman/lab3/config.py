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

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen2.5:3b"
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

# мітка прогону: за нею в Langfuse відрізнятимемо прогони
# baseline – агент з ЛР2 без змін, checks – агент з перевірками.
# Можна задати змінною середовища RUN_TAG або аргументом agent_runner.py.
RUN_TAG = os.getenv("RUN_TAG", "checks")

# лог: logs/lab3_baseline.log або logs/lab3_checks.log
LAB_LOGFILE_NAME = f"lab3_{RUN_TAG}"
