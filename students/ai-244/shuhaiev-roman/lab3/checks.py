"""Перевірки змісту аргументів."""
import csv

with open("data/schedule.csv", encoding="utf-8") as f:
    ACTIVITIES = sorted({row["activity"] for row in csv.DictReader(f)})


def check_meaning(name, args):
    if name == "schedule_info":
        # ключ довідника: назва заняття має бути в розкладі
        if args.activity != args.activity.lower():
            return (f"Помилка: назва заняття '{args.activity}' має бути в нижньому регістрі. "
                    f"Виклич інструмент ще раз з '{args.activity.lower()}'.")
        if args.activity not in ACTIVITIES:
            return (f"Помилка: заняття '{args.activity}' немає в розкладі. "
                    "У розкладі лише заняття спортзалу (наприклад: йога, пілатес, силове, "
                    "розтяжка, кардіо). Виправ назву, якщо вона записана неточно, "
                    "або повідом користувачу, що такого заняття немає.")

    if name == "search_exercises":
        # одне-два слова, а не все питання користувача
        if len(args.query.split()) > 2:
            return (f"Помилка: запит '{args.query}' задовгий. "
                    "Передай одне-два слова: групу м'язів (спина, ноги, груди, руки, прес) "
                    "або рівень (початковий, середній, просунутий).")
    return None
