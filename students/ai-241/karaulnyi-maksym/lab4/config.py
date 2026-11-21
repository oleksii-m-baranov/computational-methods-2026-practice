import os
from dotenv import load_dotenv

load_dotenv()

LAB_LOGFILE_NAME = "lab4"

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

# Модель зі звуженим контекстом (крок 1)
MODEL = "qwen25-3k"

# Параметри генерації
TEMPERATURE = 0
MAX_STEPS = 6
MAX_STEPS_LONG = 25
MAX_RETRIES = 2

# Початковий системний промпт (як у ЛР3)
SYSTEM = """Ти помічник бібліотеки. Допомагаєш читачам знайти книжку та дізнатися умови видачі.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

# Дозволені інструменти (Варіант 1 — Бібліотека)
ALLOWED = ["search_books", "book_info", "calculate"]

# Мітка прогонів у Langfuse
RUN_TAG = "ctx-control"

# Розмір контекстного вікна моделі (токенів)
NUM_CTX = 3072

# Поріг спрацювання скорочення історії (70% від NUM_CTX)
COMPRESS_AT = 2150

# Скільки останніх повідомлень зберігати при trim
KEEP_LAST = 6

# Обмеження довжини результату інструмента в TaskState
STATE_RESULT_CHARS = 200

# Режим скорочення історії за замовчуванням
COMPRESS = "none"

# Використання стану TaskState та кешу
USE_STATE = False
USE_CACHE = False
