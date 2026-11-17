
"""Семантичні перевірки аргументів інструментів. ЛР3."""

import csv
from pathlib import Path


CSV_PATH = Path(__file__).parent / "data" / "laptops.csv"


def get_laptop_data(model):
    """Повертає дані ноутбука з початкового CSV-довідника."""
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["model"].strip().lower() == model.strip().lower():
                return row

    return None


def check_meaning(name, arguments, context=None):
    """
    Перевіряє зміст аргументів інструмента.

    context — додаткові дані, отримані агентом
    під час поточного завдання.
    """
    context = context or {}

    if name == "laptop_info":
        model = arguments["model"].strip()

        laptop = get_laptop_data(model)

        if laptop is None:
            return False, (
                f"Модель '{model}' відсутня в довіднику."
            )

    if name == "calc_installment":
        price = arguments["price"]
        months = arguments["months"]
        overpay_percent = arguments["overpay_percent"]

        if price < 0:
            return False, "Ціна не може бути від'ємною."

        if months <= 0:
            return False, (
                "Кількість місяців має бути більшою за нуль."
            )

        if overpay_percent < 0:
            return False, (
                "Переплата не може бути від'ємною."
            )

        # Додаткова семантична перевірка ЛР3:
        # ціна повинна походити з успішного laptop_info.
        verified_price = context.get("verified_price")

        if verified_price is None:
            return False, (
                "Перед розрахунком розстрочки необхідно "
                "отримати ціну через laptop_info. "
                "Виклич laptop_info, а потім calc_installment."
            )

        if abs(float(price) - float(verified_price)) > 0.01:
            return False, (
                f"Невідповідність ціни: передано {price} грн, "
                f"але laptop_info підтвердив "
                f"{verified_price} грн. "
                "Повтори розрахунок із підтвердженою ціною."
            )

    return True, "OK"
