"""Функції інструментів та реєстр (Варіант 7)."""
import csv
import os


def search_routes(query: str) -> str:
    q = query.lower()
    found = []
    folder = "data/corpus"
    if not os.path.exists(folder):
        return f"Помилка: каталог '{folder}' не знайдено."

    for filename in sorted(os.listdir(folder)):
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath) and filename.endswith(".txt"):
            with open(filepath, encoding="utf-8") as f:
                text = f.read()
            if q in text.lower():
                found.append(text.split("\n")[0])
                
    if not found:
        return f"За запитом '{query}' нічого не знайдено."
    return " | ".join(found)


def transport_info(route: str) -> str:
    filepath = "data/transport.csv"
    if not os.path.exists(filepath):
        return f"Помилка: файл '{filepath}' не знайдено."

    with open(filepath, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["route"].lower() == route.lower():
                return (f"Вартість проїзду: {row['price']} грн, "
                        f"у дорозі: {row['hours']} год, "
                        f"рейсів на день: {row['departures']}")
    return f"Маршруту '{route}' немає в довіднику."


def calc_budget(price_per_person: float, people: float, extra: float) -> str:
    try:
        total = round(float(price_per_person) * float(people) + float(extra), 2)
        return f"{total} грн"
    except Exception as e:
        return f"Помилка обчислення: {e}"


TOOLS = {
    "search_routes": search_routes,
    "transport_info": transport_info,
    "calc_budget": calc_budget,
}