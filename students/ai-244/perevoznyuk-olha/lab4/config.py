from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MAX_RETRIES = 2 
ALLOWED = ["search_routes", "transport_info", "calc_budget"]
RUN_TAG = "ctx-control"
LAB_LOGFILE_NAME = "lab4"

MODEL = "qwen25-4k"
MAX_STEPS = 6
TEMPERATURE = 0.2

SYSTEM = """Ти помічник турагента. Підбираєш маршрути вихідного дня
та рахуєш бюджет поїздки.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

NUM_CTX = 4096          # розмір вікна, який ви задасте в кроці 1
MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі (MAX_STEPS не змінюємо)

COMPRESS = "none"       # "none" або "trim": скорочувати історію чи ні
COMPRESS_AT = 2800      # скорочуємо, коли prompt_tokens перевищив це число
KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні

USE_STATE = False       # чи додавати в контекст збережені результати
STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини

USE_CACHE = False       # чи кешувати виклики моделі