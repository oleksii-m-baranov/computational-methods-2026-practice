"""Перевірки змісту аргументів."""
import csv


with open("data/books.csv", encoding="utf-8") as f:
    TITLES = [row["title"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    if name == "book_info":
        if args.title not in TITLES:
            return (f"Помилка: назви книги '{args.title}' немає в довіднику. "
                    f"Доступні: {', '.join(TITLES)}. "
                    "Виправ назву книги або повідом користувачу, що даних про цю книгу немає.")
    return None