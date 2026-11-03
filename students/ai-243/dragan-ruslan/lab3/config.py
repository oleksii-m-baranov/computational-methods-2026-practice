"""Налаштування агента."""

from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen2.5:3b"
MAX_STEPS = 8
TEMPERATURE = 0


MAX_RETRIES = 2 

# інструменти, які агентові дозволено викликати (варіант 9 - Ноутбуки)
ALLOWED = ["search_laptops", "laptop_info", "calc_installment"]

RUN_TAG = "checks"


SYSTEM = """Ти консультант магазину техніки. Підбираєш ноутбук
і рахуєш умови покупки.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

LAB_LOGFILE_NAME = "lab3"