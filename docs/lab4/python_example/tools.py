import csv
import os


def search_books(query: str) -> str:
    q = query.lower()
    found = []
    folder = "data/corpus"
    for filename in sorted(os.listdir(folder)):
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            text = f.read()
        if q in text.lower():
            found.append(text.split("\n")[0])
    if not found:
        return f"За запитом '{query}' нічого не знайдено."
    return " | ".join(found)


def find_book_info(title: str) -> tuple[int, int, int]:
    with open("data/books.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["title"].lower() == title.lower():
                return int(row['copies']), int(row['loan_days']), int(row['fine_per_day'])
    return None

def book_info(title: str) -> str:
    book_information = find_book_info(title)
    if book_information:
        return (f"Примірників: {book_information[0]}, "
                f"термін видачі: {book_information[1]} днів, "
                f"штраф: {book_information[2]} грн/день")
    else:
        return f"Книжки '{title}' немає в довіднику."


def calculate(operation: str, a: float, b: float) -> str:
    ops = {
        "mul": lambda x, y: x * y,
        "add": lambda x, y: x + y,
        "sub": lambda x, y: x - y,
    }
    if operation not in ops:
        return f"Помилка: невідома операція '{operation}'. Доступні: mul, add, sub"
    return str(ops[operation](a, b))


def issue_book(title: str) -> str:
    return f"Книгу '{title}' видано"


TOOLS = {
    "search_books": search_books,
    "book_info": book_info,
    "calculate": calculate,
    "issue_book": issue_book,
}