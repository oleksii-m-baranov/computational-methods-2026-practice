from langfuse import observe

import config
from model import call_model
from dispatcher import call_tool, check_response
from compress import compress_history
from state import TaskState
from task_progress import TaskProgress
from utils.lab_logger import custom_logger


MODEL_ERRORS = {"name", "permission", "syntax", "schema", "meaning"}


@observe()
def run_agent(
    task,
    max_steps=None,
    logfile_name=None,
    task_id="task",
    log_overwrite=False,
    task_data=None
):
    max_steps = max_steps or config.MAX_STEPS
    logfile_name = logfile_name or config.LAB_LOGFILE_NAME

    logger = custom_logger(
        logfile_name,
        overwrite=log_overwrite
    )

    state = TaskState(task_id) if config.USE_STATE else None
    progress = TaskProgress(task_data) if task_data else None

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task}
    ]

    retries = 0

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, max_steps + 1):
        response, from_cache = call_model(
            messages,
            step,
            logger
        )

        if response is None or not response.choices:
            logger.error("СТОП: модель не відповідає")
            return None

        msg = response.choices[0].message

        prompt_tokens = (
            response.usage.prompt_tokens
            if response.usage else 0
        )

        completion_tokens = (
            response.usage.completion_tokens
            if response.usage else 0
        )

        logger.info(
            f"--- крок {step}"
            f" | помилок поспіль={retries}"
            f" | prompt_tokens={prompt_tokens}"
            f" | completion_tokens={completion_tokens}"
            + (" | з кешу" if from_cache else "")
        )

        status, explanation = check_response(response)

        if status != "ok":
            retries += 1

            logger.warning(
                f"ПОМИЛКА ВІДПОВІДІ: {status} | {explanation}"
            )

            if retries > config.MAX_RETRIES:
                logger.error("СТОП: перевищено ліміт помилок")
                return None

            messages.append({
                "role": "user",
                "content": explanation or "Повтори відповідь."
            })

            messages = compress_history(
                messages,
                task,
                prompt_tokens,
                state,
                logger
            )

            continue

        messages.append(
            msg.model_dump(exclude_none=True)
        )

        if not msg.tool_calls:
            if msg.content and msg.content.strip():
                if progress is not None and not progress.is_complete():
                    logger.warning(
                        "НЕЗАВЕРШЕНА ЗАДАЧА: "
                        + progress.summary()
                    )

                    messages.append({
                        "role": "user",
                        "content": (
                            "Задача ще не завершена. "
                            "Виконай відсутні виклики інструментів: "
                            + ", ".join(progress.missing())
                        )
                    })

                    messages = compress_history(
                        messages,
                        task,
                        prompt_tokens,
                        state,
                        logger
                    )

                    continue

                logger.info(f"ВІДПОВІДЬ: {msg.content}")
                return msg.content

            retries += 1

            if retries > config.MAX_RETRIES:
                logger.error(
                    "СТОП: немає змістовної відповіді"
                )
                return None

            messages.append({
                "role": "user",
                "content": "Продовж виконання задачі."
            })

            messages = compress_history(
                messages,
                task,
                prompt_tokens,
                state,
                logger
            )

            continue

        logger.info(
            "  МОДЕЛЬ ЗАПРОПОНУВАЛА ВИКЛИКІВ: "
            f"{len(msg.tool_calls)}"
        )

        has_error = False

        for call in msg.tool_calls:
            name = call.function.name
            arguments = call.function.arguments

            logger.info(
                f"  виклик   : {name}({arguments})"
            )

            level, result = call_tool(
                name,
                arguments
            )

            logger.info(f"  рівень   : {level}")
            logger.info(f"  результат: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result)
            })

            if level == "ok":
                if state is not None:
                    state.record(
                        name,
                        arguments,
                        result
                    )

            if progress is not None:
                progress.record(
                    name,
                    arguments,
                    level
                )

            if level in MODEL_ERRORS:
                has_error = True

        if has_error:
            retries += 1

            if retries > config.MAX_RETRIES:
                logger.error(
                    "СТОП: забагато помилок інструментів"
                )

                if progress is not None:
                    logger.info(
                        f"СТАН ЗАДАЧІ: {progress.summary()}"
                    )

                return None
        else:
            retries = 0

        messages = compress_history(
            messages,
            task,
            prompt_tokens,
            state,
            logger
        )

    logger.info("СТОП: вичерпано ліміт кроків")

    if progress is not None:
        logger.info(
            f"СТАН ЗАДАЧІ: {progress.summary()}"
        )

    return None


if __name__ == "__main__":
    result = run_agent(
        "Потрібен ноутбук для навчання"
    )

    print("Відповідь агента:", result)
