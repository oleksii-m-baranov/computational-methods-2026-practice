import csv
import os


def search_books(query: str) -> str:
    """Пошук книжки в корпусі коротких анотацій (data/corpus/)."""
    q = query.lower()
    found = []
    folder = "data/corpus"
    if not os.path.exists(folder):
        return f"За запитом '{query}' нічого не знайдено."
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".txt"):
            continue
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            text = f.read()
        if q in text.lower():
            found.append(text.split("\n")[0].strip())
    if not found:
        return f"За запитом '{query}' нічого не знайдено."
    return " | ".join(found)


def book_info(title: str) -> str:
    """Отримання умов видачі книги з довідника (data/books.csv)."""
    csv_path = "data/books.csv"
    if not os.path.exists(csv_path):
        return f"Книжки '{title}' немає в довіднику."
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["title"].strip().lower() == title.strip().lower():
                return (f"Примірників: {row['copies']}, "
                        f"термін видачі: {row['loan_days']} днів, "
                        f"штраф: {row['fine_per_day']} грн/день")
    return f"Книжки '{title}' немає в довіднику."


def calculate(operation: str, a: float, b: float) -> str:
    """Арифметичні обчислення: mul — множення, add — додавання, sub — віднімання."""
    ops = {
        "mul": lambda x, y: x * y,
        "add": lambda x, y: x + y,
        "sub": lambda x, y: x - y,
    }
    if operation not in ops:
        return f"Помилка: невідома операція '{operation}'. Доступні: mul, add, sub"
    return str(ops[operation](a, b))


def issue_book(title: str) -> str:
    """Дія бронювання/видачі (заборонена агенту в ЛР3-4)."""
    return f"Книгу '{title}' видано читачеві."


TOOLS = {
    "search_books": search_books,
    "book_info": book_info,
    "calculate": calculate,
    "issue_book": issue_book,
}
