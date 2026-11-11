

"""Бібліотечний агент із контекстом, станом і Langfuse."""

from langfuse import observe

import config
from compress import compress_messages
from dispatcher import MODEL_ERRORS, call_tool
from model import call_model
from state import AgentState
from utils.lab_logger import custom_logger


@observe(name="run_agent")
def run_agent(task, max_steps=None):
    """Виконує задачу користувача зі збереженням стану."""

    logger = custom_logger(config.LAB_LOGFILE_NAME)

    if max_steps is None:
        max_steps = config.MAX_STEPS

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]

    state = AgentState() if config.USE_STATE else None

    retries = 0
    last_prompt_tokens = 0

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")
    logger.info(f"РЕЖИМ: {config.RUN_TAG}")
    logger.info(f"СТИСНЕННЯ: {config.COMPRESS}")
    logger.info(f"ЗБЕРЕЖЕННЯ СТАНУ: {config.USE_STATE}")

    for step in range(1, max_steps + 1):

        old_count = len(messages)

        messages = compress_messages(
            messages,
            last_prompt_tokens,
        )

        if len(messages) < old_count:
            logger.info(
                f"TRIM: повідомлень {old_count} -> {len(messages)}"
            )

        # Після стиснення повертаємо важливі дані
        # зі стану агента до контексту моделі.
        request_messages = list(messages)

        if state is not None and state.tool_results:
            summary = state.get_summary()

            request_messages.insert(
                1,
                {
                    "role": "system",
                    "content": (
                        "Нижче наведено збережені результати "
                        "викликів інструментів. "
                        "Використовуй їх як фактичні дані, "
                        "але продовжуй виконувати задачу.\n\n"
                        + summary
                    ),
                },
            )

            logger.info(
                f"STATE: збережено викликів "
                f"{state.get_tool_count()}"
            )

        response, success = call_model(request_messages)

        if not success or response is None:
            logger.error(
                f"Помилка виклику моделі на кроці {step}"
            )
            return None

        msg = response.choices[0].message

        prompt_tokens = (
            response.usage.prompt_tokens
            if response.usage is not None
            else 0
        )

        completion_tokens = (
            response.usage.completion_tokens
            if response.usage is not None
            else 0
        )

        last_prompt_tokens = prompt_tokens

        logger.info(
            f"\n--- крок {step} | "
            f"prompt_tokens={prompt_tokens} | "
            f"completion_tokens={completion_tokens}"
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

            result_text = str(result)

            if state is not None and level == "ok":
                state.add_tool_result(
                    name,
                    arguments,
                    result_text,
                )

            # Обмежуємо довжину результату,
            # якщо ввімкнено збереження стану.
            if state is not None:
                result_text = result_text[
                    :config.STATE_RESULT_CHARS
                ]

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result_text,
                }
            )

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
                    "СТОП: перевищено кількість помилок"
                )
                return None
        else:
            retries = 0

    logger.info("СТОП: вичерпано ліміт кроків")
    return None


@observe(name="tool_execution")
def execute_tool(name, arguments):
    """Виконує інструмент через диспетчер перевірок."""
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
