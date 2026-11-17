from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MAX_RETRIES = 2 
ALLOWED = ["search_routes", "transport_info", "calc_budget"]
RUN_TAG = "checks"
LAB_LOGFILE_NAME = "lab3"

MODEL = "qwen2.5:3b"
MAX_STEPS = 6
TEMPERATURE = 0.2

SYSTEM = """Ти помічник турагента. Підбираєш маршрути вихідного дня
та рахуєш бюджет поїздки.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""