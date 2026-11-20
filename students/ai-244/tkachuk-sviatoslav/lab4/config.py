"""Налаштування агента й обмеження контексту."""
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

LAB_LOGFILE_NAME = "lab4"
BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
MODEL = "qwen25-4k"
MAX_STEPS = 6
MAX_STEPS_LONG = 25
TEMPERATURE = 0.2
NUM_CTX = 4096

SYSTEM = """Ти консультант ветеринарної клініки з догляду за котами.
Для кожного кота з довгої задачі окремо використай search_articles, vaccine_info і calc_food.
Виконуй інструменти для кожної позиції, навіть якщо знаєш відповідь із попереднього досвіду.
Не вигадуй вік щеплень, назви статей або значення розрахунків.
Для розрахунку корму використовуй навчальну норму 25 г/кг/добу, 30 днів.
Наприкінці наведи результат для кожного кота і суму корму всіх шести котів у грамах.
Довідкові норми лише навчальні, не ветеринарні рекомендації.
Якщо потрібного інструмента немає, чесно скажи про це. Відповідай українською."""

MAX_RETRIES = 2
ALLOWED = ["search_articles", "vaccine_info", "calc_food"]
RUN_TAG = "ctx-control"

COMPRESS = "none"
COMPRESS_AT = 2800
KEEP_LAST = 6
USE_STATE = False
STATE_RESULT_CHARS = 200
USE_CACHE = False
