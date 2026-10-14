"""Налаштування агента (варіант 7 — Подорожі)."""
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen2.5:3b"
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
ALLOWED = ["search_routes", "transport_info", "calc_budget"]

# мітка прогону: за нею в Langfuse відрізнятимемо прогони
# RUN_TAG = "baseline"
RUN_TAG = "checks"

# лог кожного прогону – в окремий файл: lab3_baseline.log / lab3_checks.log
LAB_LOGFILE_NAME = f"lab3_{RUN_TAG}"
