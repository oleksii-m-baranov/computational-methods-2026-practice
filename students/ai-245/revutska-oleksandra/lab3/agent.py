
"""Цикл агента з перевірками, повторними спробами та Langfuse."""

from langfuse import observe
from langfuse.openai import OpenAI

import config
from dispatcher import call_tool, check_response, MODEL_ERRORS
from schemas import SCHEMAS
from utils.lab_logger import custom_logger


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
)

logger = custom_logger(config.LAB_LOGFILE_NAME)


@observe(name="run_agent")
def run_agent(task):
    """Виконує задачу користувача з перевірками викликів."""

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

        choice = response.choices[0]
        msg = choice.message

        prompt_tokens = (
            response.usage.prompt_tokens
            if response.usage is not None
            else 0
        )

        logger.info(
            f"\n--- крок {step} "
            f"| помилок поспіль={retries} "
            f"| prompt_tokens={prompt_tokens}"
        )

        # 1. Перевірка відповіді моделі
        problem = check_response(choice)

        if problem is not None:
            level, text = problem

            logger.info(f"  рівень   : {level}")
            logger.info(f"  текст    : {msg.content}")

            retries += 1

            if retries > config.MAX_RETRIES:
                logger.info(
                    "СТОП: модель не змогла сформувати "
                    "правильний виклик"
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

        # 2. Якщо модель дала звичайну відповідь
        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        # 3. Додаємо виклики моделі в історію
        messages.append(msg)

        model_failed = False

        # 4. Перевірка та виконання інструментів
        for call in msg.tool_calls:

            name = call.function.name
            arguments = call.function.arguments

            logger.info(
                f"  виклик   : {name}({arguments})"
            )

            level, result = call_tool(name, arguments)

            logger.info(f"  рівень   : {level}")
            logger.info(f"  результат: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })

            if level in MODEL_ERRORS:
                model_failed = True

        # 5. Контроль кількості помилок моделі
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
