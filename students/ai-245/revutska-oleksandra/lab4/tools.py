
"""Інструменти бібліотечного агента для лабораторної роботи № 3."""

import csv
import os
import re


def search_books(query: str) -> str:
    """Пошук книжок за ключовими словами в корпусі."""

    folder = "data/corpus"

    if not os.path.isdir(folder):
        return "Помилка: каталог книжок не знайдено."

    query_words = re.findall(r"\w+", query.lower())

    if not query_words:
        return "Помилка: порожній пошуковий запит."

    found = []

    for filename in sorted(os.listdir(folder)):
        filepath = os.path.join(folder, filename)

        if not os.path.isfile(filepath):
            continue

        with open(filepath, encoding="utf-8") as f:
            text = f.read()

        if not text.strip():
            continue

        text_lower = text.lower()

        # Підрахунок кількості збігів із пошуковими словами
        matches = sum(
            1
            for word in query_words
            if word in text_lower
        )

        if matches > 0:
            title = text.splitlines()[0].strip()
            found.append((matches, title))

    if not found:
        return f"За запитом '{query}' нічого не знайдено."

    # Сортування за релевантністю
    found.sort(key=lambda item: (-item[0], item[1]))

    # Повернення назв знайдених книжок
    return " | ".join(
        title for _, title in found
    )


def book_info(title: str) -> str:
    """Отримання інформації про книжку за точною назвою."""

    filepath = "data/books.csv"

    if not os.path.isfile(filepath):
        return "Помилка: файл books.csv не знайдено."

    with open(filepath, encoding="utf-8") as f:
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
