"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py
Варіант 3 (доставка посилок): кожна позиція - (місто, вага в кг, тип вантажу).
"""
import json
import re

from tools import tariff_info, calc_price

ITEMS = [("Київ", 6.0, "документи"), ("Львів", 4.5, "одяг"),
         ("Харків", 6.0, "побутова техніка"), ("Одеса", 3.0, "рідини"),
         ("Дніпро", 5.0, "крихкі вантажі"), ("Запоріжжя", 7.5, "побутова електроніка")]

QUESTION = (
    "Для кожної з шести посилок: Київ 6.0 кг (документи), Львів 4.5 кг (одяг), "
    "Харків 6.0 кг (побутова техніка), Одеса 3.0 кг (рідини), "
    "Дніпро 5.0 кг (крихкі вантажі), Запоріжжя 7.5 кг (побутова електроніка). "
    "Для кожної: (а) знайди в правилах перевезення правило для цього типу вантажу "
    "і назви його одним реченням; (б) знайди в довіднику тариф міста; "
    "(в) порахуй вартість доставки з урахуванням мінімальної вартості. "
    "У кінці назви загальну вартість усіх шести посилок одним числом."
)

# Мінімум викликів інструментів: шість посилок по три інструменти
MIN_CALLS = 18


def cost_of_one(city, weight):
    """Вартість однієї посилки: тариф з довідника + calc_price (з урахуванням мінімуму)."""
    info = tariff_info(city)        # "Ціна: 18 грн/кг, термін: 2 днів, мінімальна вартість: 70 грн"
    price_per_kg = float(re.search(r"Ціна: ([\d.]+)", info).group(1))
    min_price = float(re.search(r"мінімальна вартість: ([\d.]+)", info).group(1))
    result = calc_price(weight, price_per_kg, min_price)    # "90.0 грн" або "70.0 грн (спрацювала ...)"
    return float(re.match(r"[\d.]+", result).group())


def compute():
    """Правильна відповідь: сума по всіх шести посилках. Рахуємо самі, без моделі."""
    total = 0.0
    for city, weight, _ in ITEMS:
        total = total + cost_of_one(city, weight)
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
