"""Перевірки змісту аргументів."""
import csv

with open("data/schedule.csv", encoding="utf-8") as f:
    # dict.fromkeys прибирає дублікати, зберігаючи порядок (заняття повторюються по днях)
    ACTIVITIES = list(dict.fromkeys(row["activity"] for row in csv.DictReader(f)))


def check_meaning(name, args):
    if name == "schedule_info":
        # ключ довідника: назва заняття має бути в schedule.csv
        if args.activity not in ACTIVITIES:
            return (f"Помилка: заняття '{args.activity}' немає в розкладі. "
                    f"Доступні: {', '.join(ACTIVITIES)}. "
                    "Виправ назву заняття або повідом користувачу, що даних про це заняття немає.")
    elif name == "search_exercises":
        # якщо модель передала ціле питання замість групи м'язів — це вже не пошук
        if len(args.query.split()) > 3:
            return ("Помилка: у 'query' забагато слів, схоже на ціле питання користувача. "
                    "Передай лише групу м'язів або рівень складності одним-двома словами, "
                    "наприклад 'спина' або 'початковий'.")
    return None