"""Перевірки змісту аргументів."""

import csv

with open("data/books.csv", encoding="utf-8") as f:
    BOOKS = [
        row["title"].strip().lower()
        for row in csv.DictReader(f)
    ]

def check_meaning(name, args):
    if name == "book_info":
        if args.title.strip().lower() not in BOOKS:
            return (
                f"Помилка: книжки '{args.title}' немає в довіднику бібліотеки. "
                "Спочатку знайди точну назву книжки за допомогою search_books "
                "або повідом користувачу, що даних немає."
            )

    return None
