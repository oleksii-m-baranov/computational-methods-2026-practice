
from langfuse.openai import OpenAI

import config
from schemas import SCHEMAS
from cache import ask_model


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
    timeout=120.0,
    max_retries=0
)


def call_model(messages, step, logger):
    request = {
        "model": config.MODEL,
        "messages": messages,
        "tools": SCHEMAS,
        "parallel_tool_calls": False,
        "temperature": config.TEMPERATURE,
        "extra_body": {
            "options": {
                "num_ctx": config.NUM_CTX
            }
        }
    }

    try:
        if config.USE_CACHE:
            response, from_cache = ask_model(
                client,
                **request
            )
        else:
            response = client.chat.completions.create(
                **request
            )
            from_cache = False

        logger.info(
            f"  КЕШ: {'HIT' if from_cache else 'MISS'}"
        )

        return response, from_cache

    except Exception as error:
        logger.error(
            f"--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}"
        )
        return None, False
