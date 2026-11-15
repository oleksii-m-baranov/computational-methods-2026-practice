
"""Цикл агента з перевірками викликів."""

from langfuse import observe
from langfuse.openai import OpenAI

import config
from schemas import SCHEMAS
from dispatcher import call_tool, check_response, MODEL_ERRORS
from utils.lab_logger import custom_logger


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
)

logger = custom_logger(config.LAB_LOGFILE_NAME)


@observe()
def run_agent(task):
    """Виконує питання користувача.
    Повертає відповідь або None, якщо вичерпано ліміт.
    """

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
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

        logger.info(
            f"\n--- крок {step} | помилок поспіль={retries} "
            f"| prompt_tokens={response.usage.prompt_tokens}"
        )

        # Перевірка обриву або зламаного виклику
        problem = check_response(choice)

        if problem is not None:
            level, text = problem

            logger.info(f"  рівень   : {level}")
            logger.info(f"  текст    : {msg.content}")

            retries += 1

            if retries > config.MAX_RETRIES:
                logger.info(
                    "СТОП: модель не змогла сформувати правильний виклик"
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

        # Якщо інструменти не викликалися – повертаємо відповідь
        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        messages.append(msg)

        model_failed = False

        for call in msg.tool_calls:
            logger.info(
                f"  виклик   : "
                f"{call.function.name}({call.function.arguments})"
            )

            level, result = call_tool(
                call.function.name,
                call.function.arguments,
            )

            logger.info(f"  рівень   : {level}")
            logger.info(f"  результат: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

            if level in MODEL_ERRORS:
                model_failed = True

        # Підрахунок помилок моделі поспіль
        if model_failed:
            retries += 1

            if retries > config.MAX_RETRIES:
                logger.info(
                    "СТОП: модель не змогла сформувати правильний виклик"
                )
                return None
        else:
            retries = 0

    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    run_agent("Кіт дряпає меблі, що робити?")
