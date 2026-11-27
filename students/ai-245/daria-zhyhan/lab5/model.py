"""Виклик моделі. Тут же створюється клієнт, через який агент звертається до сервера."""

from langfuse.openai import OpenAI
import config
from schemas import SCHEMAS
from cache import ask_model

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)


def call_model(messages, step, logger):
    """Один виклик моделі. Повертає пару (відповідь, чи_взято_з_кешу).
    Якщо сервер повернув помилку (наприклад, вхід задовгий), пишемо її в лог
    і повертаємо (None, False): програма не падає, а агент завершує прогін.
    """
    try:
        return ask_model(client, model=config.MODEL, messages=messages,
                         tools=SCHEMAS, temperature=config.TEMPERATURE,
                         parallel_tool_calls=False)
    except Exception as error:            
        logger.error(f"\n--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}")
        return None, False
