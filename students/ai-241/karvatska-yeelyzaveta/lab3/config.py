import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
MODEL = "qwen2.5:3b"

MAX_STEPS = 6
MAX_RETRIES = 2
TEMPERATURE = 0

ALLOWED = {
    "search_recipes",
    "product_info",
    "scale_amount",
}

RUN_TAG = "checks"

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv(
    "LANGFUSE_HOST",
    "https://cloud.langfuse.com"
)

SYSTEM_PROMPT = """Ти кухонний помічник. Допомагаєш підібрати страву та розрахувати інгредієнти.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Доступні лише інструменти пошуку рецептів, довідника продуктів
і масштабування кількості інгредієнтів.
Ти не можеш створювати або змінювати списки покупок.
Якщо користувач просить дію, для якої немає інструмента,
чітко повідом, що виконати її неможливо.
Не підмінюй запит іншою дією.
Коли даних достатньо, дай коротку відповідь українською."""
