import json
from tools import search_recipes, product_info, scale_amount

ITEMS = [
    ("рис", 300, 4, 6),
    ("курка", 400, 4, 6),
    ("морква", 100, 4, 6),
    ("цибуля", 80, 4, 6),
    ("картопля", 500, 4, 6),
    ("молоко", 200, 2, 4)
]

QUESTION = (
    "Для кожної з шести позицій: рис 300 г (на 4 порції, треба на 6 порцій), "
    "курка 400 г (на 4 порції, треба на 6 порцій), морква 100 г (на 4 порції, треба на 6 порцій), "
    "цибуля 80 г (на 4 порції, треба на 6 порцій), картопля 500 г (на 4 порції, треба на 6 порцій), "
    "молоко 200 г (на 2 порції, треба на 4 порції). "
    "Для кожної: (а) знайди в корпусі рецептів, де використовується продукт, і наведи одним реченням; "
    "(б) знайди в довіднику калорійність на 100 г; "
    "(в) використай інструмент scale_amount для перерахунку кількості на нову кількість порцій і порахуй калорійність отриманої порції (нова кількість помножена на калорійність з довідника і поділена на 100). "
    "У кінці назви сумарну калорійність усіх шести позицій одним числом."
)

MIN_CALLS = 18

def get_cal_per_100(product_info_str):
    import re
    nums = re.findall(r'\d+(?:\.\d+)?', product_info_str)
    return float(nums[0]) if nums else 100.0

def compute_one(product, base_amt, base_srv, target_srv):
    info = product_info(product)
    cal_100 = get_cal_per_100(info)
    new_amt_str = scale_amount(base_amt, base_srv, target_srv)
    new_amt = float(new_amt_str)
    return (new_amt * cal_100) / 100.0

def compute():
    total = 0.0
    for product, b_amt, b_srv, t_srv in ITEMS:
        total += compute_one(product, b_amt, b_srv, t_srv)
    return total

def save_task(total):
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