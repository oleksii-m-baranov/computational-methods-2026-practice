"""Один клієнт OpenAI для локальних моделей Ollama та хмари Groq."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
PROVIDERS = {
    "local": {
        "base_url": OLLAMA_URL + "/v1",
        "api_key": "ollama",
        "model": os.getenv("LOCAL_MODEL", "llama3.2:3b"),
    },
    "local_llama": {
        "base_url": OLLAMA_URL + "/v1",
        "api_key": "ollama",
        "model": os.getenv("LLAMA_MODEL", "llama3.2:3b"),
    },
    "local_qwen": {
        "base_url": OLLAMA_URL + "/v1",
        "api_key": "ollama",
        "model": os.getenv("QWEN_MODEL", "qwen3:4b"),
    },
    "cloud": {
        "base_url": os.getenv("CLOUD_BASE_URL", "https://api.groq.com/openai/v1"),
        "api_key": os.getenv("CLOUD_API_KEY") or os.getenv("GROQ_API_KEY"),
        "model": os.getenv("CLOUD_MODEL", "openai/gpt-oss-120b"),
    },
}


def make_client(name):
    """Повертає (OpenAI, model). Секрети не потрапляють у звіт чи журнали."""
    if name not in PROVIDERS:
        raise ValueError(f"Невідомий провайдер: {name}")
    cfg = PROVIDERS[name]
    if not cfg["api_key"]:
        raise RuntimeError("Не задано CLOUD_API_KEY у файлі .env або середовищі.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Встановіть залежності: python -m pip install -r requirements.txt") from exc
    return OpenAI(
        base_url=cfg["base_url"], api_key=cfg["api_key"],
        timeout=float(os.getenv("API_TIMEOUT_S", "600")), max_retries=0,
    ), cfg["model"]


def public_config():
    """Лише несекретна конфігурація для відтворення експериментів."""
    return {
        name: {"model": cfg["model"], "base_url": cfg["base_url"].split("?")[0]}
        for name, cfg in PROVIDERS.items()
    }

