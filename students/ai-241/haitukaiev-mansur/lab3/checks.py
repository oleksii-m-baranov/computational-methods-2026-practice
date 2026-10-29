"""Перевірки змісту аргументів."""
import csv

with open("data/schedule.csv", encoding="utf-8") as f:
    ACTIVITIES = list(dict.fromkeys(row["activity"] for row in csv.DictReader(f)))

def check_meaning(name, args):
    if name == "schedule_info":
        if args.activity.lower() not in [a.lower() for a in ACTIVITIES]:
            return (f"Помилка: заняття '{args.activity}' немає в розкладі. "
                    f"Доступні: {', '.join(ACTIVITIES)}. "
                    "Виправ назву заняття або повідом користувачу, що такого заняття немає.")
    return None