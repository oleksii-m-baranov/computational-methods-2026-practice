"""Тестування ланцюжка перевірок dispatcher.py (Таблиця 2)."""
from dispatcher import call_tool

cases = [
    ("Зламаний JSON", "search_books", '{"query": "алгоритми"'),
    ("Неправильний тип", "calculate", '{"operation": "add", "a": "пять", "b": 10}'),
    ("Відсутнє обов'язкове поле", "book_info", '{}'),
    ("Вигадане поле", "search_books", '{"query": "фантастика", "author": "Азімов"}'),
    ("Неіснуючий інструмент", "delete_book", '{"title": "Основи алгоритмів"}'),
    ("Заборонена дія", "issue_book", '{"title": "Основи алгоритмів"}'),
    ("Значення немає в довіднику", "book_info", '{"title": "Квантова фізика для чайників"}'),
    ("Значення поза межами (схема)", "calculate", '{"operation": "add", "a": -5, "b": 10}'),
    ("Значення поза межами (зміст)", "calculate", '{"operation": "sub", "a": 5, "b": 10}'),
]

print(f"{'Що перевіряємо':<28} | {'Рівень':<10} | {'Повідомлення'}")
print("-" * 80)
for desc, name, raw in cases:
    level, text = call_tool(name, raw)
    first_line = text.split("\n")[0]
    print(f"{desc:<28} | {level:<10} | {first_line}")
