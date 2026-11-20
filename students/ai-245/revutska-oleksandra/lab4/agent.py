"""Бібліотечний агент: контекст, стан, кеш і Langfuse."""

import logging
from pathlib import Path

from langfuse import observe

import config
from compress import compress_messages
from dispatcher import MODEL_ERRORS, call_tool
from model import call_model
from state import AgentState


def create_logger():
    """Створює лог у папці logs для measure.py."""

    Path("logs").mkdir(exist_ok=True)

    logger = logging.getLogger("lab4_agent")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Не додаємо однакові обробники повторно.
    if not logger.handlers:
        handler = logging.FileHandler(
            Path("logs") / f"{config.LAB_LOGFILE_NAME}.log",
            mode="a",
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
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
    """Виконує завдання через Ollama та інструменти."""

    if max_steps is None:
        max_steps = config.MAX_STEPS

    logger = create_logger()

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
    logger.info(f"КЕШ: {config.USE_CACHE}")

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

        request_messages = list(messages)

        if state is not None and state.tool_results:
            summary = state.get_summary()

            request_messages.insert(
                1,
                {
                    "role": "system",
                    "content": (
                        "Збережені результати інструментів:\n\n"
                        + summary
                    ),
                },
            )

            logger.info(
                f"STATE: збережено викликів "
                f"{state.get_tool_count()}"
            )

        response, from_cache = call_model(request_messages)

        if response is None:
            logger.error(
                f"ПОМИЛКА СЕРВЕРА на кроці {step}"
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
            f"--- крок {step} | "
            f"prompt_tokens={prompt_tokens} | "
            f"completion_tokens={completion_tokens}"
            + (" | CACHE HIT" if from_cache else "")
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
                f"  виклик: {name}({arguments})"
            )

            level, result = call_tool(
                name,
                arguments,
            )

            result_text = str(result)

            logger.info(
                f"  рівень перевірки: {level}"
            )
            logger.info(
                f"  результат: {result_text}"
            )

            if state is not None and level == "ok":
                state.add_tool_result(
                    name,
                    arguments,
                    result_text,
                )

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

            if retries > config.MAX_RETRIES:
                logger.info(
                    "СТОП: перевищено кількість помилок"
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