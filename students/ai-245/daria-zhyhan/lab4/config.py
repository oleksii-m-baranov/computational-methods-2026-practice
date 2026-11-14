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

COMPRESS = "none"
COMPRESS_AT = 2150
KEEP_LAST = 6
USE_STATE = False
STATE_RESULT_CHARS = 200

SYSTEM = """Ти консультант з догляду за кімнатними рослинами.
Не пиши проміжних відповідей! Кожен хід викликай рівно один інструмент (search_plants, fertilizer_info або calc_dose), доки не виконаєш усі 18 викликів для всіх 6 рослин (Фікус, Заміокулькас, Спатифілум, Драцена, Алое вера, Калатея).
Лише після всіх 18 викликів порахуй сумарну дозу в мілілітрах і дай відповідь українською."""
USE_CACHE = False       # чи кешувати виклики моделі
