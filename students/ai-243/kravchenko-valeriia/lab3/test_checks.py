"""Перевірка ланцюжка перевірок без моделі."""
from dispatcher import call_tool

cases = [
    # (назва, аргументи, очікуваний рівень, короткий опис)
    ("tariff_info", '{"city": "Львів"', "syntax", "зламаний JSON (немає закривної дужки)"),
    ("calc_price", '{"weight": "пʼять", "price_per_kg": 18, "min_price": 70}', "schema", "неправильний тип (рядок замість числа)"),
    ("calc_price", '{"weight": 15, "price_per_kg": 18}', "schema", "немає обов'язкового поля min_price"),
    ("calc_price", '{"weight": 15, "price_per_kg": 18, "min_price": 70, "x": 1}', "schema", "вигадане поле x"),
    ("delete_all", '{}', "name", "неіснуючий інструмент"),
    ("cancel_parcel", '{"parcel_id": "123"}', "permission", "заборонена дія"),
    ("tariff_info", '{"city": "Мадрид"}', "meaning", "міста немає в довіднику"),
    ("calc_price", '{"weight": 50, "price_per_kg": 18, "min_price": 70}', "schema", "вага поза межами (максимум 30)"),
    ("calc_price", '{"weight": 15, "price_per_kg": 18, "min_price": 70}', "ok", "успішний виклик"),
]

print(f"{'рівень':12} | {'опис':40} | {'текст (перші 80 символів)'}")
print("-" * 140)
for name, raw, expected, desc in cases:
    level, text = call_tool(name, raw)
    ok = "True" if level == expected else "False"
    text_short = text.replace("\n", " ")[:80]
    print(f"{ok} {level:12} | {desc:40} | {text_short}")
    