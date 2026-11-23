
"""Виклик мовної моделі через Ollama з кешуванням."""

from langfuse.openai import OpenAI
from openai.types.chat import ChatCompletion

import config
from schemas import SCHEMAS
from cache import make_key, get_cached, save_cached


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY
)


def call_model(messages, step, logger):
    """
    Виконує один виклик моделі.

    Повертає:
        response - відповідь моделі
        from_cache - чи взято відповідь із кешу
    """

    try:
        key = None

        if config.USE_CACHE:
            key = make_key(
                config.MODEL,
                messages,
                SCHEMAS,
                config.TEMPERATURE
            )

            cached = get_cached(key)

            if cached is not None:
                response = ChatCompletion.model_validate(cached)

                logger.info(
                    f"  CACHE HIT | крок {step} | "
                    f"ключ={key[:12]}"
                )

                return response, True

            logger.info(
                f"  CACHE MISS | крок {step} | "
                f"ключ={key[:12]}"
            )

        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )

        if config.USE_CACHE and key is not None:
            save_cached(key, response)

            logger.info(
                f"  CACHE SAVE | крок {step} | "
                f"ключ={key[:12]}"
            )

        return response, False

    except Exception as error:
        logger.error(
            f"\n--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}"
        )
        return None, False

