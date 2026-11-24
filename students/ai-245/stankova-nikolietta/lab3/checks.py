"""Перевірки змісту аргументів."""

import csv

with open("data/fertilizer.csv", encoding="utf-8") as f:
    PLANTS = [row["plant"] for row in csv.DictReader(f)]


def check_meaning(name, args):

    if name == "fertilizer_info":

        if args.plant not in PLANTS:
            return (
                f"Помилка: рослини '{args.plant}' немає в довіднику. "
                "Використай точну назву рослини або повідом користувачу, що даних немає."
            )

    return None
