
"""Цикл агента з перевірками, стисненням і станом."""

import time
from langfuse import observe

import config
from compress import compress_history
from state import TaskState
from model import call_model
from dispatcher import call_tool, check_response, MODEL_ERRORS
from utils.lab_logger import custom_logger


LAST_RUN = {}




def _finish(status, answer, steps, prompt_tokens, completion_tokens, started):
    """Записує підсумок прогону в LAST_RUN і повертає відповідь."""
    LAST_RUN.clear()
    LAST_RUN.update({
        "status": status,
        "steps": steps,                              # скільки разів модель відповіла
        "prompt_tokens": prompt_tokens,              # сума входів за прогін
        "completion_tokens": completion_tokens,
        "seconds": round(time.time() - started, 1),
    })
    return answer

@observe()
def run_agent(
    task,
    max_steps=None,
    logfile_name=config.LAB_LOGFILE_NAME,
    log_overwrite=False,
    task_id=None
):
    max_steps = max_steps or config.MAX_STEPS

    logger = custom_logger(
        logfile_name,
        overwrite=log_overwrite
    )

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]

    # Окремий стан для кожного запуску.
    state = (
        TaskState(task_id or logfile_name)
        if config.USE_STATE
        else None
    )

    retries = 0

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")
    logger.info(
        f"РЕЖИМ: {config.COMPRESS} "
        f"| USE_STATE={config.USE_STATE} "
        f"| COMPRESS_AT={config.COMPRESS_AT}"
    )

    started = time.time()
    steps = prompt_total = completion_total = 0
    def finish(status, answer=None):
        return _finish(status, answer, steps, prompt_total, completion_total, started)

    for step in range(1, max_steps + 1):

        response, from_cache = call_model(
            messages, step, logger
        )

        if response is None:
            return finish("server_error")

        choice = response.choices[0]
        msg = choice.message

        used = (
            response.usage.prompt_tokens
            if response.usage is not None
            else 0
        )

        completion = (
            response.usage.completion_tokens
            if response.usage is not None
            else 0
        )

        logger.info(
            f"\n--- крок {step} "
            f"| помилок поспіль={retries} "
            f"| prompt_tokens={used} "
            f"| completion_tokens={completion}"
            + (" | з кешу" if from_cache else "")
        )

        steps += 1
        prompt_total += used
        completion_total += completion
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
                return finish("retry_limit")

            if text is not None:
                messages.append({
                    "role": "assistant",
                    "content": msg.content or ""
                })
                messages.append({
                    "role": "user",
                    "content": text
                })

            messages = compress_history(
                messages,
                task,
                used,
                state,
                logger
            )
            continue

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return finish("final", msg.content)

        # Додаємо повідомлення асистента лише один раз.
        messages.append(
            msg.model_dump(exclude_none=True)
        )

        model_failed = False

        for call in msg.tool_calls:
            logger.info(
                f"  виклик   : "
                f"{call.function.name}"
                f"({call.function.arguments})"
            )

            level, result = call_tool(
                call.function.name,
                call.function.arguments
            )

            logger.info(f"  рівень   : {level}")
            logger.info(f"  результат: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

            # У стан записуємо тільки успішні виклики.
            if state is not None and level == "ok":
                state.record(
                    call.function.name,
                    call.function.arguments,
                    result
                )

            if level in MODEL_ERRORS:
                model_failed = True

        if model_failed:
            retries += 1

            if retries > config.MAX_RETRIES:
                logger.info(
                    "СТОП: модель не змогла сформувати "
                    "правильний виклик"
                )
                return finish("retry_limit")
        else:
            retries = 0

        # Стиснення виконується всередині циклу.
        messages = compress_history(
            messages,
            task,
            used,
            state,
            logger
        )

    logger.info("СТОП: вичерпано ліміт кроків")
    return finish("step_limit")


if __name__ == "__main__":
    run_agent("Знайди щось із куркою")
