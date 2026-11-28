"""Цикл агента, валідація викликів і метрики прогону."""
import time
import sys
from pathlib import Path
from langfuse import observe

import config
from compress import compress_history
from dispatcher import MODEL_ERRORS, call_tool, check_response
from model import call_model
from state import TaskState

LAST_RUN = {}


def _finish(status, answer, steps, prompt_tokens, completion_tokens, started):
    LAST_RUN.clear()
    LAST_RUN.update({"status": status, "steps": steps, "prompt_tokens": prompt_tokens,
                     "completion_tokens": completion_tokens, "seconds": round(time.perf_counter() - started, 2)})
    return answer


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from utils.lab_logger import custom_logger


@observe()
def run_agent(task, max_steps=None, logfile_name=config.LAB_LOGFILE_NAME,
              task_id="task", log_overwrite=False):
    logger = custom_logger(logfile_name, overwrite=log_overwrite)
    started = time.perf_counter()
    steps = prompt_total = completion_total = 0

    def finish(status, answer=None):
        return _finish(status, answer, steps, prompt_total, completion_total, started)

    state = TaskState(task_id)
    messages = [{"role": "system", "content": config.SYSTEM}, {"role": "user", "content": task}]
    retries = 0
    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, (max_steps or config.MAX_STEPS) + 1):
        response, from_cache = call_model(messages, step, logger)
        if response is None:
            return finish("server_error")
        choice = response.choices[0]
        msg = choice.message
        used = response.usage.prompt_tokens if response.usage else 0
        output_tokens = response.usage.completion_tokens if response.usage else 0
        steps += 1
        prompt_total += used
        completion_total += output_tokens
        logger.info(f"\n--- крок {step} | помилок поспіль={retries} "
                    f"| prompt_tokens={used} | completion_tokens={output_tokens}"
                    + (" | з кешу" if from_cache else ""))
        problem = check_response(choice)
        if problem is not None:
            level, note = problem
            logger.info(f"  рівень   : {level}")
            logger.info(f"  текст    : {msg.content}")
            retries += 1
            if retries > config.MAX_RETRIES:
                logger.info("СТОП: модель не змогла сформувати правильний виклик")
                return finish("retry_limit")
            if note:
                messages.append({"role": "assistant", "content": msg.content or ""})
                messages.append({"role": "user", "content": note})
            continue

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return finish("final", msg.content)

        messages.append(msg.model_dump(exclude_none=True))
        model_failed = False
        for call in msg.tool_calls:
            logger.info(f"  виклик   : {call.function.name}({call.function.arguments})")
            level, result = call_tool(call.function.name, call.function.arguments)
            logger.info(f"  рівень   : {level}")
            logger.info(f"  результат: {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
            if level == "ok":
                if config.USE_STATE:
                    state.record(call.function.name, call.function.arguments, result)
            if level in MODEL_ERRORS:
                model_failed = True
        retries = retries + 1 if model_failed else 0
        if retries > config.MAX_RETRIES:
            logger.info("СТОП: модель не змогла сформувати правильний виклик")
            return finish("retry_limit")
        messages = compress_history(messages, task, used, state, logger)

    logger.info("СТОП: вичерпано ліміт кроків")
    return finish("step_limit")


if __name__ == "__main__":
    run_agent("Кіт дряпає меблі, що робити?")
