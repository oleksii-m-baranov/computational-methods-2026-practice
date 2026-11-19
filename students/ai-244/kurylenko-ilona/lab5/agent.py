"""Цикл агента."""
import time
from langfuse import observe

import config
from model import call_model
from compress import compress_history
from state import TaskState
from dispatcher import call_tool, check_response, MODEL_ERRORS
from utils.lab_logger import custom_logger

# Підсумок останнього прогону; його читає measure_rag.py
# status: final | server_error | retry_limit | step_limit (як у lab4/logparse.py)
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
    retries = 0

    state = TaskState(task_id)  # записник результатів інструментів
    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    started = time.time()
    steps = prompt_total = completion_total = 0

    def finish(status, answer=None):
        return _finish(status, answer, steps, prompt_total, completion_total, started)

    for step in range(1, max_steps + 1):
        response, from_cache = call_model(messages, step, logger)
        if response is None:                  # сервер повернув помилку (вона вже записана в лог)
            return finish("server_error")
        choice = response.choices[0]
        msg = choice.message
        used = response.usage.prompt_tokens  # скільки токенів було на вході цього виклику

        steps += 1
        prompt_total += response.usage.prompt_tokens
        completion_total += response.usage.completion_tokens

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
                return finish("retry_limit")
            if text is not None:
                messages.append({"role": "assistant", "content": msg.content})
                messages.append({"role": "user", "content": text})
            continue

        # немає tool_calls – модель дала відповідь, виходимо
        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return finish("final", msg.content)

        # пропозицію моделі кладемо в історію
        messages.append(msg.model_dump(exclude_none=True))

        # виконуємо кожен запитаний виклик
        model_failed = False
        for call in msg.tool_calls:
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
            if level == "ok":
                state.record(call.function.name, call.function.arguments, result)
            if level in MODEL_ERRORS:
                model_failed = True

        if model_failed:
            retries += 1
            if retries > config.MAX_RETRIES:
                logger.info("СТОП: модель не змогла сформувати правильний виклик")
                return finish("retry_limit")
        else:
            retries = 0

        # якщо вхід завеликий, скорочуємо історію
        messages = compress_history(messages, task, used, state, logger)

    logger.info("СТОП: вичерпано ліміт кроків")
    return finish("step_limit")


if __name__ == "__main__":
    run_agent("Кіт дряпає меблі, що робити?")
