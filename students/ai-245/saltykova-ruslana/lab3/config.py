import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
MODEL = "qwen2.5:3b"
MAX_STEPS = 6
TEMPERATURE = 0.0

LAB_LOGFILE_NAME = "lab3.log"
MAX_RETRIES = 2
ALLOWED = ["search_recipes", "product_info", "scale_amount"]
RUN_TAG = "checks"

SYSTEM = """Ти кухонний помічник. Допомагаєш підібрати страву
та розрахувати інгредієнти.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""