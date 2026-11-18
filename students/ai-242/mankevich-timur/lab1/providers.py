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
    "cloud": {
        # Google AI Studio (OpenAI-сумісний endpoint). Якщо береш Groq:
        # "https://api.groq.com/openai/v1"
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key": os.getenv("CLOUD_API_KEY"),
        # Назву моделі бери дослівно з документації провайдера
        "model": "gemini-2.5-flash",
    },
}


def make_client(name, model=None):
    """Повертає готовий клієнт і назву моделі для обраного провайдера.
    Необов'язковий model дозволяє взяти іншу модель того ж провайдера
    (наприклад, qwen3:4b замість llama3.2:3b на локальному Ollama)."""
    cfg = PROVIDERS[name]
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
    return client, (model or cfg["model"])
