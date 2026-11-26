"""Перевірки змісту аргументів."""
import csv

with open("data/tariffs.csv", encoding="utf-8") as f:
    ROWS = list(csv.DictReader(f))

CITIES = [row["city"].lower() for row in ROWS]


def check_meaning(name, args):
    if name == "tariff_info":
        if args.city.lower() not in CITIES:
            return (f"Помилка: міста '{args.city}' немає в довіднику тарифів. "
                    "Назва має бути українською в називному відмінку "
                    "(наприклад, Львів, а не Львов). "
                    "Виправ назву або повідом користувачу, що даних про це місто немає.")
    return None
