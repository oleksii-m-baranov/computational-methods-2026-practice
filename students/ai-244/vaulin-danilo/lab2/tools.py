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


def book_info(title: str) -> str:
    with open("data/books.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["title"].lower() == title.lower():
                return (f"Примірників: {row['copies']}, "
                        f"термін видачі: {row['loan_days']} днів, "
                        f"штраф: {row['fine_per_day']} грн/день")
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

TOOLS = {
    "search_books": search_books,
    "book_info": book_info,
    "calculate": calculate,
}