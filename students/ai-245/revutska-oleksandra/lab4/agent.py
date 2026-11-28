
"""Бібліотечний агент: контекст, стан, кеш і Langfuse."""

import logging
from pathlib import Path

from langfuse import observe

import config
from compress import compress_history
from dispatcher import MODEL_ERRORS, call_tool
from model import call_model
from state import TaskState


def create_logger(logfile_name=None, overwrite=False):
    """Створює окремий лог для кожного прогону."""

    logfile_name = logfile_name or config.LAB_LOGFILE_NAME

    Path("logs").mkdir(exist_ok=True)

    logger = logging.getLogger("lab4_agent")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    handler = logging.FileHandler(
        Path("logs") / f"{logfile_name}.log",
        mode="w" if overwrite else "a",
        encoding="utf-8",
    )

    handler.setFormatter(
        logging.Formatter("%(message)s")
    )

    logger.addHandler(handler)

    return logger


@observe(name="run_agent")
def run_agent(
    task,
    max_steps=None,
    logfile_name=None,
    task_id="task",
    log_overwrite=False,
):
    """Виконує бібліотечне завдання."""

    if max_steps is None:
        max_steps = config.MAX_STEPS

    logger = create_logger(
        logfile_name,
        overwrite=log_overwrite,
    )

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]

    state = TaskState(task_id)
    retries = 0

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")
    logger.info(f"РЕЖИМ: {config.RUN_TAG}")
    logger.info(f"СТИСНЕННЯ: {config.COMPRESS}")
    logger.info(f"ЗБЕРЕЖЕННЯ СТАНУ: {config.USE_STATE}")
    logger.info(f"КЕШ: {config.USE_CACHE}")

    for step in range(1, max_steps + 1):

        try:
            response, from_cache = call_model(messages)

        except Exception as error:
            logger.error(
                f"--- крок {step} | "
                f"ПОМИЛКА СЕРВЕРА: {error}"
            )
            return None

        if response is None:
            logger.error(
                f"--- крок {step} | ПОМИЛКА СЕРВЕРА"
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

        logger.info(
            f"--- крок {step} | "
            f"помилок поспіль={retries} | "
            f"prompt_tokens={prompt_tokens} | "
            f"completion_tokens={completion_tokens}"
            + (" | з кешу" if from_cache else "")
        )

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        messages.append(
            msg.model_dump(exclude_none=True)
        )

        model_failed = False

        for call in msg.tool_calls:

            name = call.function.name
            arguments = call.function.arguments

            logger.info(
                f"  виклик   : {name}({arguments})"
            )

            level, result = call_tool(
                name,
                arguments,
            )

            result_text = str(result)

            logger.info(
                f"  рівень   : {level}"
            )

            logger.info(
                f"  результат: {result_text}"
            )

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result_text,
            })

            if level == "ok":
                state.record(
                    name,
                    arguments,
                    result_text,
                )

            if level in MODEL_ERRORS:
                model_failed = True

        if model_failed:
            retries += 1

            if retries > config.MAX_RETRIES:
                logger.info(
                    "СТОП: модель не змогла "
                    "виправити помилки"
                )
                return None

        else:
            retries = 0

        messages = compress_history(
            messages,
            task,
            prompt_tokens,
            state,
            logger,
        )

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
