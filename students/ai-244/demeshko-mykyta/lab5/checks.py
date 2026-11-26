"""Перевірки змісту аргументів."""
import csv

with open("data/fertilizer.csv", encoding="utf-8") as f:
    PLANTS = [row["plant"] for row in csv.DictReader(f)]

PLANTS_LOWER = {p.lower() for p in PLANTS}


def check_meaning(name, args):
    if name == "fertilizer_info":
        if args.plant.strip().lower() not in PLANTS_LOWER:
            return (
                f"Помилка: рослини '{args.plant}' немає в довіднику підживлення. "
                "У довіднику вказані повні назви видів (наприклад, 'Фікус Бенджаміна'). "
                "Точну назву рослини можна дізнатися інструментом search_plants."
            )

    if name == "search_plants":
        words = args.query.strip().split()
        if len(words) > 3:
            return (
                f"Помилка: пошуковий запит '{args.query}' занадто довгий ({len(words)} сл.). "
                "Допустимо 1–3 ключові слова українською. "
                "Скороти запит до одного основного слова і виклич search_plants ще раз."
            )

    return None