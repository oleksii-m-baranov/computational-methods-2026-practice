"""Тестування ланцюжка перевірок диспетчера (Таблиця 2)."""
from dispatcher import call_tool

cases = [
    # 1. Зламаний JSON
    ("calculate_trip", '{"days": 3, "cost_per_day": 500'),
    
    # 2. Неправильний тип (рядок замість числа)
    ("calculate_trip", '{"days": "три", "cost_per_day": 500}'),
    
    # 3. Відсутнє обов'язкове поле (немає days)
    ("calculate_trip", '{"cost_per_day": 500}'),
    
    # 4. Вигадане поле (extra="forbid")
    ("calculate_trip", '{"days": 3, "cost_per_day": 500, "extra_field": 100}'),
    
    # 5. Неіснуючий інструмент
    ("delete_all", '{}'),
    
    # 6. Заборонена дія (є в TOOLS, але немає в ALLOWED)
    ("buy_ticket", '{"ticket_id": "123"}'),
    
    # 7. Значення немає в довіднику (перевірка змісту / meaning)
    ("search_routes", '{"query": "НеіснуючеМісто123"}'),
    
    # 8. Значення поза межами (schema, наприклад days > 30)
    ("calculate_trip", '{"days": 50, "cost_per_day": 500}'),
]

print("=== ЗАПУСК ТЕСТІВ ПЕРЕВІРОК (ТАБЛИЦЯ 2) ===\n")
for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"Виклик: {name} | Вхід: {raw}")
    print(f"  -> Рівень : {level}")
    print(f"  -> Текст  : {text}")
    print("-" * 60)