"""Цикл агента для варіанта 7 (Подорожі)."""
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

    # Історія розмови: системне повідомлення і питання користувача
    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, config.MAX_STEPS + 1):

        # 1. Запит до моделі: передаємо всю історію заново
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )
        msg = response.choices[0]

        logger.info(f"\n--- крок {step} | prompt_tokens={response.usage.prompt_tokens}")

        # 2. Якщо немає tool_calls – модель дала остаточну відповідь, виходимо
        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        # 3. Пропозицію моделі кладемо в історію
        messages.append(msg)

        # 4. Виконуємо кожен запитаний виклик інструмента
        for call in msg.tool_calls:
            func_name = call.function.name
            args_raw = call.function.arguments

            # Захист для малих моделей: парсимо JSON аргументів
            try:
                args_dict = json.loads(args_raw)
            except Exception:
                args_dict = {}

            # Якщо модель викликала search_routes, але передала 'category' замість 'query'
            if func_name == "search_routes" and "category" in args_dict and "query" not in args_dict:
                args_dict["query"] = args_dict.pop("category")

            # Якщо модель викликала transport_info, але передала 'destination' або 'city' замість 'route'
            if func_name == "transport_info":
                if "destination" in args_dict and "route" not in args_dict:
                    args_dict["route"] = args_dict.pop("destination")
                elif "city" in args_dict and "route" not in args_dict:
                    args_dict["route"] = args_dict.pop("city")

            # Якщо модель викликала calc_budget, але передала інші ключі або забула 'extra'
            if func_name == "calc_budget":
                if "price_per_person" not in args_dict and "transport_cost" in args_dict:
                    args_dict["price_per_person"] = args_dict.pop("transport_cost")
                if "extra" not in args_dict:
                    args_dict["extra"] = 0  # Безпечний дефолт

            fixed_args_raw = json.dumps(args_dict, ensure_ascii=False)

            logger.info(f"  виклик   : {func_name}({fixed_args_raw})")

            # Викликаємо диспетчер
            result = call_tool(func_name, fixed_args_raw)

            logger.info(f"  результат: {result}")

            # 5. Результат повертаємо моделі з роллю tool
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })

    # Сюди потрапляємо, якщо цикл дійшов до ліміту кроків без відповіді
    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    # Тестуємо ваше завдання з розрахунком бюджету на поїздку
    run_agent("Скільки вийде поїздка втрьох до Кам'янця-Подільського, якщо ще 500 грн на їжу на всіх?")
