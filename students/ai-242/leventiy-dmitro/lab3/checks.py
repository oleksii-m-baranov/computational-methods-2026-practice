"""Перевірки змісту аргументів."""
import csv

with open("data/vaccines.csv", encoding="utf-8") as f:
    VACCINES = [row["vaccine"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    if name == "vaccine_info":
        if args.vaccine.lower() not in VACCINES:
            return (f"Помилка: щеплення '{args.vaccine}' немає в довіднику. "
                    f"Доступні: {', '.join(VACCINES)}. "
                    "Виправ назву щеплення або повідом користувачу, що даних про це щеплення немає.")
    return None
