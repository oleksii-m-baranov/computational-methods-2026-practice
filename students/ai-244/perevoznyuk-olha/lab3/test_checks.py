from dispatcher import call_tool

cases = [
    # Некоректний JSON
    ("search_routes", '{"query": "історія"'),
    # Неправильний тип аргументу: query має бути рядком
    ("search_routes", '{"query": 123}'),
    # Не передано обов'язкове поле query
    ("search_routes", '{}'),
    # Передано невідоме поле
    ("search_routes", '{"query": "історія", "extra": true}'),
    # Інструмента з такою назвою не існує
    ("delete_all", '{}'),
    # Інструмент є, але його виклик не дозволено
    ("buy_ticket", '{"booking_id": "ABC123"}'),
    # Маршруту немає в довіднику
    ("transport_info", '{"route": "Київ — Львів"}'),
    # Успішний пошук маршрутів
    ("search_routes", '{"query": "історія"}'),
    # Успішний пошук інформації про маршрут
    ("transport_info", '{"route": "Зелені Карпати — Яремче"}'),
    # Успішне обчислення бюджету поїздки
    ("calc_budget", '{"price_per_person": 225, "people": 3, "extra": 500}'),
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")
