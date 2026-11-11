"""Перевірки змісту аргументів."""
import csv

with open("data/books.csv", encoding="utf-8") as f:
    BOOKS = [row["title"].lower() for row in csv.DictReader(f)]


def check_meaning(name, args):
    if name == "book_info":
        if args.title.lower() not in BOOKS:
            return (
                f"Помилка: книжки '{args.title}' немає в довіднику. "
                "Потрібна точна назва книжки з каталогу, яку можна дізнатися інструментом search_books. "
                "Виклич search_books для пошуку точної назви або повідом користувачу, що даних про цю книжку немає."
            )
    if name == "calculate":
        if args.operation == "sub" and args.a < args.b:
            return (
                f"Помилка: результат віднімання ({args.a} - {args.b}) буде від'ємним. "
                "У розрахунках бібліотеки перший операнд при відніманні має бути не меншим за другий (a >= b). "
                "Перевір порядок операндів і виклич інструмент ще раз."
            )
    return None

