"""Семантичні перевірки аргументів інструментів."""

import csv
import math


def check_meaning(name: str, args: dict) -> str | None:
    """Перевіряє зміст аргументів інструмента."""

    if name == "product_info":
        product = args["product"]

        with open("data/products.csv", encoding="utf-8") as file:
            products = {
                row["product"].casefold()
                for row in csv.DictReader(file)
            }

        if product.casefold() not in products:
            return (
                f"Продукту '{product}' немає в довіднику. "
                "Використовуй назву продукту з products.csv."
            )

    elif name == "scale_amount":
        amount = args["amount"]
        base_servings = args["base_servings"]
        target_servings = args["target_servings"]

        scaled_amount = amount * target_servings / base_servings

        if not math.isfinite(scaled_amount):
            return "Помилка: результат перерахунку кількості некоректний."

    elif name == "place_order":
        return "Заборонена дія: замовлення продуктів недоступне."

    return None
