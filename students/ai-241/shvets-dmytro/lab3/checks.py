"""Перевірки змісту аргументів (варіант 2: кулінарія)."""
import csv
import difflib

with open("data/products.csv", encoding="utf-8") as f:
    PRODUCTS = [row["product"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    """Повертає текст помилки для моделі або None, якщо все гаразд.
    args — уже перевірений Pydantic об'єкт."""

    if name == "product_info":
        # ключ довідника: продукт має бути в data/products.csv
        product = args.product.lower()
        if product not in PRODUCTS:
            similar = difflib.get_close_matches(product, PRODUCTS, n=3, cutoff=0.6)
            hint = (f" Схожі назви: {', '.join(similar)}." if similar else "")
            return (f"Помилка: продукту '{args.product}' немає в довіднику.{hint} "
                    "Допустима назва — один продукт в називному відмінку однини, "
                    "малими літерами (наприклад, 'рис', 'морква'). "
                    "Виправ назву або повідом користувачу, що даних про цей продукт немає.")

    if name == "search_recipes":
        # пошук працює за підрядком: фраза з трьох і більше слів нічого не знайде
        if len(args.query.split()) > 2:
            return (f"Помилка: запит '{args.query}' задовгий для пошуку. "
                    "Допустимо один інгредієнт, тип страви або спосіб приготування "
                    "(одне-два слова). "
                    "Виклич пошук ще раз із коротким запитом, наприклад, 'курка' або 'суп'.")

    return None
