
"""Цикл кухонного агента з перевірками та трасуванням."""

from langfuse import observe


import os
import config
import guided_longrun
import longrun_guard
from model import call_model
from compress import compress_history
from state import TaskState
from dispatcher import call_tool, check_response, MODEL_ERRORS
from utils.lab_logger import custom_logger





@observe()
def run_agent(task, max_steps=None, logfile_name=config.LAB_LOGFILE_NAME, task_id="task", log_overwrite=False):
    """Виконує завдання та повертає відповідь агента."""
    # Додаткова діагностика: базові режими та історичні логи НЕ змінюємо.
    if os.environ.get("LAB4_GUIDED_V3") == "1" and guided_longrun.applies_to(task):
        return guided_longrun.run_guided(task, max_steps=max_steps, logfile_name=logfile_name,
                                         task_id=task_id, log_overwrite=log_overwrite)
    max_steps = max_steps or config.MAX_STEPS
    logger = custom_logger(logfile_name, overwrite=log_overwrite)
    state = TaskState(task_id)

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]

    consecutive_errors = 0

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")
    if os.environ.get("LAB4_LONGRUN_GUARD") == "1":
        logger.info("  ЕКСПЕРИМЕНТАЛЬНИЙ КОНТРОЛЬ ПОВНОТИ: увімкнено")

    for step in range(1, max_steps + 1):
        response, from_cache = call_model(messages, step, logger)

        if response is None:
            return None

        choice = response.choices[0]
        msg = choice.message

        if (
            config.SERIAL_TOOL_CALLS
            and msg.tool_calls
            and len(msg.tool_calls) > 1
        ):
            count = len(msg.tool_calls)
            logger.info(
                f"  ПОСЛІДОВНИЙ РЕЖИМ: модель запропонувала "
                f"{count} викликів; виконуємо перший"
            )
            msg.tool_calls = msg.tool_calls[:1]

        usage = response.usage

        prompt_tokens = (
            usage.prompt_tokens if usage else None
        )

        completion_tokens = (
            usage.completion_tokens if usage else None
        )

        logger.info(
            f"\n--- крок {step} | "
            f"помилок поспіль={consecutive_errors} "
            f"| prompt_tokens={prompt_tokens if prompt_tokens is not None else 'невідомо'} "
            f"| completion_tokens={completion_tokens if completion_tokens is not None else 'невідомо'}"
            + (" | з кешу" if from_cache else "")
        )

        response_ok, response_message = check_response(choice)

        if not response_ok:
            logger.warning(f"Некоректна відповідь моделі: {response_message}")
            consecutive_errors += 1

            if consecutive_errors > config.MAX_RETRIES:
                logger.error("СТОП: модель не змогла сформувати правильний виклик")
                return None

            messages.append({
                "role": "assistant",
                "content": msg.content or "",
            })
            messages.append({
                "role": "user",
                "content": (
                    "Попередня відповідь була некоректною. "
                    "Надай завершену відповідь або коректний виклик інструмента."
                ),
            })
            continue

        if not msg.tool_calls:
            # Додаткова діагностика: звичайні прогони залишаються БЕЗ змін.
            if os.environ.get("LAB4_LONGRUN_GUARD") == "1" and longrun_guard.applies_to(task):
                complete, reminder = longrun_guard.verify_before_final(state.results)
                if not complete:
                    logger.info("  НЕПОВНЕ ВИКОНАННЯ: агент намагався відповісти до завершення всіх 18 дій")
                    messages.append({"role": "assistant", "content": msg.content or ""})
                    messages.append({"role": "user", "content": reminder})
                    messages = compress_history(messages, task, prompt_tokens or 0, state, logger)
                    continue
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        messages.append(msg.model_dump(exclude_none=True))

        for call in msg.tool_calls:
            name = call.function.name
            arguments = call.function.arguments

            logger.info(f"  виклик   : {name}({arguments})")

            level, result = call_tool(name, arguments)

            logger.info(f"  рівень   : {level}")
            logger.info(f"  результат: {result}")
            if level == "ok":
                state.record(name, arguments, result)

            if level in MODEL_ERRORS:
                consecutive_errors += 1

                if consecutive_errors > config.MAX_RETRIES:
                    logger.error("СТОП: модель не змогла сформувати правильний виклик")
                    return None

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": f"Помилка {level}: {result}. Виправ виклик інструмента.",
                })
            else:
                if level == "ok":
                    consecutive_errors = 0

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                })

        messages = compress_history(messages, task, prompt_tokens or 0, state, logger)

    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    run_agent("Знайди щось із куркою")

