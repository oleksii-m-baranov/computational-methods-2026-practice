"""Налаштування агента."""

from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen3:4b-instruct-3k"
MAX_STEPS = 6
TEMPERATURE = 0

LAB_LOGFILE_NAME = "lab4"

NUM_CTX = 3072          # розмір вікна, який ви задасте в кроці 1
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі (MAX_STEPS не змінюємо)

SYSTEM = """Ти помічник бібліотеки. Допомагаєш читачам знайти книжку
та дізнатися умови видачі.
Не вигадуй дані – усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2

ALLOWED = ["search_books", "book_info", "calculate"]

RUN_TAG = "ctx-control"

COMPRESS = "none"       # "none" або "trim": скорочувати історію чи ні
COMPRESS_AT = 2150      # скорочуємо, коли prompt_tokens перевищив це число
KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні

USE_STATE = False       # чи додавати в контекст збережені результати
STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини

USE_CACHE = False       # чи кешувати виклики моделі


