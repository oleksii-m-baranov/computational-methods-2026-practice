import os
from openai import OpenAI
from dotenv import load_dotenv

# Завантажуємо API-ключ з файлу .env
load_dotenv()

PROVIDERS = {
    "local": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "llama3.2:3b",
    },
    "cloud": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/",
        "api_key": os.getenv("CLOUD_API_KEY"),
        "model": "gemini-3.8-flash",
    },
}

def make_client(name: str):
    """Повертає готовий клієнт і назву моделі для обраного провайдера."""
    cfg = PROVIDERS[name]
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
    return client, cfg["model"]