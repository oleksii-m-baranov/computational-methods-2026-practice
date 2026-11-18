import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # зчитує файл .env і робить його значення доступними

PROVIDERS = {
    "local": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "llama3.2:3b",
    },
    "local_qwen": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "qwen3:4b",
    },
    "cloud": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": os.getenv("CLOUD_API_KEY"),
        "model": "openai/gpt-oss-120b",  # llama-3.3-70b-versatile у Groq більше недоступна
    },
}


def make_client(name):
    """Повертає готовий клієнт і назву моделі для обраного провайдера."""
    cfg = PROVIDERS[name]
    # безкоштовний тариф Groq: 8000 токенів/хв, тож на 429 клієнт чекає й повторює запит
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"], max_retries=8)
    return client, cfg["model"]
