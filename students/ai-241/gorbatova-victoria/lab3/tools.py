"""Функції інструментів та реєстр (Варіант 7)."""

import csv
import os


def search_routes(query: str) -> str:
    filepath = "data/transport.csv"
    if not os.path.exists(filepath):
        return f"Помилка: файл '{filepath}' не знайдено."
    
    q = query.lower()
    found = []
    
    # Синоніми для гнучкого пошуку у 7-му варіанті
    keywords = {
        "гор": ["яремче", "синевир", "дземброня", "карпати"],
        "море": ["затока", "одеса"],
        "істор": ["кам'янець", "хотин", "львів"],
        "винар": ["закарпатська винарня"]
    }
    
    active_q = q
    for key, values in keywords.items():
        if key in q:
            active_q = "" # знімаємо жорсткий фільтр, щоб перевірити ключові слова
            
    with open(filepath, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            r_lower = row["route"].lower()
            desc_lower = row.get("description", "").lower()
            
            if active_q == "":
                # якщо був запит на категорію (наприклад, гори), шукаємо відповідні маршрути
                if any(v in r_lower for key, values in keywords.items() if key in q for v in values):
                    found.append(row["route"])
            elif q in r_lower or q in desc_lower:
                found.append(row["route"])
                
    if not found:
        # Fallback: якщо зовсім нічого не знайшлося, показуємо всі доступні
        with open(filepath, encoding="utf-8") as f:
            all_routes = [row["route"] for row in csv.DictReader(f)]
        return f"За запитом '{query}' нічого не знайдено. Доступні маршрути: {', '.join(all_routes)}"
        
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


TOOLS = {
    "search_routes": search_routes,
    "route_info": route_info,
    "calculate_trip": calculate_trip,
}