"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів."""
import json
from tools import schedule_info, calc_calories

ITEMS = ["йога", "пілатес", "силове", "розтяжка", "кардіо", "кросфіт"]

QUESTION = (
    "Виконуй задачу покроково: на кожному кроці викликай інструменти лише для ОДНОГО заняття "
    "і чекай результату перед переходом до наступного. "
    "Шість занять: йога, пілатес, силове, розтяжка, кардіо, кросфіт. "
    "Для кожного: (а) знайди в корпусі вправи за словом 'тяга' або 'жим' або назвою заняття і наведи повний список; "
    "(б) знайди в розкладі годину початку заняття (число годин із поля 'час', наприклад для 18:00 це 18); "
    "(в) порахуй витрату калорій через інструмент calc_calories, підставивши як тривалість (minutes) "
    "знайдену годину початку помножену на 2 (тобто minutes = година * 2), вагу weight_kg = 70 та met = 5. "
    "У кінці назви сумарну витрату калорій за всі шість занять одним числом."
)

MIN_CALLS = 18


def calories_of_one(activity: str) -> float:
    info = schedule_info(activity)
    time_part = info.split("час: ")[1].split(",")[0]
    hour = int(time_part.split(":")[0])
    minutes = hour * 2
    res = calc_calories(minutes=minutes, weight_kg=70, met=5)
    return float(res.split()[0])


def compute() -> float:
    return sum(calories_of_one(act) for act in ITEMS)


def save_task(total: float):
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