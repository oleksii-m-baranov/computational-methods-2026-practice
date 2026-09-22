"""Цикл агента."""
from openai import OpenAI
import config
from schemas import SCHEMAS
from dispatcher import call_tool
from utils.lab_logger import custom_logger

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
logger = custom_logger('lab2')


def run_agent(task):
    """task – питання користувача
    Повертає текст відповіді або None, якщо вичерпано ліміт."""

    # історія розмови: системне повідомлення і питання
    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]

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
        msg = response.choices[0].message

        logger.info(f"\n--- крок {step} | prompt_tokens={response.usage.prompt_tokens}")

        # 2. немає tool_calls – модель дала відповідь, виходимо
        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        # 3. пропозицію моделі кладемо в історію
        messages.append(msg)

        # 4. виконуємо кожен запитаний виклик
        for call in msg.tool_calls:
            logger.info(f" виклик : {call.function.name}({call.function.arguments})")
            result = call_tool(call.function.name, call.function.arguments)
            logger.info(f" результат: {result}")


        # 5. результат повертаємо моделі з роллю tool
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": result,
        })

    # сюди потрапляємо, якщо цикл дійшов до кінця без відповіді
    logger.info("СТОП: вичерпано ліміт кроків")
    return None
