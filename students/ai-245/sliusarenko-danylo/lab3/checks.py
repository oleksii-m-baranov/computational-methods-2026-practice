"""Перевірки змісту аргументів."""
import csv

with open("data/schedule.csv", encoding="utf-8") as f:
    ACTIVITIES = sorted({row["activity"].strip().lower() for row in csv.DictReader(f)})


def check_meaning(name, args):
    if name == "schedule_info":
        act = args.activity.strip().lower()
        if act not in ACTIVITIES:
            return (
                f"Помилка: заняття '{args.activity}' немає в розкладі. "
                f"Доступні заняття: {', '.join(ACTIVITIES)}. "
                "Виправ назву заняття або повідом користувачу, що такого заняття немає."
            )
    return None