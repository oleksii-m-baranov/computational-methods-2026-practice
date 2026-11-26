"""Налаштування агента."""
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-3k"
MAX_STEPS = 6
TEMPERATURE = 0.2

MAX_RETRIES = 2
ALLOWED = ["search_plants", "fertilizer_info", "calc_dose"]
RUN_TAG = "ctx-control"
LAB_LOGFILE_NAME = "lab4"

NUM_CTX = 3072
MAX_STEPS_LONG = 25

COMPRESS = "none"         # "none", "trim" або "summary"
COMPRESS_AT = 1700        # скорочуємо, коли prompt_tokens перевищив це число
KEEP_LAST = 6             # скільки останніх повідомлень лишати при обрізанні

USE_STATE = False         # чи додавати в контекст збережені результати
STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини

USE_CACHE = False         # чи кешувати виклики моделі

SYSTEM = """Ти консультант з догляду за кімнатними рослинами.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
У search_plants передавай лише назву рослини (наприклад, 'Фікус Бенджаміна'), без слів 'полив' чи 'догляд'.
Не рахуй самостійно, для цього є окремий інструмент calc_dose (передавай у нього точну дозу на літр з довідника).
Коли опрацюєш усі шість рослин, дай коротку відповідь українською і в кінці вкажи сумарну дозу в мілілітрах одним числом."""
