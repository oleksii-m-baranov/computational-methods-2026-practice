"""Перевірки змісту аргументів."""
import csv

with open("data/fertilizer.csv", encoding="utf-8") as f:
    PLANTS = [row["plant"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    if name == "fertilizer_info":
        if args.plant not in PLANTS:
            return (f"Помилка: рослини '{args.plant}' немає в довіднику підживлення. "
                    "Точну назву рослини можна дізнатися пошуком через інструмент search_plants. "
                    "Виклич search_plants або повідом користувачу, що даних про цю рослину немає.")
    if name == "calc_dose":
        if args.pot_liters * args.dose_ml_per_liter > 1000:
            return ("Помилка: загальна кількість добрива перевищує 1000 мл, що нереалістично для кімнатної рослини. "
                    "Перевір об'єм горщика та дозу на літр.")
    return None
