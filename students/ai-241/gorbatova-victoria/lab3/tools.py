"""Функції інструментів та реєстр (Варіант 7)."""

import csv
import os

def search_routes(query: str) -> str:
    filepath = "data/transport.csv"
    if not os.path.exists(filepath):
        return f"Помилка: файл '{filepath}' не знайдено."
    
    q = query.lower()
    found = []
    
    with open(filepath, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            r_lower = row["route"].lower()
            desc_lower = row.get("description", "").lower()
            
            if q in r_lower or q in desc_lower:
                found.append(row["route"])
                
    if not found:
        # Fallback: якщо нічого не знайдено за запитом
        return f"За запитом '{query}' нічого не знайдено."
        
    return " | ".join(found)


def route_info(route: str) -> str:
    filepath = "data/transport.csv"
    if not os.path.exists(filepath):
        return f"Помилка: файл '{filepath}' не знайдено."

    with open(filepath, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["route"].lower() == route.lower():
                return (f"Маршрут: {row['route']}, "
                        f"вартість проїзду: {row['price']} грн, "
                        f"час у дорозі: {row['hours']} год, "
                        f"рейсів на день: {row['departures']}")
                        
    return f"Маршруту '{route}' немає в довіднику."


def calculate_trip(price_per_person: float, people: int, extra: float) -> str:
    try:
        total = round(float(price_per_person) * int(people) + float(extra), 2)
        return f"Загальний бюджет поїздки: {total} грн"
    except Exception as e:
        return f"Помилка обчислення: {e}"


def buy_tickets(route: str, people: int) -> str:
    return "Вибачте, але купівля квитків через цей сервіс недоступна. Агент може лише підбирати маршрути та рахувати бюджет."


# Реєстр усіх доступних інструментів
TOOLS = {
    "search_routes": search_routes,
    "route_info": route_info,
    "calculate_trip": calculate_trip,
    "buy_tickets": buy_tickets,
}