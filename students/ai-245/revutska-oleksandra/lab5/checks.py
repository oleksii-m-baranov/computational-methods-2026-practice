"""Перевірка змісту аргументів інструментів."""

import csv
from pathlib import Path


BOOKS_PATH = Path(__file__).resolve().parent / "data" / "books.csv"

with BOOKS_PATH.open(encoding="utf-8-sig", newline="") as f:
    BOOKS = {
        row["title"].strip().casefold()
        for row in csv.DictReader(f)
    }


def check_meaning(name, args):
    """Повертає текст помилки або None, якщо аргументи коректні."""

    if name == "book_info":
        title = args.title.strip()

        if title.casefold() not in BOOKS:
            return (
                f"Помилка: книжки '{title}' "
                "немає в каталозі. "
                "Точну назву можна знайти "
                "за допомогою search_books. "
                "Виправ назву або повідом користувачу."
            )

    return None