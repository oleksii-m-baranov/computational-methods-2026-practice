"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py
"""
import json
import re

from tools import calc_materials, material_info, search_works

# Шість позицій (Варіант 16 — Ремонт квартири): пара (матеріал, площа в м²).
ITEMS = [
    ("шпалери", 14),
    ("фінішна шпаклівка", 30),
    ("інтер'єрна фарба", 36),
    ("ламінат", 11),
    ("керамічна плитка", 10),
    ("гіпсокартонний лист", 16),
]

# Питання для агента з переліком усіх шести позицій.
QUESTION = (
    "Для кожної з шести позицій ремонту: шпалери (площа 14 м²), фінішна шпаклівка (площа 30 м²), "
    "інтер'єрна фарба (площа 36 м²), ламінат (площа 11 м²), керамічна плитка (площа 10 м²), "
    "гіпсокартонний лист (площа 16 м²). Для кожної позиції: "
    "(а) знайди в корпусі ремонтних робіт, для яких робіт використовується цей матеріал, і наведи одним реченням; "
    "(б) знайди в довіднику ціну за одиницю та покриття в м²; "
    "(в) порахуй потрібну кількість одиниць і вартість для вказаної площі. "
    "У кінці назви загальну вартість усіх шести матеріалів одним числом у гривнях."
)

# Мінімум викликів інструментів для повного розв'язання: шість позицій по три інструменти.
MIN_CALLS = 18


def cost_of_one(material, area):
    """Вартість матеріалу на задану площу через прямі виклики інструментів."""
    works = search_works(material)
    assert "нічого не знайдено" not in works, f"Матеріал '{material}' не знайдено в корпусі"
    info = material_info(material)
    match_info = re.search(r"ціна:\s*(\d+(?:\.\d+)?)\s*грн,\s*покриття:\s*(\d+(?:\.\d+)?)\s*м²", info)
    if not match_info:
        raise ValueError(f"Не вдалося розібрати довідник для '{material}': {info}")
    price = float(match_info.group(1))
    coverage = float(match_info.group(2))
    calc_res = calc_materials(area, coverage, price)
    match_cost = re.search(r"вартість:\s*(\d+(?:\.\d+)?)\s*грн", calc_res)
    if not match_cost:
        raise ValueError(f"Не вдалося порахувати '{material}': {calc_res}")
    return float(match_cost.group(1))


def compute():
    """Правильна відповідь: сума по всіх шести позиціях. Рахуємо самі, без моделі."""
    total = 0.0
    for material, area in ITEMS:
        total += cost_of_one(material, area)
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


if __name__ == "__main__":
    task = save_task(compute())
    print("Правильна відповідь:", task["expected"])
    print("Файл long_task.json записано")
