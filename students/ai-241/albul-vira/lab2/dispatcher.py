"""Виклик інструмента за назвою, отриманою від моделі."""
import json
from tools import TOOLS


def call_tool(name: str, args_raw: str) -> str:
    if name not in TOOLS:
        return (f"Помилка: інструмента '{name}' не існує. "
                f"Доступні: {', '.join(TOOLS)}")
    try:
        args = json.loads(args_raw)
        return str(TOOLS[name](**args))
    except json.JSONDecodeError:
        return "Помилка: аргументи не є коректним JSON."
    except TypeError as e:
        return f"Помилка в аргументах: {e}"
    except Exception as e:
        return f"Помилка виконання: {e}"


if __name__ == "__main__":
    print("1. Успішний виклик:")
    print(call_tool("search_books", '{"query": "фантастика"}'))
    
    print("\n2. Неіснуючий інструмент:")
    print(call_tool("delete_all", '{}'))
    
    print("\n3. Некоректний JSON:")
    print(call_tool("search_books", '{"query": фантастика}'))
    
    print("\n4. Неправильні назви аргументів:")
    print(call_tool("search_books", '{"text": "фантастика"}'))
