"""Перевірки змісту аргументів."""
import csv

with open("data/transport.csv", encoding="utf-8") as f:
    ROUTES = [row["route"] for row in csv.DictReader(f)]

def check_meaning(name, args):
    if name == "route_info":
        target = getattr(args, "route", None)
        with open("data/transport.csv", encoding="utf-8") as f:
            routes = [row["route"] for row in csv.DictReader(f)]
        if target and target not in routes:
            return (f"Помилка: маршруту '{target}' немає в довіднику. "
                    f"Доступні маршрути: {', '.join(routes)}. "
                    f"Виправ назву або повідом користувачу.")
    return None