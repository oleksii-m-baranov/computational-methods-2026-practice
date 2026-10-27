"""Mock-база даних та інструменти агента."""
import json

# Імітація бази даних маршрутів
ROUTES_DB = {
    "історія": ["Замки Поділля: Кам'янець-Подільський", "Стара фортеця у Хотині"],
    "природа": ["Дністровський каньйон", "Подільські Товтри"]
}

# Довідник транспорту
TRANSPORT_DB = {
    "кам'янець-подільський": {"cost": 400, "duration_hours": 8},
    "хотин": {"cost": 350, "duration_hours": 7}
}


def search_routes(query: str) -> str:
    """Шукає маршрути за категорією або ключовим словом (максимально м'який пошук)."""
    q = query.lower().strip()

    # Шукаємо збіги за корнем слів (враховуємо українську/російську розкладку та опечатки)
    if "істор" in q or "истор" in q:
        routes = ROUTES_DB.get("історія", [])
        return json.dumps({"routes": routes}, ensure_ascii=False)

    if "природ" in q:
        routes = ROUTES_DB.get("природа", [])
        return json.dumps({"routes": routes}, ensure_ascii=False)

    # Перевірка на прямий збіг з категоріями
    for category, routes in ROUTES_DB.items():
        if category in q:
            return json.dumps({"routes": routes}, ensure_ascii=False)

    return f"За запитом '{query}' нічого не знайдено в корпусі маршрутів."


def transport_info(route: str) -> str:
    """Повертає інформацію про транспорт (з нечітким пошуком за назвою міста)."""
    r_clean = route.lower().strip()

    # Шукаємо ключ за частковим збігом підрядка
    for city, info in TRANSPORT_DB.items():
        # Перевірка на входження ключових фрагментів назви міста
        if city in r_clean or r_clean in city or city[:6] in r_clean:
            return json.dumps(info, ensure_ascii=False)

    return f"Маршрут '{route}' відсутній у довіднику транспорту."


def calc_budget(price_per_person: float, people: int, extra: float) -> float:
    """Обчислює загальний бюджет поїздки."""
    return (float(price_per_person) * int(people)) + float(extra)


# Словник доступних інструментів для диспетчера
TOOLS = {
    "search_routes": search_routes,
    "transport_info": transport_info,
    "calc_budget": calc_budget
}

if __name__ == "__main__":
    # Швидке самотестування функцій
    print("Z1 Тест:", search_routes("историчні місця"))
    print("Z2 Тест:", transport_info("Кам'янц-Подільський"))
    print("Z3 Тест:", calc_budget(price_per_person=400, people=3, extra=500))