"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py      (з каталогу lab4, де лежить data/)

Варіант 12 (= 2: кулінарія). Шість продуктів із рецептів. Для кожного продукту:
  (а) search_recipes - знайти в корпусі рецепт з цим продуктом;
  (б) product_info   - знайти в довіднику калорійність на 100 г;
  (в) scale_amount   - порахувати калорійність порції заданої ваги:
                       калорійність на 100 г * вага / 100.
Підсумок: сумарна калорійність шести порцій, ккал.

Скрипт рахує правильну відповідь тими самими інструментами, що й агент, без моделі.
Якщо слово для пошуку в корпусі нічого не знаходить, він підбирає інше й пише про це.
"""
import json
import re

from tools import product_info, scale_amount, search_recipes

# Шість продуктів: (продукт, вага порції в грамах). Ваги кратні 20 г,
# тож вага/100 виходить числом з однією цифрою після коми.
ITEMS = [
    ("курка", 200),
    ("рис", 150),
    ("сметана", 100),
    ("сир", 120),
    ("масло", 20),
    ("борошно", 180),
]

# Мінімум викликів інструментів для повного розв'язання: шість продуктів по три інструменти.
MIN_CALLS = 18


def kcal_per_100g(product):
    """Калорійність на 100 г з відповіді product_info: «Калорійність: 190 ккал на 100 г, ...»."""
    text = product_info(product)
    match = re.search(r"Калорійність: (\d+)", text)
    if not match:
        raise SystemExit(f"У довіднику немає продукту '{product}': {text}")
    return int(match.group(1))


def cost_of_one(product, grams):
    """Калорійність порції: scale_amount(ккал на 100 г, 1, вага/100). Рахуємо як агент."""
    kcal = kcal_per_100g(product)
    return float(scale_amount(kcal, 1, grams / 100))


def compute():
    """Правильна відповідь: сума по всіх шести продуктах."""
    total = 0.0
    for product, grams in ITEMS:
        total = total + cost_of_one(product, grams)
    return total


def build_question():
    """Текст питання за шаблоном лабораторної: перелік, (а), (б), (в), підсумок."""
    items = "; ".join(f"{product} {grams} г" for product, grams in ITEMS)
    return (
        f"Для кожного з шести продуктів (з вагою порції): {items}. "
        "Для кожного: (а) знайди в корпусі рецептів страву з цим продуктом і наведи її назву "
        "одним реченням; (б) знайди в довіднику калорійність продукту на 100 г; "
        "(в) порахуй калорійність порції за допомогою scale_amount: amount = калорійність "
        "на 100 г, base_servings = 1, target_servings = вага порції в грамах, поділена на 100 "
        "(наприклад, для 150 г це 1.5). "
        "Кожне множення виконуй окремим викликом scale_amount, самостійно не рахуй. "
        "У кінці назви сумарну калорійність усіх шести порцій одним числом у ккал."
    )


def save_task(total):
    """Записує питання, правильну відповідь і MIN_CALLS у файл long_task.json.

    Ключ reference - довідка для ручної перевірки логів (чи не вигадала модель числа); агент її не бачить.
    """
    reference = [{
        "product": product,
        "grams": grams,
        "search": f"{product} -> {search_recipes(product)}",
        "product_info": product_info(product),
        "kcal": cost_of_one(product, grams),
    } for product, grams in ITEMS]
    task = {
        "id": "L1",
        "question": build_question(),
        "expected": format(round(total, 2), "g"),   # число як текст, без зайвих нулів
        "min_calls": MIN_CALLS,
        "reference": reference,
    }
    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


for product, _ in ITEMS:
    if search_recipes(product).startswith("За запитом"):
        print(f"УВАГА: за словом '{product}' у корпусі нічого не знайдено")

task = save_task(compute())
print("Питання:", task["question"])
print("Правильна відповідь:", task["expected"])
print("Файл long_task.json записано")
