"""Цикл агента з перевірками викликів, скороченням історії, станом і кешем."""
from langfuse import observe
import time

import config
from model import call_model
from compress import compress_history
from state import TaskState
from dispatcher import call_tool, check_response, MODEL_ERRORS

try:
    from utils.lab_logger import custom_logger
except ImportError:
    # запасний варіант, якщо utils недоступний: пише і у logs/<name>.log, і в консоль
    import logging
    import os
    import sys

    def custom_logger(name, overwrite=False):
        os.makedirs("logs", exist_ok=True)
        log = logging.getLogger(name)
        for h in list(log.handlers):             # щоб повторний виклик не дублював рядки
            log.removeHandler(h)
            h.close()
        log.setLevel(logging.INFO)
        log.propagate = False
        fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s",
                                "%Y-%m-%d %H:%M:%S")
        mode = "w" if overwrite else "a"
        for h in (logging.FileHandler(f"logs/{name}.log", mode=mode, encoding="utf-8"),
                  logging.StreamHandler(sys.stdout)):
            h.setFormatter(fmt)
            log.addHandler(h)
        return log


LAST_RUN = {}

def _finish(status, answer, steps, prompt_tokens, completion_tokens, started):
    LAST_RUN.clear()
    LAST_RUN.update({
        "status": status, "steps": steps, "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "seconds": round(time.time() - started, 1),
    })
    return answer


@observe()
def run_agent(task, max_steps=None, logfile_name=config.LAB_LOGFILE_NAME,
              task_id="task", log_overwrite=False):
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
    started = time.time()
    steps = prompt_total = completion_total = 0

    def finish(status, answer=None):
        return _finish(status, answer, steps, prompt_total, completion_total, started)

    state = TaskState(task_id)                # записник результатів інструментів
    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, max_steps + 1):

        # 1. запит до моделі: передаємо ВСЮ історію заново
        response, from_cache = call_model(messages, step, logger)
        if response is None:                  # сервер повернув помилку (вона вже записана в лог)
            return finish("server_error")
        choice = response.choices[0]
        msg = choice.message
        used = response.usage.prompt_tokens   # скільки токенів було на вході цього виклику
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

        # 2. немає tool_calls – модель дала відповідь, виходимо
        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return finish("final", msg.content)

        # 3. Один виклик інструмента на крок. Деякі локальні моделі повертають
        # багато tool_calls одразу; тоді задача з 18 викликів закінчувалася за
        # 2 кроки і не перевіряла обмеження контекстного вікна. Решту запропонованих
        # викликів не виконуємо наперед: на наступному кроці модель побачить
        # результат першого і сама вирішить, що робити далі.
        calls = list(msg.tool_calls)
        assistant_msg = msg.model_dump(exclude_none=True)
        if len(calls) > 1:
            logger.info(f"  ПОСЛІДОВНИЙ РЕЖИМ: модель запропонувала {len(calls)} викликів, виконуємо перший")
            assistant_msg["tool_calls"] = [calls[0].model_dump(exclude_none=True)]
        messages.append(assistant_msg)

        # 4. Виконуємо лише перший запитаний виклик.
        model_failed = False
        for call in calls[:1]:
            logger.info(f"  виклик   : {call.function.name}({call.function.arguments})")

            level, result = call_tool(call.function.name, call.function.arguments)

            logger.info(f"  рівень   : {level}")
            logger.info(f"  результат: {result}")

            # 5. результат повертаємо моделі з роллю tool
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
                return finish("retry_limit")
        else:
            retries = 0

        # якщо вхід завеликий, скорочуємо історію
        messages = compress_history(messages, task, used, state, logger)

    # сюди потрапляємо, якщо цикл дійшов до кінця без відповіді
    logger.info("СТОП: вичерпано ліміт кроків")
    return finish("step_limit")


if __name__ == "__main__":
    run_agent("Який ліміт ручної поклажі в клубі?")
