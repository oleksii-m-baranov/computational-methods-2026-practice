"""Виклик мовної моделі з підтримкою кешування."""

from langfuse.openai import OpenAI

import config
from schemas import SCHEMAS
from cache import ask_model


# Клієнт для звернення до локальної моделі через Ollama
client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
)


def call_model(messages, step, logger):
    """Викликає модель або отримує відповідь із кешу.

    Повертає пару:
    (відповідь моделі, чи використано кеш).
    """
    try:
        request = {
            "model": config.MODEL,
            "messages": messages,
            "tools": SCHEMAS,
            "temperature": config.TEMPERATURE,
        }

        # Діагностичний режим: максимум один виклик
        # інструмента за одну відповідь моделі.
        # У звичайних прогонах цей параметр не додається.
        if getattr(config, "SINGLE_TOOL_CALL", False):
            request["parallel_tool_calls"] = False

        response, from_cache = ask_model(
            client,
            **request,
        )

        return response, from_cache

    except Exception as error:
        logger.error(
            f"\n--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}"
        )
        return None, False