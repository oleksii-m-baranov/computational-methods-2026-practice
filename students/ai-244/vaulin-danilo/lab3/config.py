"""Налаштування агента."""

from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen3:4b"
MAX_STEPS = 6
TEMPERATURE = 0

LAB_LOGFILE_NAME = "lab3"

SYSTEM = """Ти помічник бібліотеки. Допомагаєш читачам знайти книжку
та дізнатися умови видачі.
Не вигадуй дані – усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2

ALLOWED = ["search_books", "book_info", "calculate"]

RUN_TAG = "checks"