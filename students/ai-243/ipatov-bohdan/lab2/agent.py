"""Agent loop for library assistant. Variant 11 (Library)."""
from openai import OpenAI

import config
from schemas import SCHEMAS
from dispatcher import call_tool
from lab_logger import custom_logger

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
logger = custom_logger('lab2')


def run_agent(task: str):
    """Execute the agent loop for a user task.
    Returns the final answer string or None if step limit exceeded."""
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


if __name__ == "__main__":
    run_agent("Знайди щось легке з фантастики")
