"""Перевірки змісту аргументів (Варіант 1 — Бібліотека)."""
import csv

with open("data/books.csv", encoding="utf-8") as f:
    TITLES = [row["title"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    """Перевірка смислових обмежень (рівень meaning)."""
    if name == "book_info":
        if args.title not in TITLES:
            return (
                f"Помилка: назви книги '{args.title}' немає в довіднику. "
                f"Доступні: {', '.join(TITLES)}. "
                "Виправ назву книги або скористайся search_books для пошуку точної назви."
            )

    if name == "calculate":
        if args.operation == "sub" and args.a < args.b:
            return (
                f"Помилка: операція віднімання a - b призведе до від'ємного значення ({args.a} < {args.b}). "
                "Дні або штрафи не можуть бути від'ємними."
            )

    return None
