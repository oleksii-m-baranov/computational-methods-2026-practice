"""Виклик інструмента за назвою, отриманою від моделі."""
import json
from tools import TOOLS


def call_tool(name: str, args_raw: str) -> str:
    # Модель могла назвати інструмент, якого не існує
    if name not in TOOLS:
        return (f"Помилка: інструмента '{name}' не існує. "
                f"Доступні: {', '.join(TOOLS)}")
    try:
        # Парсимо аргументи з рядка JSON у словник
        if isinstance(args_raw, str):
            args = json.loads(args_raw)
        elif isinstance(args_raw, dict):
            args = args_raw
        else:
            args = {}

        # Безпосередній виклик функції з розпакуванням словника аргументів (**args).
        # Це гарантує, що передадуться саме ті ключі, які чекає ваша функція (query, route тощо).
        return str(TOOLS[name](**args))

    except json.JSONDecodeError:
        return "Помилка: аргументи не є коректним JSON."
    except TypeError as e:
        return f"Помилка в аргументах: {e}"
    except Exception as e:
        return f"Помилка виконання: {e}"


if __name__ == "__main__":
    print(call_tool("search_routes", '{"query": "карпати"}'))