"""Налаштування провайдерів: усі відмінності між ними зібрані в одному словнику."""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()   # зчитує файл .env і робить його значення доступними

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
    # Хмарна модель: Groq (безкоштовний тариф). llama-3.3-70b-versatile вже вимкнено
    # (shutdown 16.08.2026), рекомендована заміна — openai/gpt-oss-120b.
    # Актуальні назви: https://console.groq.com/docs/models
    "cloud": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": os.getenv("CLOUD_API_KEY"),
        "model": "openai/gpt-oss-120b",
    },
}


def make_client(name):
    """Повертає готовий клієнт і назву моделі для обраного провайдера."""
    cfg = PROVIDERS[name]
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
    return client, cfg["model"]
