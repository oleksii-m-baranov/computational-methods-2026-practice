"""Перевірки змісту аргументів (варіант 1 — Бібліотека)."""
import csv

with open("data/books.csv", encoding="utf-8") as f:
    TITLES = [row["title"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    if name == "book_info":
        if args.title not in TITLES:
            return (f"Помилка: назви книжки '{args.title}' немає в довіднику. "
                    f"Доступні: {', '.join(TITLES)}. "
                    "Виправ назву книжки (точно, як у каталозі) або повідом "
                    "користувачу, що даних про цю книжку немає.")
    return None
