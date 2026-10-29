"""Налаштування агента (Варіант 7 — Подорожі)."""

from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "llama3.2:3b"
MAX_STEPS = 6
TEMPERATURE = 0

MAX_RETRIES = 2       # кількість помилок моделі поспіль
ALLOWED = ["search_routes", "route_info", "calculate_trip"] # інструменти 
RUN_TAG = "checks"  # мітка прогону для Langfuse
LAB_LOGFILE_NAME = "lab3"

SYSTEM = """Ти помічник турагента. Підбираєш маршрути вихідного дня
та рахуєш бюджет поїздки.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""