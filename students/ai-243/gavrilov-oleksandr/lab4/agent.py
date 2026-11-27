"""Агент з перевіркою викликів інструментів перед виконанням."""
import json
from langfuse import observe

import config
from compress import compress_history
from dispatcher import call_tool
from model import call_model
from state import TaskState
from utils.lab_logger import custom_logger


@observe()
def run_agent(
    task,
    max_steps=None,
    logfile_name=config.LAB_LOGFILE_NAME,
    task_id="task",
    log_overwrite=False,
    min_tool_calls=None,
):
    """task – питання користувача
    Повертає текст відповіді або None, якщо вичерпано ліміт."""
    max_steps = max_steps or config.MAX_STEPS
    logger = custom_logger(logfile_name, overwrite=log_overwrite)
    state = TaskState(task_id)

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")
    logger.info(f"МОДЕЛЬ: {config.MODEL} | КРОКІВ: {max_steps} | RETRIES: {config.MAX_RETRIES}")

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]

    retries = 0
    tool_calls_executed = 0
    pending_calls = []

    for step in range(1, max_steps + 1):
        response, from_cache = call_model(messages, step, logger)
        if response is None:
            return None

        choice = response.choices[0]
        msg = choice.message
        used = response.usage.prompt_tokens
        all_calls = msg.tool_calls or []
        used_queued_call = bool(pending_calls)
        # Ollama may batch tool calls; execute that plan one call per agent step.
        if used_queued_call:
            call = pending_calls.pop(0)
            calls = [call]
            model_message = {
                "role": "assistant",
                "tool_calls": [call.model_dump(exclude_none=True)],
            }
        else:
            calls = all_calls[:1]
            if len(all_calls) > 1:
                pending_calls.extend(all_calls[1:])
            model_message = msg.model_dump(exclude_none=True)
            if len(all_calls) > 1:
                model_message["tool_calls"] = [
                    call.model_dump(exclude_none=True) for call in calls
                ]

        logger.info(
            f"\n--- крок {step} | помилок поспіль={retries} "
            f"| prompt_tokens={response.usage.prompt_tokens} "
            f"| completion_tokens={response.usage.completion_tokens}"
            + (" | з кешу" if from_cache else "")
        )

        if len(all_calls) > 1 and not used_queued_call and not pending_calls:
            logger.info(
                f"  ПАКЕТ ВИКЛИКІВ: отримано {len(all_calls)}, "
                "у цьому кроці обробляється лише перший"
            )
        elif pending_calls and len(all_calls) > 1 and not used_queued_call:
            logger.info(
                f"  ПАКЕТ ВИКЛИКІВ: отримано {len(all_calls)}, "
                f"у черзі залишилося {len(pending_calls)}"
            )
        elif used_queued_call:
            logger.info(
                f"  ВИКЛИК ІЗ ЧЕРГИ: залишилося {len(pending_calls)}"
            )
        messages.append(model_message)

        if not calls:
            answer = msg.content or ""
            if min_tool_calls is not None and tool_calls_executed < min_tool_calls:
                logger.info(
                    f"  ВІДПОВІДЬ ВІДКЛАДЕНО: виконано {tool_calls_executed} "
                    f"з {min_tool_calls} обов'язкових викликів інструментів"
                )
                messages.append({
                    "role": "user",
                    "content": (
                        f"Ще не завершуй задачу: виконано {tool_calls_executed} "
                        f"з {min_tool_calls} потрібних викликів інструментів. "
                        "Продовжуй з наступного невиконаного пункту; не повторюй "
                        "вже отримані результати."
                    ),
                })
                messages = compress_history(messages, task, used, state, logger)
                continue
            logger.info(f"ВІДПОВІДЬ: {answer}")
            return answer

        had_error = False
        for call in calls:
            tool_calls_executed += 1
            raw_args = call.function.arguments
            if isinstance(raw_args, dict):
                raw_args = json.dumps(raw_args, ensure_ascii=False)

            logger.info(f"  виклик   : {call.function.name}({raw_args})")

            level, result = call_tool(call.function.name, raw_args)
            logger.info(f"  результат: [{level}] {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

            if level == "ok":
                state.record(call.function.name, raw_args, result)

            if level != "ok":
                had_error = True

        if had_error:
            retries += 1
            if retries > config.MAX_RETRIES:
                logger.warning(f"СТОП: модель не змогла виправити помилку за {config.MAX_RETRIES} спроби.")
                return None
        else:
            retries = 0

        messages = compress_history(messages, task, used, state, logger)

    logger.warning(f"СТОП: вичерпано ліміт кроків ({max_steps}).")
    return None


if __name__ == "__main__":
    run_agent("Які є вправи для спини та скільки коштує розтяжка?")
