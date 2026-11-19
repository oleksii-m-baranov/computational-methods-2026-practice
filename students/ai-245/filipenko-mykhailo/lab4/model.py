import time

from langfuse.openai import OpenAI

import config
from schemas import SCHEMAS
from cache import ask_model


# Одна додаткова спроба після помилки сервера.
MAX_SERVER_RETRIES = 1

# Затримка перед повторною спробою.
RETRY_DELAY = 1

# Максимальне очікування однієї відповіді Ollama.
REQUEST_TIMEOUT = 60.0


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
    timeout=REQUEST_TIMEOUT,
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

    for attempt in range(MAX_SERVER_RETRIES + 1):
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
                f"--- крок {step} | "
                f"ПОМИЛКА СЕРВЕРА "
                f"(спроба {attempt + 1}/"
                f"{MAX_SERVER_RETRIES + 1}): "
                f"{type(error).__name__}: {error}"
            )

            if attempt < MAX_SERVER_RETRIES:
                logger.warning(
                    f"  ПОВТОРНА СПРОБА через "
                    f"{RETRY_DELAY} с"
                )

                time.sleep(RETRY_DELAY)
            else:
                logger.error(
                    "СТОП: сервер не відповів "
                    "після повторних спроб"
                )

                return None, False

    return None, False
