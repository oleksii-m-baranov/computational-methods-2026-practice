"""Configuration settings for Library Agent (Variant 11, Lab 4)."""
from dotenv import load_dotenv

load_dotenv()

LAB_LOGFILE_NAME = "lab4"

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-3k"
MAX_STEPS = 6
TEMPERATURE = 0

SYSTEM = """Ти помічник бібліотеки. Допомагаєш читачам знайти книжку
та дізнатися умови видачі.
Не вигадуй дані – усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2      # скільки помилок моделі поспіль допускаємо

# інструменти, які агентові дозволено викликати (варіант 11)
ALLOWED = ["search_books", "book_info", "calculate"]

# мітка прогону: за нею в Langfuse відрізнятимемо прогони
RUN_TAG = "ctx-control"

NUM_CTX = 3072          # розмір вікна (звужено до 3072, випадок C)
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі (MAX_STEPS не змінюємо)

COMPRESS = "none"       # "none", "trim" або "summary"
COMPRESS_AT = 1100      # скорочуємо, коли prompt_tokens перевищив це число (1206 > 1100)
KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні

USE_STATE = False       # чи додавати в контекст збережені результати
STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини

USE_CACHE = False       # чи кешувати виклики моделі
