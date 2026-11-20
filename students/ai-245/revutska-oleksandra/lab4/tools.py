

"""Інструменти бібліотечного агента для лабораторної роботи № 4."""

import csv
import os


def search_books(query: str) -> str:
    """Пошук книжок за назвою в каталозі books.csv."""

    filepath = "data/books.csv"

    if not os.path.isfile(filepath):
        return "Помилка: файл books.csv не знайдено."

    query = query.strip().casefold()

    if not query:
        return "Помилка: порожній пошуковий запит."

    found = []

    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            title = row["title"].strip()

            if query in title.casefold():
                found.append(title)

    if not found:
        return f"За запитом '{query}' нічого не знайдено."

    return " | ".join(found)


def book_info(title: str) -> str:
    """Отримання інформації про книжку за точною назвою."""

    filepath = "data/books.csv"

    if not os.path.isfile(filepath):
        return "Помилка: файл books.csv не знайдено."

    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            book_title = row["title"].strip()

            if book_title.casefold() == title.strip().casefold():
                return (
                    f"Назва: {book_title}, "
                    f"Примірників: {row['copies']}, "
                    f"термін видачі: {row['loan_days']} днів, "
                    f"штраф: {row['fine_per_day']} грн/день"
                )

    return f"Книжки '{title}' немає в довіднику."


def calculate(operation: str, a: float, b: float) -> str:
    """Виконання арифметичних обчислень."""

    operations = {
        "mul": lambda x, y: x * y,
        "add": lambda x, y: x + y,
        "sub": lambda x, y: x - y,
    }

    if operation not in operations:
        return (
            f"Помилка: невідома операція '{operation}'. "
            "Доступні: mul, add, sub."
        )

    result = operations[operation](a, b)

    if result == int(result):
        return str(int(result))

    return str(result)


def issue_book(title: str) -> str:
    """Демонстраційна заборонена дія — видача книжки."""

    return "Книжку видано"


# Реєстр інструментів
TOOLS = {
    "search_books": search_books,
    "book_info": book_info,
    "calculate": calculate,
    "issue_book": issue_book,
}
