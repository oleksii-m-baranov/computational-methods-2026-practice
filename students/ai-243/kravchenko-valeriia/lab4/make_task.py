"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py
"""
import json
import re

# Беремо твої функції з tools.py
from tools import calc_price, tariff_info

# Шість позицій (місто, вага)
ITEMS = [("Київ", 2.0), ("Львів", 1.5), ("Харків", 3.0),
         ("Одеса", 1.0), ("Дніпро", 2.5), ("Запоріжжя", 4.0)]

# Питання для агента
QUESTION = (
    "Для кожної з шести посилок: Київ 2.0 кг, Львів 1.5 кг, Харків 3.0 кг, Одеса 1.0 кг, "
    "Дніпро 2.5 кг, Запоріжжя 4.0 кг. Для кожної: (а) знайди в правилах доставки, що сказано "
    "про місто, і наведи одним реченням; (б) знайди в довіднику тариф міста; "
    "(в) порахуй вартість доставки як вагу, помножену на тариф. "
    "У кінці назви загальну вартість усіх шести посилок одним числом."
)

MIN_CALLS = 18


def cost_of_one(city, weight):
    """Витягує ціну і мін. вартість з тексту tariff_info і рахує через calc_price."""
    text = tariff_info(city)  # "Ціна: 18 грн/кг, термін: 2 днів, мінімальна вартість: 70 грн"
    
    # Регулярками витягуємо числа з тексту
    price_match = re.search(r"Ціна:\s*([\d.]+)", text)
    min_match = re.search(r"мінімальна вартість:\s*([\d.]+)", text)
    
    if not price_match or not min_match:
        raise ValueError(f"Не вдалося розпізнати тариф для міста {city}: {text}")
    
    price_per_kg = float(price_match.group(1))
    min_price = float(min_match.group(1))
    
    # calc_price повертає рядок (наприклад "270.0 грн" або "70 грн (спрацювала...)")
    result_text = calc_price(weight, price_per_kg, min_price)
    
    # Витягуємо перше число з результату
    return float(re.search(r"([\d.]+)", result_text).group(1))


def compute():
    """Сумарна вартість для всіх шести посилок."""
    total = 0.0
    for city, weight in ITEMS:
        total += cost_of_one(city, weight)
    return total


def save_task(total):
    """Записує питання, правильну відповідь і MIN_CALLS у файл long_task.json."""
    task = {
        "id": "L1",
        "question": QUESTION,
        "expected": format(round(total, 2), "g"),   # число як текст, без зайвих нулів
        "min_calls": MIN_CALLS,
    }
    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


if __name__ == "__main__":
    task = save_task(compute())
    print("Правильна відповідь:", task["expected"])
    print("Файл long_task.json записано")