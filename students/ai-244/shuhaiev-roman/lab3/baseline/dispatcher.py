"""Диспетчер з ЛР2 без змін (виклик інструмента за назвою)."""
import json
from tools import TOOLS as ALL_TOOLS

# у ЛР2 були лише три інструменти
TOOLS = {name: ALL_TOOLS[name] for name in ["search_exercises", "schedule_info", "calc_calories"]}


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
