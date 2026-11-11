from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MAX_RETRIES = 2      # скільки помилок моделі поспіль допускаємо

# інструменти, які агентові дозволено викликати
ALLOWED = ["search_exercises", "schedule_info", "calc_calories"]

# мітка прогону: за нею в Langfuse відрізнятимемо прогони
RUN_TAG = "checks"

LAB_LOGFILE_NAME = "lab3"

MODEL = "qwen3:4b"
# MODEL = "gemma4:26b-a4b-it-qat"
MAX_STEPS = 6
TEMPERATURE = 0

SYSTEM = """Ти помічник тренажерного залу. Підбираєш вправи,
    повідомляєш розклад і рахуєш навантаження.
    Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
    Не рахуй самостійно, для цього є окремий інструмент.
    Якщо потрібного інструмента немає, чесно скажи про це.
    Коли даних достатньо, дай коротку відповідь українською."""
