"""Перевірки змісту аргументів."""
import csv

with open("data/books.csv", encoding="utf-8-sig") as f:
    BOOKS = [row["title"].strip() for row in csv.DictReader(f)]

BOOKS_LOWER = {title.lower() for title in BOOKS}


def check_meaning(name, args):
    if name == "book_info":
        if args.title.strip().lower() not in BOOKS_LOWER:
            if len(BOOKS) <= 10:
                allowed_hint = f"Доступні назви книжок: {', '.join(BOOKS)}."
            else:
                allowed_hint = "Точну назву книжки можна дізнатися пошуком через інструмент search_books."
            return (
                f"Помилка: книжки '{args.title}' немає в довіднику. "
                f"{allowed_hint} "
                "Виправ назву книжки або повідом користувачу, що такої книжки немає."
            )

    if name == "search_books":
        if len(args.query.strip().split()) > 1:
            return (
                f"Помилка: запит '{args.query}' містить кілька слів, а пошук працює лише за одним словом. "
                "Допустимо передавати строго одне слово або його корінь (наприклад, 'фантаст' або 'легк'). "
                "Виклич search_books з одним словом."
            )

    return None