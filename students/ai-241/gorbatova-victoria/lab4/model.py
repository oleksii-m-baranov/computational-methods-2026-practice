"""Виклик моделі з підтримкою кешування."""
from langfuse.openai import OpenAI

import config
from schemas import SCHEMAS
from cache import ask_model

# Клієнт: адреса сервера й ключ беруться з config.py.
client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)


def call_model(messages, step, logger):
    """Один виклик моделі. Повертає пару (відповідь, чи_взято_з_кешу)."""
    try:
        response, from_cache = ask_model(
            client,
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )
        return response, from_cache
    except Exception as error:
        logger.error(f"\n--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}")
        return None, False