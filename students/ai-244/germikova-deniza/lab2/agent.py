"""Цикл кухонного агента."""
from openai import OpenAI
import config
from schemas import SCHEMAS
from dispatcher import call_tool
from utils.lab_logger import custom_logger

client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
)
logger = custom_logger("lab2")


def run_agent(task):
    """Виконує завдання та повертає відповідь агента."""

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]

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

        logger.info(
            f"\n--- крок {step} | "
            f"prompt_tokens={response.usage.prompt_tokens}"
        )

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        # Зберігаємо повідомлення асистента з усіма викликами.
        messages.append(msg)

        # Виконуємо кожен виклик і додаємо кожен результат.
        for call in msg.tool_calls:
            logger.info(
                f"ВИКЛИК: {call.function.name}"
                f"({call.function.arguments})"
            )

            result = call_tool(
                call.function.name,
                call.function.arguments,
            )

            logger.info(f"РЕЗУЛЬТАТ: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })

    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    run_agent("Знайди щось із куркою")