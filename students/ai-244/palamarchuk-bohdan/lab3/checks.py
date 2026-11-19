"""Перевірки змісту аргументів."""
import csv

with open("data/schedule.csv", encoding="utf-8") as f:
    ACTIVITIES = []
    for row in csv.DictReader(f):
        name = row["activity"].lower()
        if name not in ACTIVITIES:
            ACTIVITIES.append(name)


def check_meaning(name, args):
    if name == "schedule_info":
        if args.activity.lower() not in ACTIVITIES:
            return (f"Помилка: заняття '{args.activity}' немає в розкладі. "
                    f"Доступні: {', '.join(ACTIVITIES)}. "
                    "Виправ назву заняття або повідом користувачу, "
                    "що такого заняття немає.")
    return None
