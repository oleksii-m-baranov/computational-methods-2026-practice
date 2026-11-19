import json
import re
from tools import search_routes, transport_info, calc_budget

# 1. Шість позицій з вашого transport.csv: (назва_маршруту, кількість_осіб, додаткові_витрати)
ITEMS = [
    ("Кам'янець-Подільський", 2, 300),
    ("Одеса", 3, 500),
    ("Львів", 4, 400),
    ("Умань", 2, 200),
    ("Чернівці", 3, 450),
    ("Яремче", 2, 350),
]

items_list_str = ", ".join(
    f"{route} ({people} осіб, додаткові витрати {extra} грн)"
    for route, people, extra in ITEMS
)

# 2. Текст довгої задачі
QUESTION = (
    f"Для кожної з шести позицій: {items_list_str}. "
    "Для кожної: (а) знайди в корпусі опис маршруту і наведи одним реченням; "
    "(б) знайди в довіднику вартість проїзду; "
    "(в) порахуй бюджет на групу із заданої кількості осіб з урахуванням додаткових витрат. "
    "У кінці назви загальний бюджет одним числом."
)


def cost_of_one(route: str, people: int, extra: float) -> float:
    """Прямий розрахунок еталонної відповіді для однієї позиції без LLM."""
    _ = search_routes(query=route)

    info_text = transport_info(route=route)
    match = re.search(r"(\d+(?:\.\d+)?)\s*грн", info_text)
    if not match:
        raise ValueError(f"Не вдалося знайти ціну у відповіді transport_info: {info_text}")
    price = float(match.group(1))

    budget_res = calc_budget(price_per_person=price, people=people, extra=extra)
    return float(budget_res)


def main():
    total_budget = sum(cost_of_one(route, people, extra) for route, people, extra in ITEMS)
    expected_answer = int(total_budget) if total_budget.is_integer() else round(total_budget, 2)

    task_data = {
        "question": QUESTION,
        "expected": expected_answer,
        "min_calls": 18,
    }

    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task_data, f, ensure_ascii=False, indent=2)

    print("Збережено long_task.json:")
    print(json.dumps(task_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()