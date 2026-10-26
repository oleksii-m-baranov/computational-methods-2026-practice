"""Цикл агента з перевірками, повторними спробами та Langfuse."""

from langfuse import observe
from langfuse.openai import OpenAI

import config
from dispatcher import MODEL_ERRORS, call_tool
from schemas import SCHEMAS
from utils.lab_logger import custom_logger


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
)

logger = custom_logger("lab3")


@observe(name="run_agent")
def run_agent(task):
    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]

    retries = 0

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")
    logger.info(f"РЕЖИМ: {config.RUN_TAG}")

    for step in range(1, config.MAX_STEPS + 1):
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )

        msg = response.choices[0].message

        prompt_tokens = (
            response.usage.prompt_tokens
            if response.usage is not None
            else 0
        )

        logger.info(
            f"\n--- крок {step} | prompt_tokens={prompt_tokens}"
        )

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        messages.append(msg)

        model_failed = False

        for call in msg.tool_calls:
            name = call.function.name
            arguments = call.function.arguments

            logger.info(
                f"  виклик: {name}({arguments})"
            )

            level, result = execute_tool(name, arguments)

            logger.info(f"  рівень перевірки: {level}")
            logger.info(f"  результат: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })

            if level in MODEL_ERRORS:
                model_failed = True

        if model_failed:
            retries += 1

            logger.info(
                f"  помилок поспіль: "
                f"{retries}/{config.MAX_RETRIES}"
            )

            if retries > config.MAX_RETRIES:
                logger.info(
                    "СТОП: модель не змогла сформувати "
                    "правильний виклик"
                )
                return None
        else:
            retries = 0

    logger.info("СТОП: вичерпано ліміт кроків")
    return None


@observe(name="tool_execution")
def execute_tool(name, arguments):
    return call_tool(name, arguments)


if __name__ == "__main__":
    from langfuse import get_client, propagate_attributes

    with propagate_attributes(
        trace_name=f"{config.RUN_TAG}-manual",
        tags=[config.RUN_TAG],
    ):
        answer = run_agent(
            "Знайди щось легке з фантастики"
        )

    print("Відповідь агента:", answer)

    get_client().flush()