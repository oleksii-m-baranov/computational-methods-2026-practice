"""7	Подорожі	Шість відрізків маршруту	Вартість проїзду	Бюджет на групу з заданої кількості осіб	Загальний бюджет

Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.
Запуск:  python make_task.py
"""
import json
import re

from tools import calc_budget, transport_info

ROUTES = [
    "Стара Фортеця — Кам'янець-Подільський",
    "Зелені Карпати — Яремче",
    "Морський Бриз — Одеса",
    "Смачні Карпати — Яремче",
    "Замкова Спадщина — Луцьк",
    "Стежки Опришків — Славське",
]
PEOPLE = 4

QUESTION = (
    f"Є шість відрізків маршруту: {'; '.join(ROUTES)}. "
    f"Для кожного відрізка знайди в довіднику вартість проїзду на одну особу "
    f"та порахуй бюджет для групи з {PEOPLE} осіб без додаткових витрат. "
    "Наведи вартість на одну особу і бюджет групи для кожного відрізка, "
    "а наприкінці підсумуй бюджети всіх шести відрізків."
)

MIN_CALLS = len(ROUTES) * 2


def price_for_route(route):
    """Повертає ціну проїзду на одну особу з довідника."""
    info = transport_info(route)
    match = re.search(r"Вартість проїзду:\s*([\d.]+)\s*грн", info)
    if match is None:
        raise ValueError(f"Не вдалося отримати вартість для маршруту {route!r}: {info}")
    return float(match.group(1))


def compute():
    """Обчислює загальний бюджет групи за допомогою інструментів."""
    total = 0.0
    for route in ROUTES:
        price = price_for_route(route)
        budget = calc_budget(price, PEOPLE, 0)
        match = re.fullmatch(r"([\d.]+)\s*грн", budget)
        if match is None:
            raise ValueError(f"Не вдалося прочитати бюджет для маршруту {route!r}: {budget}")
        total += float(match.group(1))
    return total


def save_task(total):
    """Записує питання, правильну відповідь і MIN_CALLS у файл long_task.json."""
    task = {
        "id": "L1",
        "question": QUESTION,
        "expected": format(round(total, 2), "g"),
        "min_calls": MIN_CALLS,
    }
    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


task = save_task(compute())
print("Правильна відповідь:", task["expected"])
print("Файл long_task.json записано")