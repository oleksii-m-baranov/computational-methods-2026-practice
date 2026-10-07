"""Цикл агента."""
from langfuse import observe
from langfuse.openai import OpenAI

import config
from schemas import SCHEMAS
from dispatcher import call_tool, check_response, MODEL_ERRORS        # НОВЕ
from utils.lab_logger import custom_logger

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
logger = custom_logger(config.LAB_LOGFILE_NAME)


@observe()
def run_agent(task):
    """task – питання користувача
    Повертає текст відповіді або None, якщо вичерпано ліміт."""

    # історія розмови: системне повідомлення і питання
    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]
    retries = 0                                                       # НОВЕ: помилок моделі поспіль

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, config.MAX_STEPS + 1):
        # 1. запит до моделі: передаємо ВСЮ історію заново
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )
        choice = response.choices[0]
        msg = choice.message

        logger.info(f"\n--- крок {step} | помилок поспіль={retries} "           # НОВЕ
                    f"| prompt_tokens={response.usage.prompt_tokens}")

        # НОВЕ: обрив або зламаний виклик у тексті відповіді
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

        # 2. немає tool_calls – модель дала відповідь, виходимо
        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        # 3. пропозицію моделі кладемо в історію
        messages.append(msg)

        # 4. виконуємо кожен запитаний виклик
        model_failed = False                                          # НОВЕ
        for call in msg.tool_calls:
            logger.info(f"  виклик   : {call.function.name}({call.function.arguments})")

            level, result = call_tool(call.function.name, call.function.arguments)   # НОВЕ

            logger.info(f"  рівень   : {level}")                              # НОВЕ
            logger.info(f"  результат: {result}")

            # 5. результат повертаємо моделі з роллю tool
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })
            if level in MODEL_ERRORS:                                 # НОВЕ
                model_failed = True

        # НОВЕ: рахуємо помилки моделі поспіль
        if model_failed:
            retries += 1

            if retries > config.MAX_RETRIES:
                logger.info("СТОП: модель не змогла сформувати правильний виклик")
                return None
        else:
            retries = 0

    # сюди потрапляємо, якщо цикл дійшов до кінця без відповіді
    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    run_agent("Знайди щось легке з фантастики")
