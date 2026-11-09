""" Перевірки змісту аргументів.
import csv

with open("data/cities.csv", encoding="utf-8") as f:
    CITIES = [row["city"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    if name == "get_weather":
        if args.city not in CITIES:
            return (f"Помилка: міста '{args.city}' немає в довіднику. "
                    f"Доступні: {', '.join(CITIES)}. "
                    "Виправ назву міста або повідом користувачу, що даних про це місто немає.")
    return None"""

import csv

with open("data/transport.csv", encoding="utf-8") as f:
    ROUTES = [row["route"] for row in csv.DictReader(f)]

def check_meaning(name, args):
    if name == "transport_info":
        if args.route not in ROUTES:
            return (f"Помилка: маршруту '{args.route}' немає в довіднику. "
                    f"Доступні: {', '.join(ROUTES)}. "
                    "Виправ назву маршруту або повідом користувачу, що даних про цей маршрут немає.")
    return None


