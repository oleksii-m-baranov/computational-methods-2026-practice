
"""Виклик мовної моделі через Ollama."""

import os
import config
from schemas import SCHEMAS
from cache import ask_model

# Langfuse використовуємо, коли налаштовані ключі.
# Інакше працюємо напряму через OpenAI-сумісний API Ollama.
if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
    from langfuse.openai import OpenAI
else:
    from openai import OpenAI

client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
    timeout=90.0,
    max_retries=0,
)


def call_model(messages, step, logger):
    try:
        return ask_model(
            client,
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
            max_tokens=512,
        )
    except Exception as error:
        logger.error(
            f"\n--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}"
        )
        return None, False
