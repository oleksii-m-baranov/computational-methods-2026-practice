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
            # лаб. 4: повертаємо весь опис маршруту (назва, тип, опис, тривалість), а не лише назву,
            # щоб модель могла навести, що сказано про місце. Результат не скорочуємо.
            found.append(" ".join(line.strip() for line in text.strip().split("\n")))
    if not found:
        return f"За запитом '{query}' нічого не знайдено."
    return " | ".join(found)


def find_route_info(route: str):
    """Рядок довідника транспорту для маршруту: (ціна, години, рейси) або None."""
    with open("data/transport.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["route"].lower() == route.lower():
                return float(row["price"]), float(row["hours"]), int(row["departures"])
    return None


def transport_info(route: str) -> str:
    info = find_route_info(route)
    if info:
        price, hours, departures = info
        return (f"Вартість проїзду: {price:g} грн, "
                f"у дорозі: {hours:g} год, "
                f"рейсів на день: {departures}")
    return f"Маршруту '{route}' немає в довіднику."


def calc_budget(price_per_person: float, people: float,
                extra: float) -> str:
    return f"{round(price_per_person * people + extra, 2)} грн"


def buy_ticket(route: str) -> str:
    return f"Квиток на маршрут '{route}' куплено"      # заглушка: агентові ця дія заборонена


TOOLS = {
    "search_routes": search_routes,
    "transport_info": transport_info,
    "calc_budget": calc_budget,
    "buy_ticket": buy_ticket,
}
