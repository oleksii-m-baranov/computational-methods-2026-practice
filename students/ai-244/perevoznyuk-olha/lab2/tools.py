import csv
import os


def search_routes(query: str) -> str:
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


def transport_info(route: str) -> str:
    with open("data/transport.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["route"].lower() == route.lower():
                return (f"Вартість проїзду: {row['price']} грн, "
                        f"у дорозі: {row['hours']} год, "
                        f"рейсів на день: {row['departures']}")
    return f"Маршруту '{route}' немає в довіднику."


def calc_budget(price_per_person: float, people: float,
                extra: float) -> str:
    return f"{round(price_per_person * people + extra, 2)} грн"

TOOLS = {
    "search_routes": search_routes,
    "transport_info": transport_info,
    "calc_budget": calc_budget
}