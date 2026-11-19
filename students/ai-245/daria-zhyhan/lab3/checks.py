"""Перевірки змісту аргументів."""

import csv

with open("data/fertilizer.csv", encoding="utf-8") as f:
    PLANTS_IN_CSV = {row["plant"].lower() for row in csv.DictReader(f)}


def check_meaning(name, args):
    if name == "fertilizer_info":
        if args.plant.lower() not in PLANTS_IN_CSV:
            return (f"Помилка: рослини '{args.plant}' немає в довіднику підживлення. "
                    "Точну назву рослини можна перевірити інструментом search_plants "
                    "або повідомити користувачу, що даних про підживлення цієї рослини немає.")
    return None