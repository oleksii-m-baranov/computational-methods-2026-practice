"""Перевірки змісту аргументів. Варіант 2 — Кулінарія."""

import csv
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"
PRODUCTS_FILE = DATA_DIR / "products.csv"


def load_products():
    """Завантажує назви продуктів із довідника."""

    with PRODUCTS_FILE.open(encoding="utf-8") as f:
        return {
            row["product"].strip().lower()
            for row in csv.DictReader(f)
        }


PRODUCTS = load_products()


def check_meaning(name, args):
    """
    Перевіряє зміст аргументів.

    Повертає:
    - None, якщо аргументи правильні;
    - повідомлення про помилку в іншому випадку.
    """

    if name == "product_info":

        product = args.product.strip().lower()

        if product not in PRODUCTS:

            return (
                f"Помилка: продукту '{args.product}' "
                "немає в довіднику. "
                "Використовуй точну назву продукту з довідника "
                "data/products.csv. "
                "Якщо правильна назва невідома, "
                "повідом користувачу, що даних немає."
            )

    return None
