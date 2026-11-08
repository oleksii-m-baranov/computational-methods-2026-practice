"""Перевірки змісту аргументів."""
import csv

with open("data/transport.csv", encoding="utf-8") as f:
    ROWS = list(csv.DictReader(f))

ROUTES = [row["route"] for row in ROWS]
PRICES = {float(row["price"]) for row in ROWS}


def check_meaning(name, args):
    if name == "transport_info":
        # ключ довідника: маршрутів більше десяти, тому не перелічуємо всі
        if args.route.lower() not in [r.lower() for r in ROUTES]:
            return (f"Помилка: маршруту '{args.route}' немає в довіднику транспорту. "
                    "Точну назву маршруту можна дізнатися інструментом search_routes. "
                    "Виправ назву або повідом користувачу, що даних про цей маршрут немає.")

    if name == "calc_budget":
        # ціна має бути взята з довідника, а не вигадана
        if args.price_per_person not in PRICES:
            return (f"Помилка: вартості проїзду {args.price_per_person:g} грн немає в довіднику. "
                    "Спершу дізнайся вартість інструментом transport_info "
                    "і передай її в price_per_person без змін.")
    return None
