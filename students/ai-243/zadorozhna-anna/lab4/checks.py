"""Перевірки змісту аргументів."""
import csv


def _load_products():
    """Завантажує назви продуктів із довідника."""
    products = []
    with open("data/products.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            products.append(row["product"].strip().lower())
    return products


PRODUCTS = _load_products()


def check_meaning(name, args):
    """Перевіряє зміст аргументів.
    Повертає текст помилки для моделі або None, якщо все гаразд.
    """
    if name == "product_info":
        if args.product.strip().lower() not in PRODUCTS:
            return (
                f"Помилка: продукту '{args.product}' немає в довіднику. "
                "Точну назву можна дізнатися пошуком або переглянути список продуктів. "
                "Виправ назву продукту або повідом користувачу, що даних про цей продукт немає."
            )
    return None