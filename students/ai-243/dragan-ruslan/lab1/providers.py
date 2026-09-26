import os
from xmlrpc import client
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv() # зчитує файл .env і робить його значення доступними
PROVIDERS = {
"local": {
"base_url": "http://localhost:11434/v1",
"api_key": "ollama",
"model": "llama3.2:3b",
},
"cloud": {
"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
"api_key": os.getenv("CLOUD_API_KEY"),
"model": "gemini-3.1-flash-lite",
},
}

def make_client(name):
    """Повертає готовий клієнт і назву моделі для обраного провайдера."""

    cfg = PROVIDERS[name]
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
    return client, cfg["model"]