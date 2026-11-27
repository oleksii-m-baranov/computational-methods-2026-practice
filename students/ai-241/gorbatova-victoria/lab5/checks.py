"""Перевірки змісту аргументів."""
import csv

with open("data/transport.csv", encoding="utf-8") as f:
    ROUTES = [row["route"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    if name == "transport_info":
        target = getattr(args, "route", None)
        if target and target not in ROUTES:
            return (f"Помилка: маршруту '{target}' немає в довіднику. "
                    f"Доступні маршрути: {', '.join(ROUTES)}. "
                    f"Виправ назву або повідом користувачу.")
    return None