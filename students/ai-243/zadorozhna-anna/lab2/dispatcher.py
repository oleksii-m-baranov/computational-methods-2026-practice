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
    # 1. правильний виклик — має повернути результат пошуку
    print(call_tool("search_recipes", '{"query": "сир"}'))
    print()
    # 2. неіснуючий інструмент — має повернути помилку зі списком доступних
    print(call_tool("delete_all", '{}'))
    print()
    # 3. зіпсований JSON (без лапок) — має повернути помилку JSON
    print(call_tool("search_recipes", '{"query": сир}'))
    print()
    # 4. неправильна назва аргумента — має повернути помилку в аргументах
    print(call_tool("search_recipes", '{"text": "сир"}'))
    print()
    # 5. правильний виклик product_info
    print(call_tool("product_info", '{"product": "рис"}'))
    print()
    # 6. правильний виклик scale_amount
    print(call_tool("scale_amount", '{"amount": 200, "base_servings": 2, "target_servings": 6}'))