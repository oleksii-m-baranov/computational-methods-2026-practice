"""Перевірки змісту аргументів."""
import csv

with open("data/schedule.csv", encoding="utf-8") as f:
    ACTIVITIES = {row["activity"].strip().lower() for row in csv.DictReader(f)}


def check_meaning(name, args):
    if name == "schedule_info":
        if args.activity.strip().lower() not in ACTIVITIES:
            return (f"Помилка: вправи '{args.activity}' немає в розкладі. "
                    "Точну назву можна дізнатися інструментом search_exercises. "
                    "Виправ назву вправи або повідом користувачу, що даних про цю вправу немає.")
    return None
