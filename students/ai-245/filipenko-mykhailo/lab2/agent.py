
"""AI-агент для вибору ноутбука. Варіант 9."""

from openai import OpenAI

import config
from schemas import SCHEMAS
from dispatcher import call_tool
from utils.lab_logger import custom_logger


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY
)

logger = custom_logger("lab2")


def run_agent(task):
    """Запускає агента та повертає його відповідь."""

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task}
    ]

    logger.info("\n" + "=" * 60)
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, config.MAX_STEPS + 1):

        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE
        )

        msg = response.choices[0].message

        tokens = response.usage.prompt_tokens if response.usage else "невідомо"

        logger.info(f"\n--- крок {step} | prompt_tokens={tokens}")

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        messages.append(msg)

        for call in msg.tool_calls:
            name = call.function.name
            arguments = call.function.arguments

            logger.info(f"  виклик   : {name}({arguments})")

            result = call_tool(name, arguments)

            logger.info(f"  результат: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result
            })

    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    run_agent("Потрібен ноутбук для навчання")
