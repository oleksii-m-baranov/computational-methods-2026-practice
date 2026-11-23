"""Перевірки змісту аргументів."""
import csv

with open("data/fertilizer.csv", encoding="utf-8") as f:
    PLANTS = sorted(set(row["plant"] for row in csv.DictReader(f)))
    PLANTS_LOWER = {p.lower(): p for p in PLANTS}
    VALID_DOSES = sorted(set(float(row["dose_ml_per_liter"]) for row in csv.DictReader(open("data/fertilizer.csv", encoding="utf-8"))))


def check_meaning(name, args):
    if name == "fertilizer_info":
        if args.plant.lower() not in PLANTS_LOWER:
            return (f"Помилка: рослини '{args.plant}' немає в довіднику підживлення. "
                    "Точну назву рослини можна дізнатися пошуком через інструмент search_plants. "
                    "Виклич search_plants або повідом користувачу, що даних про цю рослину немає.")
    elif name == "calc_dose":
        if args.dose_ml_per_liter not in VALID_DOSES:
            return (f"Помилка: доза {args.dose_ml_per_liter} мл/л не відповідає жодному значенню з довідника "
                    f"(допустимі значення з довідника: {VALID_DOSES}). "
                    "Спочатку отримай точну дозу з довідника через fertilizer_info.")
    return None