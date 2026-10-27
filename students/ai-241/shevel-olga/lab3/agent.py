"""Цикл агента з перевірками викликів."""
from langfuse import observe
from langfuse.openai import OpenAI

import config
from schemas import SCHEMAS
from dispatcher import call_tool, check_response, MODEL_ERRORS
from utils.lab_logger import custom_logger

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
logger = custom_logger(config.LAB_LOGFILE_NAME)


@observe()
def run_agent(task):
    """task – питання користувача
    Повертає текст відповіді або None, якщо вичерпано ліміт."""

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]
    retries = 0  # помилок моделі поспіль

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, config.MAX_STEPS + 1):
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )
        choice = response.choices[0]
        msg = choice.message

        logger.info(f"\n--- крок {step} | помилок поспіль={retries} "
                    f"| prompt_tokens={response.usage.prompt_tokens}")

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

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        messages.append(msg)

        model_failed = False
        for call in msg.tool_calls:
            logger.info(f"  виклик   : {call.function.name}({call.function.arguments})")

            level, result = call_tool(call.function.name, call.function.arguments)

            logger.info(f"  рівень   : {level}")
            logger.info(f"  результат: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })
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

    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    run_agent("Скільки коштує відправити 15 кг до Львова?")
