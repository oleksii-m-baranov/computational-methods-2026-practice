
"""Генерація довгої задачі для лабораторної роботи №4."""

import csv
import json

from tools import search_books, book_info, calculate


def main():
    with open("data/books.csv", encoding="utf-8", newline="") as f:
        books = list(csv.DictReader(f))

    # Вибираємо шість книжок, які є в наявності.
    selected = [
        book for book in books
        if int(book["copies"]) > 0
    ][:6]

    if len(selected) < 6:
        raise ValueError("У каталозі недостатньо книжок.")

    # Кількість днів прострочення для кожної книжки.
    overdue_days = [3, 5, 7, 4, 6, 8]

    instructions = [
        "Виконай бібліотечну перевірку для шести книжок.",
        "Для КОЖНОЇ книжки обов'язково:",
        "1. Виклич search_books, щоб знайти книжку.",
        "2. Виклич book_info, щоб дізнатися штраф за день.",
        "3. Виклич calculate з operation='mul',",
        "   щоб обчислити штраф за прострочення.",
        "Не пропускай жодної книжки.",
        "Наприкінці наведи штраф для кожної книжки",
        "та загальну суму штрафів.",
        "",
        "Книжки та дні прострочення:",
    ]

    expected_items = []
    total = 0

    for index, (book, days) in enumerate(
        zip(selected, overdue_days), start=1
    ):
        title = book["title"]

        # Перевіряємо роботу реальних інструментів.
        search_result = search_books(title)
        info_result = book_info(title)

        if "Помилка:" in search_result or "Помилка:" in info_result:
            raise ValueError(f"Помилка інструмента для: {title}")

        if title not in search_result:
            raise ValueError(f"Книжку не знайдено: {title}")

        fine_per_day = int(book["fine_per_day"])

        fine = int(
            calculate(
                operation="mul",
                a=fine_per_day,
                b=days,
            )
        )

        total += fine

        instructions.append(
            f"{index}. {title} — прострочення {days} днів."
        )

        expected_items.append({
            "title": title,
            "overdue_days": days,
            "fine_per_day": fine_per_day,
            "fine": fine,
        })

    task = {
        "id": "long_books_01",
        "task": "\n".join(instructions),
        "min_calls": 18,
        "expected": {
            "items": expected_items,
            "total_fine": total,
        },
    }

    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)

    print("Створено long_task.json")
    print("Кількість книжок:", len(expected_items))
    print("Мінімум викликів:", task["min_calls"])
    print("Очікувана сума штрафів:", total, "грн")


if __name__ == "__main__":
    main()
