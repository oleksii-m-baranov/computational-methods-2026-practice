"""Перевірки змісту аргументів."""
import csv

with open("data/transport.csv", encoding="utf-8") as f:
    ROUTES = [row["route"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    if name == "transport_info":
        # порівняння без урахування регістру — так само, як у tools.transport_info
        if args.route.lower() not in [r.lower() for r in ROUTES]:
            # у довіднику 11 маршрутів (> 10), тому не перелічуємо їх усі,
            # а кажемо, як отримати правильну назву
            return (f"Помилка: маршруту '{args.route}' немає в довіднику транспорту. "
                    "Назва має збігатися з довідником дослівно, у називному відмінку. "
                    "Точну назву маршруту можна дізнатися інструментом search_routes. "
                    "Виправ назву або повідом користувачу, що даних про цей маршрут немає.")
    return None
