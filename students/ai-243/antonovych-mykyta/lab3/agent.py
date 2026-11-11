"""Цикл агента з перевірками. Лабораторна робота №3."""

import os
import sys

# Підключення utils з кореня репозиторію
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", ".."
        )
    ),
)

from langfuse import observe
from langfuse.openai import OpenAI

import config

from dispatcher import (
    call_tool,
    check_response,
    MODEL_ERRORS,
)

from schemas import SCHEMAS
from utils.lab_logger import custom_logger


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
)

logger = custom_logger(config.LAB_LOGFILE_NAME)


@observe()
def run_agent(task):
    """Запускає агента та обробляє помилки моделі."""

    messages = [
        {
            "role": "system",
            "content": config.SYSTEM,
        },
        {
            "role": "user",
            "content": task,
        },
    ]

    retries = 0

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, config.MAX_STEPS + 1):

        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )

        choice = response.choices[0]
        msg = choice.message

        prompt_tokens = (
            response.usage.prompt_tokens
            if response.usage
            else "N/A"
        )

        logger.info(
            f"\n--- крок {step} | "
            f"помилок поспіль={retries} | "
            f"prompt_tokens={prompt_tokens}"
        )

        # 1. Перевірка відповіді

        problem = check_response(choice)

        if problem is not None:

            level, text = problem

            logger.info(f"  рівень   : {level}")
            logger.info(f"  текст    : {msg.content}")

            retries += 1

            if retries > config.MAX_RETRIES:

                logger.info(
                    "СТОП: модель не змогла "
                    "сформувати правильний виклик"
                )

                return None

            if text is not None:

                messages.append({
                    "role": "assistant",
                    "content": msg.content,
                })

                messages.append({
                    "role": "user",
                    "content": text,
                })

            continue

        # 2. Фінальна текстова відповідь

        if not msg.tool_calls:

            logger.info(
                f"ВІДПОВІДЬ: {msg.content}"
            )

            return msg.content

        # 3. Виклики інструментів

        messages.append(msg)

        model_failed = False

        for call in msg.tool_calls:

            name = call.function.name
            args_raw = call.function.arguments

            logger.info(
                f"  виклик   : {name}({args_raw})"
            )

            level, result = call_tool(
                name,
                args_raw,
            )

            logger.info(
                f"  рівень   : {level}"
            )

            logger.info(
                f"  результат: {result}"
            )

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

            if level in MODEL_ERRORS:
                model_failed = True

        # 4. Обмеження кількості помилок поспіль

        if model_failed:

            retries += 1

            if retries > config.MAX_RETRIES:

                logger.info(
                    "СТОП: модель не змогла "
                    "сформувати правильний виклик"
                )

                return None

        else:

            retries = 0

    logger.info(
        "СТОП: вичерпано ліміт кроків"
    )

    return None


if __name__ == "__main__":

    run_agent(
        "Рецепт плову розрахований на 4 порції "
        "і потребує 300 г рису. "
        "Скільки рису треба на 10 порцій?"
    )
