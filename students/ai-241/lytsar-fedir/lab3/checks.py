"""Перевірки змісту аргументів."""
import csv

# Завантажуємо список усіх рослин з нашого довідника
with open("data/fertilizer.csv", encoding="utf-8") as f:
    PLANTS = [row["plant"].lower() for row in csv.DictReader(f)]

def check_meaning(name, args):
    if name == "fertilizer_info":
        if args.plant.lower() not in PLANTS:
            return (f"Помилка: рослини '{args.plant}' немає в довіднику. "
                    "Знайди точну назву за допомогою search_plants або повідом користувачу, що даних про цю рослину немає.")
    return None