
"""Цикл кухонного агента з перевірками та трасуванням."""

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

logger = custom_logger("lab3")


@observe()
def run_agent(task):
    """Виконує завдання та повертає відповідь агента."""

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]

    consecutive_errors = 0

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, config.MAX_STEPS + 1):
        try:
            response = client.chat.completions.create(
                model=config.MODEL,
                messages=messages,
                tools=SCHEMAS,
                temperature=config.TEMPERATURE,
            )
        except Exception as error:
            logger.exception(f"Помилка запиту до моделі: {error}")
            return None

        choice = response.choices[0]
        msg = choice.message

        logger.info(
            f"\n--- крок {step} | "
            f"prompt_tokens={response.usage.prompt_tokens if response.usage else 'невідомо'}"
        )

        response_ok, response_message = check_response(choice)

        if not response_ok:
            logger.warning(f"Некоректна відповідь моделі: {response_message}")
            consecutive_errors += 1

            if consecutive_errors > config.MAX_RETRIES:
                logger.error("СТОП: вичерпано ліміт повторних спроб")
                return None

            messages.append({
                "role": "assistant",
                "content": msg.content or "",
            })
            messages.append({
                "role": "user",
                "content": (
                    "Попередня відповідь була некоректною. "
                    "Надай завершену відповідь або коректний виклик інструмента."
                ),
            })
            continue

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        messages.append(msg)

        for call in msg.tool_calls:
            name = call.function.name
            arguments = call.function.arguments

            logger.info(f"ВИКЛИК: {name}({arguments})")

            level, result = call_tool(name, arguments)

            logger.info(f"РІВЕНЬ: {level}")
            logger.info(f"РЕЗУЛЬТАТ: {result}")

            if level in MODEL_ERRORS:
                consecutive_errors += 1

                if consecutive_errors > config.MAX_RETRIES:
                    logger.error("СТОП: вичерпано ліміт повторних спроб")
                    return None

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": f"Помилка {level}: {result}. Виправ виклик інструмента.",
                })
            else:
                if level == "ok":
                    consecutive_errors = 0

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                })

    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    run_agent("Знайди щось із куркою")

