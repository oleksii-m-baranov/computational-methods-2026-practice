
"""Виклик LLM із підтримкою кешування."""

from langfuse.openai import OpenAI

import config
from cache import ModelCache
from schemas import SCHEMAS


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
)

# Один кеш для всіх викликів моделі в межах процесу.
model_cache = ModelCache()


def call_model(messages):
    """Викликає модель або повертає кешовану відповідь."""

    cache_key = None

    if config.USE_CACHE:
        cache_key = model_cache.make_key(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )

        cached_response = model_cache.get(cache_key)

        if cached_response is not None:
            if config.CACHE_LOGGING:
                print("CACHE HIT: відповідь отримано з кешу")

            return cached_response, True

        if config.CACHE_LOGGING:
            print("CACHE MISS: виклик Ollama")

    try:
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )

        if config.USE_CACHE and cache_key is not None:
            model_cache.set(cache_key, response)

        return response, True

    except Exception as error:
        print(f"Помилка виклику моделі: {error}")
        return None, False


def get_cache_stats():
    """Повертає статистику кешування."""
    return model_cache.stats()


def clear_cache():
    """Очищає кеш."""
    model_cache.clear()
