import config

from langfuse.openai import OpenAI

from schemas import SCHEMAS
from cache import ask_model


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
    timeout=240,
    max_retries=0,
)

def call_model(messages, step, logger, tool_choice=None):
    try:
        request = {
            "model": config.MODEL,
            "messages": messages,
            "tools": SCHEMAS,
            "temperature": config.TEMPERATURE,
        }

        if tool_choice is not None:
            request["tool_choice"] = tool_choice

        return ask_model(client, **request)

    except Exception as error:
        logger.error(f"\n--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}")
        return None, False
    try:
        return ask_model(
            client,
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )

    except Exception as error:
        logger.error(
            f"\n--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}"
        )
        return None, False
