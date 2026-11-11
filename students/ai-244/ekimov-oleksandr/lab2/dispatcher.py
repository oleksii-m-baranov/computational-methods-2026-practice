"""Виклик інструмента за назвою, отриманою від моделі."""
import json
from tools import TOOLS


def call_tool(name: str, args_raw: str) -> str:
    # модель могла назвати інструмент, якого не існує
    if name not in TOOLS:
        return (f"Помилка: інструмента '{name}' не існує. "
                f"Доступні: {', '.join(TOOLS)}")
    try:
        args = json.loads(args_raw)        # рядок -> словник
        return str(TOOLS[name](**args))    # ** розпаковує словник в аргументи
    except json.JSONDecodeError:
        return "Помилка: аргументи не є коректним JSON."
    except TypeError as e:
        return f"Помилка в аргументах: {e}"
    except Exception as e:
        return f"Помилка виконання: {e}"
if __name__ == "__main__":

        print("1:", call_tool("search_routes", '{"query": "природа"}'))

        print("2:", call_tool("delete_all", '{}'))

        print("3:", call_tool("search_routes", '{"query": природа}'))

        print("4:", call_tool("search_routes", '{"text": "природа"}'))
