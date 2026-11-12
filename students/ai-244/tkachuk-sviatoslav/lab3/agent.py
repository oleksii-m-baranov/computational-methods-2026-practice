"""Цикл агента і виклики інструментів."""
import logging
import sys
from pathlib import Path
from langfuse import observe
from langfuse.openai import OpenAI

import config
from dispatcher import MODEL_ERRORS, call_tool, check_response
from dispatcher_baseline import call_tool as call_tool_baseline
from schemas import SCHEMAS
from schemas_baseline import SCHEMAS as SCHEMAS_BASELINE

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from utils.lab_logger import custom_logger

logger = logging.getLogger(config.LAB_LOGFILE_NAME)


@observe()
def run_agent(task: str, client=None):
    """Повертає відповідь моделі або None, коли вичерпано ліміт; клієнт підмінюється у тестах."""
    if not logger.handlers:
        custom_logger(config.LAB_LOGFILE_NAME)
    if client is None:
        client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)

    messages = [{"role": "system", "content": config.SYSTEM},
                {"role": "user", "content": task}]
    retries = 0
    baseline = config.RUN_TAG == "baseline"

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, config.MAX_STEPS + 1):
        response = client.chat.completions.create(
            model=config.MODEL, messages=messages,
            tools=SCHEMAS_BASELINE if baseline else SCHEMAS,
            temperature=config.TEMPERATURE,
        )
        choice = response.choices[0]
        msg = choice.message
        usage = getattr(response, 'usage', None)
        tokens = getattr(usage, 'prompt_tokens', 'н/д')
        logger.info(f"\n--- крок {step} | помилок поспіль={retries} | prompt_tokens={tokens}" if not baseline
                    else f"\n--- крок {step} | prompt_tokens={tokens}")

        if not baseline:
            problem = check_response(choice)
            if problem is not None:
                level, text = problem
                logger.info(f"  рівень   : {level}")
                logger.info(f"  текст    : {msg.content}")
                retries += 1
                if retries > config.MAX_RETRIES:
                    logger.info("СТОП: модель не змогла сформувати правильний виклик")
                    return None
                if text is not None:
                    messages.append({"role": "assistant", "content": msg.content or ""})
                    messages.append({"role": "user", "content": text})
                continue

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        messages.append(msg)
        model_failed = False
        for call in msg.tool_calls:
            logger.info(f"  виклик   : {call.function.name}({call.function.arguments})")
            if baseline:
                result = call_tool_baseline(call.function.name, call.function.arguments)
            else:
                level, result = call_tool(call.function.name, call.function.arguments)
                logger.info(f"  рівень   : {level}")
                if level in MODEL_ERRORS:
                    model_failed = True
            logger.info(f"  результат: {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

        if not baseline:
            if model_failed:
                retries += 1
                if retries > config.MAX_RETRIES:
                    logger.info("СТОП: модель не змогла сформувати правильний виклик")
                    return None
            else:
                retries = 0

    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    run_agent("Кіт дряпає меблі, що робити?")
