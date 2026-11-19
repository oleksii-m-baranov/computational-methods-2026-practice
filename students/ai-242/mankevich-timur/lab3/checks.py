"""Перевірки змісту аргументів."""
import csv
import difflib

# довідник продуктів: ключ, за яким product_info шукає рядок
with open("data/products.csv", encoding="utf-8") as f:
    PRODUCTS = [row["product"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    """Повертає текст помилки для моделі або None, якщо все гаразд."""
    if name == "product_info":
        if args.product.lower() not in PRODUCTS:
            # у довіднику 20 продуктів — усі не перелічуємо,
            # а підказуємо найближчі за написанням (рису -> рис)
            similar = difflib.get_close_matches(args.product.lower(), PRODUCTS,
                                                n=3, cutoff=0.6)
            hint = ""
            if similar:
                hint = f" Схожі назви в довіднику: {', '.join(similar)}."
            return (f"Помилка: продукту '{args.product}' немає в довіднику."
                    f"{hint} Назва має бути в називному відмінку однини "
                    "(наприклад, «рис», а не «рису»). "
                    "Виправ назву або повідом користувачу, "
                    "що даних про цей продукт немає.")
    return None
