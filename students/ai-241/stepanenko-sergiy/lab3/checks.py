"""Перевірки змісту аргументів інструментів."""

import csv


with open("data/laptops.csv", encoding="utf-8") as f:
    LAPTOPS = {
        row["model"]: row
        for row in csv.DictReader(f)
    }


def check_meaning(name, args):
    if name == "laptop_info":
        if args.model.lower() not in {
            model.lower() for model in LAPTOPS
        }:
            return (
                f"Помилка: моделі '{args.model}' немає в довіднику. "
                "Точну назву моделі можна отримати через search_laptops. "
                "Виправ назву або повідом користувачу, що даних немає."
            )

    return None