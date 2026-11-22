import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
MODEL = "qwen25-3k"

MAX_STEPS = 6
NUM_CTX = 3072
MAX_STEPS_LONG = 25
LAB_LOGFILE_NAME = "lab4"
MAX_RETRIES = 2
TEMPERATURE = 0

ALLOWED = {
    "search_recipes",
    "product_info",
    "scale_amount",
}

RUN_TAG = "ctx-control"

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv(
    "LANGFUSE_HOST",
    "https://cloud.langfuse.com"
)

SYSTEM_PROMPT = """Ти кухонний помічник. Допомагаєш підібрати страву та розрахувати інгредієнти.

Не вигадуй дані. Використовуй інструменти для отримання інформації та обчислень.

Доступні інструменти та їхні точні аргументи:
1. search_recipes — передавай один аргумент query з назвою продукту.
2. product_info — передавай один аргумент product з точною назвою продукту українською.
3. scale_amount — передавай аргументи amount, base_servings і target_servings.
amount — точна калорійність на 100 г із попереднього виклику product_info.
base_servings — 100.
target_servings — маса порції у грамах.

Для product_info використовуй саме ключ product, а не id чи name.
Для search_recipes використовуй саме ключ query.
Не вигадуй додаткових аргументів.

Не пропускай необхідні виклики інструментів.
Коли даних достатньо, дай коротку відповідь українською."""
COMPRESS = "none"
COMPRESS_AT = 2150
KEEP_LAST = 6
USE_STATE = False
STATE_RESULT_CHARS = 200
USE_CACHE = False  # чи кешувати виклики моделі
