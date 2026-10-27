"""Цикл агента."""
import json
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
            func_name = call.function.name
            args_raw = call.function.arguments

            # ЗАХИСТ ДЛЯ МАЛИХ МОДЕЛЕК: виправляємо ключі прямо «на льоту» перед викликом диспетчера
            try:
                args_dict = json.loads(args_raw)
            except:
                args_dict = {}

            # Якщо модель викликала search_routes, але передала 'category' замість 'query'
            if func_name == "search_routes" and "category" in args_dict and "query" not in args_dict:
                args_dict["query"] = args_dict.pop("category")
            # Якщо навпаки — функція чекає category, а модель передала query (про всяк випадок)
            elif func_name == "search_routes" and "query" in args_dict:
                pass  # у вашій схемі вимагається саме query, тож залишаємо

            # Якщо модель викликала transport_info, але передала 'destination' замість 'route'
            if func_name == "transport_info" and "destination" in args_dict and "route" not in args_dict:
                args_dict["route"] = args_dict.pop("destination")

            # Якщо модель викликала calc_budget, але забула 'extra' або передала price_per_person
            if func_name == "calc_budget":
                if "price_per_person" not in args_dict and "transport_cost" in args_dict:
                    args_dict["price_per_person"] = args_dict.pop("transport_cost")
                if "extra" not in args_dict:
                    args_dict["extra"] = 0  # безпечний дефолт, щоб не падало по missing argument

            fixed_args_raw = json.dumps(args_dict, ensure_ascii=False)

            logger.info(f"  виклик   : {func_name}({fixed_args_raw})")

            result = call_tool(func_name, fixed_args_raw)

            logger.info(f"  результат: {result}")

            # 5. результат повертаємо моделі з роллю tool
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })

    # сюди потрапляємо, якщо цикл дійшов до кінця без відповіді
    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    # Тестуємо ваше завдання з розрахунком бюджету на поїздку
    run_agent("Скільки вийде поїздка втрьох до Кам'янця-Подільського, якщо ще 500 грн на їжу на всіх?")