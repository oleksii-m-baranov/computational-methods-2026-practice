"""Перевірки змісту аргументів."""
import csv

with open("data/tariffs.csv", encoding="utf-8") as f:
    ROWS = list(csv.DictReader(f))

CITIES = [row["city"].lower() for row in ROWS]
TARIFFS = {(float(r["price_per_kg"]), float(r["min_price"])) for r in ROWS}


def check_meaning(name, args):
    if name == "tariff_info":
        if args.city.lower() not in CITIES:
            return (f"Помилка: міста '{args.city}' немає в довіднику тарифів. "
                    "Назва має бути українською в називному відмінку "
                    "(наприклад, Львів, а не Львов). "
                    "Виправ назву або повідом користувачу, що даних про це місто немає.")
    if name == "calc_price":
        if (args.price_per_kg, args.min_price) not in TARIFFS:
            return (f"Помилка: ціна за кг {args.price_per_kg} і мінімальна вартість "
                    f"{args.min_price} не збігаються з жодним тарифом у довіднику. "
                    "Не вигадуй ці значення: спочатку виклич tariff_info для міста "
                    "призначення й візьми значення з його результату.")
    return None
