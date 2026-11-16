
"""Єдиний інтерфейс для локальної Ollama та Google Gemini."""
import getpass
import os

PROVIDERS = {
    "local": {
        "base_url": "http://localhost:11434/v1",
        "model": "llama3.2:3b",
        "api_key": "ollama",
    },
    "cloud": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-3.5-flash-lite",
    },
}


def make_client(provider):
    if provider not in PROVIDERS:
        raise ValueError(f"Невідомий провайдер: {provider}")

    cfg = PROVIDERS[provider]

    if provider == "local":
        key = cfg["api_key"]
    else:
        key = os.getenv("CLOUD_API_KEY", "").strip()

        if not key:
            key = getpass.getpass(
                "Google API key (ввід прихований): "
            ).strip()

        if not key:
            raise RuntimeError(
                "Для Gemini потрібен чинний Google API-ключ"
            )

    from openai import OpenAI

    client = OpenAI(
        base_url=cfg["base_url"],
        api_key=key,
        timeout=120.0,
        max_retries=0,
    )

    return client, cfg["model"]
