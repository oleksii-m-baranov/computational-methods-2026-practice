"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py          (варіант формулювання з long_task_variant.txt або "v2")
         python make_task.py v3       (явно вибраний варіант)

Варіант 8 (обслуговування авто): шість робіт, для кожної — кількість деталей.
"""
import json
import os
import sys

# Беремо власні функції-інструменти з tools.py
from tools import calc_total, find_price

# Шість позицій: (назва роботи з прайсу, кількість деталей)
ITEMS = [("заміна масла", 4), ("заміна свічок запалювання", 4),
         ("заміна гальмівних колодок", 2), ("заміна гальмівних дисків", 2),
         ("заміна амортизаторів", 2), ("заміна акумулятора", 1)]

BASE = (
    "Для кожної з шести робіт: заміна масла (4 деталі), заміна свічок запалювання (4 деталі), "
    "заміна гальмівних колодок (2 деталі), заміна гальмівних дисків (2 деталі), "
    "заміна амортизаторів (2 деталі), заміна акумулятора (1 деталь). "
    "Для кожної: (а) знайди в корпусі регламентних робіт, як часто її виконують, і наведи одним реченням; "
    "(б) знайди в прайсі вартість роботи й вартість однієї деталі; "
    "(в) порахуй вартість роботи з урахуванням заданої кількості деталей. "
)
FINAL = "У кінці назви сумарну вартість усіх шести робіт одним числом."

# Варіанти формулювання. v1 - перша спроба: модель викликала 12 інструментів паралельно за один крок,
# пропустила calc_total і вигадала суму (attempt1/). v2 і v3 вимагають обробляти роботи по черзі.
QUESTIONS = {
    "v1": BASE + FINAL,
    "v2": BASE + (
        "Працюй строго по черзі: за один крок викликай рівно ОДИН інструмент і дочекайся його результату. "
        "Для кожної роботи порядок такий: search_service, потім price_info, потім calc_total з цінами з price_info. "
        "Лише після calc_total переходь до наступної роботи. Нічого не рахуй сам. "
    ) + FINAL,
    "v3": BASE + (
        "Опрацьовуй роботи по черзі, по одній роботі за крок: спершу виклич search_service і price_info "
        "для однієї роботи, наступним кроком - calc_total з цінами з price_info, і лише потім переходь до "
        "наступної роботи. Не викликай інструменти для кількох робіт одночасно і не рахуй сам. "
    ) + FINAL,
}

# Мінімум викликів інструментів для повного розв'язання: шість позицій по три інструменти.
MIN_CALLS = 18


def choose_variant():
    if len(sys.argv) > 1:
        return sys.argv[1]
    if os.path.exists("long_task_variant.txt"):
        with open("long_task_variant.txt", encoding="utf-8") as f:
            return f.read().strip()
    return "v2"


def cost_of_one(service, quantity):
    """Вартість однієї позиції: робота + деталь × кількість (через calc_total з tools.py)."""
    work_price, part_price, _ = find_price(service)              # ціни з довідника
    text = calc_total(work_price, part_price, quantity)          # "1400.0 грн"
    return float(text.split()[0])


def compute():
    """Правильна відповідь: сума по всіх шести позиціях. Рахуємо самі, без моделі."""
    total = 0.0
    for service, quantity in ITEMS:
        total = total + cost_of_one(service, quantity)
    return total


def save_task(total, variant):
    """Записує питання, правильну відповідь і MIN_CALLS у файл long_task.json."""
    task = {
        "id": "L1",
        "variant": variant,
        "question": QUESTIONS[variant],
        "expected": format(round(total, 2), "g"),   # число як текст, без зайвих нулів
        "min_calls": MIN_CALLS,
    }
    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


task = save_task(compute(), choose_variant())
print("Варіант формулювання:", task["variant"])
print("Правильна відповідь:", task["expected"])
print("Файл long_task.json записано")
