"""Виклик моделі. Тут же створюється клієнт, через який агент звертається до сервера."""
from langfuse.openai import OpenAI

import config
from schemas import SCHEMAS
from cache import ask_model

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
        # Виконуємо по одному виклику інструмента за крок, щоб модель бачила результат перед наступним кроком
        msg = response.choices[0].message
        if msg.tool_calls and len(msg.tool_calls) > 1:
            msg.tool_calls = msg.tool_calls[:1]
        return response, from_cache
    except Exception as error:
        logger.error(f"\n--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}")
        return None, False
