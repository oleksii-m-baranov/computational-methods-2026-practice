"""Перевірки змісту аргументів."""
import csv
import os

TRANSPORT_ROUTES = []
csv_path = "data/transport.csv"
if os.path.exists(csv_path):
    with open(csv_path, encoding="utf-8") as f:
        TRANSPORT_ROUTES = [row["route"].strip().lower() for row in csv.DictReader(f)]


def check_meaning(name, args):
    if name == "transport_info":
        if args.route.strip().lower() not in TRANSPORT_ROUTES:
            return (f"Помилка: маршруту '{args.route}' немає в довіднику. "
                    "Точну назву маршруту можна дізнатися за допомогою пошуку. "
                    "Виправ назву маршруту або повідом користувачу, що даних про цей маршрут немає.")
    return None