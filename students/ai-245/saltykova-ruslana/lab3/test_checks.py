from dispatcher import call_tool

cases = [
    ("scale_amount", "amount: 300, base_servings: 4"),

    ("scale_amount", '{"amount": "триста", "base_servings": 4, "target_servings": 10}'),

    ("scale_amount", '{"base_servings": 4, "target_servings": 10}'),

    ("scale_amount", '{"amount": 300, "base_servings": 4, "target_servings": 10, "extra_field": 1}'),

    ("fake_tool", '{"query": "плов"}'),

    ("place_order", '{"product": "плов"}'),

    ("product_info", '{"product": "невідомий_продукт_123"}'),

    ("scale_amount", '{"amount": -50, "base_servings": 4, "target_servings": 10}'),
]

print("ТЕСТУВАННЯ ЛАНЦЮЖКА ПЕРЕВІРОК")
for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"Інструмент: {name} | Рівень: {level}")
    print(f"Відповідь: {text}\n" + "-" * 50)