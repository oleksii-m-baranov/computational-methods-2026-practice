"""Перевірки змісту аргументів."""
import csv

with open("data/schedule.csv", encoding="utf-8") as f:
    ACTIVITIES = [row["activity"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    if name == "schedule_info":
        if args.title not in ACTIVITIES:
            return (f"Помилка: вправи '{args.title}' немає в розкладі. "
                    "Точну назву можна дізнатися інструментом search_exercises. "
                    "Виправ назву вправи або повідом користувачу, що даних про цю вправу немає.")
    return None