"""Цикл агента з ЛР2 без змін; додано лише трасування Langfuse (крок 2)."""
import logging

from langfuse import observe
from langfuse.openai import OpenAI      # було: from openai import OpenAI

import config
from baseline.schemas import SCHEMAS
from baseline.dispatcher import call_tool

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
logger = logging.getLogger(config.LAB_LOGFILE_NAME)   # налаштовує agent_runner.py

STATS = {"model_calls": 0, "tokens": 0}


@observe()
def run_agent(task):
    """task – питання користувача
    Повертає текст відповіді або None, якщо вичерпано ліміт."""

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]
    STATS["model_calls"] = 0
    STATS["tokens"] = 0

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, config.MAX_STEPS + 1):

        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )
        msg = response.choices[0].message
        STATS["model_calls"] += 1
        STATS["tokens"] += response.usage.total_tokens

        logger.info(f"\n--- крок {step} | prompt_tokens={response.usage.prompt_tokens}")

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        messages.append(msg)

        for call in msg.tool_calls:
            logger.info(f"  виклик   : {call.function.name}({call.function.arguments})")

            result = call_tool(call.function.name, call.function.arguments)

            logger.info(f"  результат: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

    logger.info("СТОП: вичерпано ліміт кроків")
    return None
