"""Semantic meaning checks for tool arguments. Variant 11 (Library)."""
import csv
import difflib

with open("data/books.csv", encoding="utf-8") as f:
    TITLES = [row["title"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    """Check semantic validity of arguments against domain database.
    Returns 3-part error string or None if valid."""
    if name == "book_info":
        if args.title not in TITLES:
            matches = difflib.get_close_matches(args.title, TITLES, n=2, cutoff=0.5)
            hint = f" Можливо, мається на увазі: {', '.join(matches)}." if matches else ""
            return (
                f"Помилка: книжки '{args.title}' немає в довіднику books.csv.{hint} "
                "Точну назву можна дізнатися пошуком через search_books. "
                "Виправ назву книжки або повідом користувачу, що даних про неї немає."
            )
    return None
