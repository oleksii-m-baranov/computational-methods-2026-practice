import os

# Налаштування локальної моделі Ollama
BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
MODEL = "qwen2.5:3b"

MAX_STEPS = 8
TEMPERATURE = 0

# Оригінальний системний промпт із ЛР2
SYSTEM = """Ти консультант магазину техніки. Підбираєш ноутбук
і рахуєш умови покупки.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

# Додаткові налаштування ЛР3
MAX_RETRIES = 3

ALLOWED = [
    "search_laptops",
    "laptop_info",
    "calc_installment"
]

# Режим експерименту: baseline або checks
RUN_TAG = os.getenv("RUN_TAG", "checks").strip().lower()

if RUN_TAG not in ("baseline", "checks"):
    raise ValueError(
        "Некоректний RUN_TAG. Використовуй baseline або checks."
    )

# Окремий лог для кожного режиму
LAB_LOGFILE_NAME = f"lab3_{RUN_TAG}"
