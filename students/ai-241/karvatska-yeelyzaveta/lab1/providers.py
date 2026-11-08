import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

PROVIDERS = {
    "llama": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "llama3.2:3b",
    },
    "qwen": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "qwen3:4b",
    },
}


def make_client(name):
    cfg = PROVIDERS[name]

    client = OpenAI(
        base_url=cfg["base_url"],
        api_key=cfg["api_key"],
        timeout=180
    )

    return client, cfg["model"]