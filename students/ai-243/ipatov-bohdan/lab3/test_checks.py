"""Unit tests for tool dispatch validation pipeline (Table 2). Variant 11 (Library)."""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dispatcher import call_tool

cases = [
    ("Зламаний JSON", "search_books", '{"query": "фантастика"'),
    ("Неправильний тип", "calculate", '{"operation": "mul", "a": "два", "b": 10}'),
    ("Відсутнє обов'язкове поле", "book_info", '{}'),
    ("Вигадане поле", "search_books", '{"query": "фантастика", "extra_param": 123}'),
    ("Неіснуючий інструмент", "delete_all_books", '{}'),
    ("Заборонена дія", "issue_book", '{"title": "Основи алгоритмів"}'),
    ("Значення немає в довіднику", "book_info", '{"title": "Невідома Книга 2026"}'),
    ("Значення поза межами", "calculate", '{"operation": "mul", "a": -5, "b": 10}'),
]

print(f"{'Що перевіряємо':30} | {'Рівень':12} | Повідомлення")
print("-" * 80)
for desc, name, raw in cases:
    level, text = call_tool(name, raw)
    first_line = text.replace("\n", " ")
    print(f"{desc:30} | {level:12} | {first_line}")
