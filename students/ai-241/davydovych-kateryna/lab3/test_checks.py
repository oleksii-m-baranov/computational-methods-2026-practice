"""Перевірка ланцюжка перевірок диспетчера без моделі (табл. 2)."""
from dispatcher import call_tool

cases = [
    # (що перевіряємо, інструмент, аргументи рядком – як їх передає модель)
    ("Правильний виклик (контроль)",
     "calc_installment", '{"price": 24000, "months": 6, "overpay_percent": 10}'),
    ("Зламаний JSON",
     "laptop_info", '{"model": "StudyBook 14"'),
    ("Неправильний тип",
     "calc_installment", '{"price": "двадцять чотири тисячі", "months": 6, "overpay_percent": 10}'),
    ("Рядок-число (Pydantic перетворить сам)",
     "calc_installment", '{"price": "24000", "months": "6", "overpay_percent": 10}'),
    ("Відсутнє обов'язкове поле",
     "calc_installment", '{"price": 24000, "months": 6}'),
    ("Вигадане поле",
     "search_laptops", '{"query": "навчання", "budget": 30000}'),
    ("Неіснуючий інструмент",
     "reserve_laptop", '{"model": "StudyBook 14"}'),
    ("Заборонена дія",
     "place_order", '{"model": "StudyBook 14"}'),
    ("Значення немає в довіднику",
     "laptop_info", '{"model": "MacBook Pro 16"}'),
    ("Схожа назва (підказка)",
     "laptop_info", '{"model": "StudyBook 15"}'),
    ("Модель є в корпусі, але не в довіднику",
     "laptop_info", '{"model": "ArtLine Studio 15"}'),
    ("Значення поза межами (у класі)",
     "calc_installment", '{"price": 24000, "months": 0, "overpay_percent": 10}'),
    ("Усе питання замість ключового слова (у класі)",
     "search_laptops", '{"query": "Порадь ноутбук для монтажу відео 8К"}'),
    ("Вигадана ціна (у check_meaning)",
     "calc_installment", '{"price": 25000, "months": 6, "overpay_percent": 10}'),
]

for title, name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"### {title}")
    print(f"виклик : {name}({raw})")
    print(f"рівень : {level}")
    print(f"текст  : {text}\n")
