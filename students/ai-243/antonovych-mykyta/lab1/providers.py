import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


LAB_DIR = Path(__file__).resolve().parent
load_dotenv(LAB_DIR / ".env")


PROVIDERS = {
    "local": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "llama3.2:3b",
    },

    "local_llama": {
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
        "base_url": os.getenv("CLOUD_BASE_URL"),
        "api_key": os.getenv("CLOUD_API_KEY"),
        "model": os.getenv("CLOUD_MODEL"),
    },
}


def make_client(name):
    cfg = PROVIDERS[name]

    if not cfg["base_url"]:
        raise RuntimeError(
            f"Не задано base_url для провайдера {name}"
        )

    if not cfg["api_key"]:
        raise RuntimeError(
            f"Не задано api_key для провайдера {name}"
        )

    if not cfg["model"]:
        raise RuntimeError(
            f"Не задано model для провайдера {name}"
        )

    client = OpenAI(
        base_url=cfg["base_url"],
        api_key=cfg["api_key"],
    )

    return client, cfg["model"]
