import os
import json
import logging
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
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key": os.getenv("CLOUD_API_KEY"),
        "model": os.getenv("CLOUD_MODEL", "gemini-3.5-flash-lite"),
        # Gemini 3.5+ не приймає temperature/top_p (застарілі параметри семплювання)
        "sampling": False,
    },
}


def make_client(name):
    """Повертає готовий клієнт і назву моделі для обраного провайдера."""
    cfg = PROVIDERS[name]
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
    return client, cfg["model"]


def sampling_params(name, **params):
    """Повертає temperature/top_p лише для провайдерів, які їх підтримують."""
    return params if PROVIDERS[name].get("sampling", True) else {}


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_logger():
    """Логер: пише і в консоль, і у файл logs/lab1.log."""
    logger = logging.getLogger("lab1")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh = logging.FileHandler(os.path.join(BASE_DIR, "logs", "lab1.log"), encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def save_json(name, data):
    """Зберігає сирі результати в results/<name>.json."""
    os.makedirs(os.path.join(BASE_DIR, "results"), exist_ok=True)
    path = os.path.join(BASE_DIR, "results", name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path
