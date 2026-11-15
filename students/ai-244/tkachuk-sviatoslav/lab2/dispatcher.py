"""Безпечне виконання інструмента за запитом мовної моделі."""
import json
from tools import TOOLS


def call_tool(name: str, args_raw: str) -> str:
    if name not in TOOLS:
        return (f"Помилка: інструмента '{name}' не існує. "
                f"Доступні: {', '.join(TOOLS)}")
    try:
        args = json.loads(args_raw)
        if not isinstance(args, dict):
            return "Помилка: аргументи повинні бути JSON-об'єктом."
        return str(TOOLS[name](**args))
    except json.JSONDecodeError:
        return "Помилка: аргументи не є коректним JSON."
    except TypeError as e:
        return f"Помилка в аргументах: {e}"
    except Exception as e:
        return f"Помилка виконання: {e}"


if __name__ == "__main__":
    print(call_tool("search_articles", '{"query": "дряпає"}'))
    print(call_tool("delete_all", '{}'))
    print(call_tool("search_articles", '{"query": дряпає}'))
    print(call_tool("search_articles", '{"text": "дряпає"}'))
