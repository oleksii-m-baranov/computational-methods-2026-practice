import csv

from pathlib import Path


PRODUCTS_FILE = Path("data") / "products.csv"


def check_meaning(name: str, args: dict) -> str | None:
    """
    Перевіряє зміст аргументів інструмента.
    Повертає текст помилки або None, якщо перевірку пройдено.
    """

    if name == "product_info":
        product = args["product"].strip().casefold()

        with open(
            PRODUCTS_FILE,
            encoding="utf-8-sig",
            newline=""
        ) as file:
            reader = csv.DictReader(file)
            products = {
                (row.get("product") or "").strip().casefold()
                for row in reader
            }

        if product not in products:
            return f"Продукту '{args['product']}' немає в довіднику."

    elif name == "scale_amount":
        if args["amount"] <= 0:
            return "Кількість інгредієнта має бути більшою за нуль."

        if args["base_servings"] <= 0:
            return "Початкова кількість порцій має бути більшою за нуль."

        if args["target_servings"] <= 0:
            return "Потрібна кількість порцій має бути більшою за нуль."

    return None
