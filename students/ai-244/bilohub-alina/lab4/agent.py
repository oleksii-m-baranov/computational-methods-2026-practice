"""Цикл агента з перевірками викликів, скороченням історії, станом і кешем."""
from langfuse import observe

import config
from model import call_model
from compress import compress_history
from state import TaskState
from dispatcher import call_tool, check_response, MODEL_ERRORS
from utils.lab_logger import custom_logger


@observe()
def run_agent(task, max_steps=None, logfile_name=config.LAB_LOGFILE_NAME, task_id="task", log_overwrite=False):
    """task – питання користувача
    Повертає текст відповіді або None, якщо вичерпано ліміт."""
    logger = custom_logger(logfile_name, overwrite=log_overwrite)
    max_steps = max_steps or config.MAX_STEPS

    # історія розмови: системне повідомлення і питання
    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]
    retries = 0  # помилок моделі поспіль

    state = TaskState(task_id)                # записник результатів інструментів
    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, max_steps + 1):
        response, from_cache = call_model(messages, step, logger)
        if response is None:                  # сервер повернув помилку (вона вже записана в лог)
            return None
        choice = response.choices[0]
        msg = choice.message
        used = response.usage.prompt_tokens   # скільки токенів було на вході цього виклику

        logger.info(f"\n--- крок {step} | помилок поспіль={retries} "
                    f"| prompt_tokens={response.usage.prompt_tokens} "
                    f"| completion_tokens={response.usage.completion_tokens}"
                    + (" | з кешу" if from_cache else ""))

        # обрив або зламаний виклик у тексті відповіді
        problem = check_response(choice)
        if problem is not None:
            level, text = problem
            logger.info(f"  рівень   : {level}")
            logger.info(f"  текст    : {msg.content}")
            retries = retries + 1
            if retries > config.MAX_RETRIES:
                logger.info("СТОП: модель не змогла сформувати правильний виклик")
                return None
            if text is not None:
                messages.append({"role": "assistant", "content": msg.content})
                messages.append({"role": "user", "content": text})
            continue

        # немає tool_calls – модель дала відповідь, виходимо
        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        # модель могла запросити кілька викликів за один крок
        calls = msg.tool_calls
        one_call = getattr(config, "ONE_CALL_PER_STEP", False)
        if one_call and len(calls) > 1:
            logger.info(f"  ПОПЕРЕДЖЕННЯ: модель запросила {len(calls)} викликів за раз, "
                        "виконується лише перший")
            calls = calls[:1]

        # зберігаємо повідомлення моделі як словник: trim читає з нього ключ "role"
        assistant_message = msg.model_dump(exclude_none=True)
        if one_call:
            assistant_message["tool_calls"] = assistant_message["tool_calls"][:1]
        messages.append(assistant_message)

        # виконуємо кожен запитаний виклик
        model_failed = False
        for call in calls:
            logger.info(f"  виклик   : {call.function.name}({call.function.arguments})")

            level, result = call_tool(call.function.name, call.function.arguments)

            logger.info(f"  рівень   : {level}")
            logger.info(f"  результат: {result}")

            # результат повертаємо моделі з роллю tool
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })
            # у стан потрапляють лише успішні виклики
            if level == "ok":
                state.record(call.function.name, call.function.arguments, result)
            if level in MODEL_ERRORS:
                model_failed = True

        # рахуємо помилки моделі поспіль
        if model_failed:
            retries = retries + 1
            if retries > config.MAX_RETRIES:
                logger.info("СТОП: модель не змогла сформувати правильний виклик")
                return None
        else:
            retries = 0

        # якщо вхід завеликий, скорочуємо історію
        messages = compress_history(messages, task, used, state, logger)

    # сюди потрапляємо, якщо цикл дійшов до кінця без відповіді
    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    run_agent("Знайди щось легке з фантастики")
