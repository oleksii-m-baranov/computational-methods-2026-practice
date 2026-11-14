"""Виклик моделі."""
from langfuse.openai import OpenAI

import config
from schemas import SCHEMAS
from cache import ask_model

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)


def call_model(messages, step, logger):
    try:
        return ask_model(
            client,
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )
    except Exception as error:
        logger.error(f"\n--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}")
        return None, False