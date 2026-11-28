import csv
from pathlib import Path


def load_laptops():
    csv_path = Path(__file__).parent / "data" / "laptops.csv"

    with open(
        csv_path,
        encoding="utf-8-sig",
        newline=""
    ) as file:
        return list(csv.DictReader(file))


def check_meaning(name, arguments):
    if name == "laptop_info":
        model = arguments["model"].strip()
        laptops = load_laptops()

        available_models = [
            row["model"].strip().lower()
            for row in laptops
        ]

        if model.lower() not in available_models:
            return (
                False,
                f"Модель '{model}' відсутня в довіднику."
            )

    if name == "calc_installment":
        price = arguments["price"]
        months = arguments["months"]
        overpay_percent = arguments["overpay_percent"]

        if price <= 0:
            return False, "Ціна має бути більшою за нуль."

        if months < 1 or months > 60:
            return False, "Кількість місяців має бути від 1 до 60."

        if overpay_percent < 0 or overpay_percent > 100:
            return False, "Переплата має бути від 0 до 100 відсотків."

        laptops = load_laptops()

        known_prices = {
            float(row["price"])
            for row in laptops
        }

        if float(price) not in known_prices:
            return (
                False,
                f"Ціна {price} грн відсутня в довіднику. "
                "Виклич laptop_info для потрібної моделі "
                "та використай отриману ціну."
            )

    return True, "OK"
