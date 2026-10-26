"""Перевірка ланцюжка перевірок диспетчера без участі моделі (табл. 2)."""
from dispatcher import call_tool

cases = [
    ("Зламаний JSON",
     "calc_installment", '{"price": 24000, "months": 6'),
    ("Неправильний тип",
     "calc_installment", '{"price": "двадцять чотири тисячі", "months": 6, "overpay_percent": 10}'),
    ("Відсутнє обов'язкове поле",
     "calc_installment", '{"price": 24000, "months": 6}'),
    ("Вигадане поле",
     "search_laptops", '{"query": "навчання", "budget": 30000}'),
    ("Неіснуючий інструмент",
     "delete_all", '{}'),
    ("Заборонена дія",
     "place_order", '{"model": "StudyBook 14"}'),
    ("Значення немає в довіднику",
     "laptop_info", '{"model": "MacBook Pro 16"}'),
    ("Значення поза межами (у класі)",
     "calc_installment", '{"price": 24000, "months": 0, "overpay_percent": 10}'),
    ("Значення поза межами (у check_meaning)",
     "calc_installment", '{"price": 25000, "months": 6, "overpay_percent": 10}'),
    ("Модель із корпусу, відсутня в довіднику",
     "laptop_info", '{"model": "ProArt Creator"}'),
    ("Контрольний коректний виклик",
     "calc_installment", '{"price": 24000, "months": 6, "overpay_percent": 10}'),
]

for label, name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"[{label}]")
    print(f"Виклик : {name}('{raw}')")
    print(f"Рівень : {level}")
    print(f"Текст  : {text}\n")
