"""Виклик моделі. Тут же створюється клієнт, через який агент звертається до сервера."""
from langfuse.openai import OpenAI

import config
from schemas import SCHEMAS
from cache import ask_model

# Клієнт: адреса сервера й ключ беруться з config.py.
# Версія OpenAI з langfuse автоматично записує кожен виклик у трасу.
client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY, timeout=60, max_retries=0)


def call_model(messages, step, logger):
    """Один виклик моделі. Повертає пару (відповідь, чи_взято_з_кешу).

    Якщо сервер повернув помилку (наприклад, вхід задовгий), пишемо її в лог
    і повертаємо (None, False): програма не падає, а агент завершує прогін.
    """
    try:
        options = {}
        if config.MAX_OUTPUT_TOKENS is not None:
            options["max_tokens"] = config.MAX_OUTPUT_TOKENS
        return ask_model(client, model=config.MODEL, messages=messages,
                         tools=SCHEMAS, temperature=config.TEMPERATURE, **options)
    except Exception as error:                  # будь-яка помилка під час виклику
        logger.error(f"\n--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}")
        return None, False
