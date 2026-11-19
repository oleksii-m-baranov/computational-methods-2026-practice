"""Тестування перевірок диспетчера для варіанта 7 (Подорожі)."""
from dispatcher import call_tool

cases = [
    # 1. Зламаний JSON (незакрита дужка)
    ("calc_budget", '{"price_per_person": 100, "people": 2, "extra": 0'),

    # 2. Неправильний тип (рядок замість числа)
    ("calc_budget", '{"price_per_person": "сто", "people": 2, "extra": 0}'),

    # 3. Відсутнє обов'язкове поле (пропущено price_per_person)
    ("calc_budget", '{"people": 2, "extra": 0}'),

    # 4. Вигадане поле (завдяки extra="forbid")
    ("calc_budget", '{"price_per_person": 100, "people": 2, "extra": 0, "unknown": 1}'),

    # 5. Неіснуючий інструмент
    ("delete_all", '{}'),

    # 6. Заборонена дія (є в TOOLS, але немає в config.ALLOWED)
    ("buy_ticket", '{"ticket_id": "123"}'),

    # 7. Значення немає в довіднику (перевірка в check_meaning)
    ("transport_info", '{"route": "Неіснуючий маршрут 999"}'),

    # 8. Значення поза межами (від'ємна ціна, порушення gt=0 у схемі Pydantic)
    ("calc_budget", '{"price_per_person": -100, "people": 2, "extra": 0}'),
]

print("=== ЗАПУСК ТЕСТІВ ДИСПЕТЧЕРА ===")
for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"Інструмент: {name}")
    print(f"Рівень: {level}")
    print(f"Повідомлення:\n{text}")
    print("-" * 50)