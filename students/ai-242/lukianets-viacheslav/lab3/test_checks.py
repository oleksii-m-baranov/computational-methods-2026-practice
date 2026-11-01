"""Перевірка кожної ланки ланцюжка диспетчера окремо, без моделі."""
from dispatcher import call_tool

cases = [
    ("search_books", '{"query": "фантастика"'),                           # зламаний JSON
    ("calculate", '{"operation": "mul", "a": "п\'ять", "b": 2}'),           # неправильний тип
    ("calculate", '{"operation": "mul", "a": 5}'),                         # немає поля
    ("book_info", '{"title": "Основи алгоритмів", "x": 1}'),               # вигадане поле
    ("delete_all", '{}'),                                                   # неіснуючий інструмент
    ("issue_book", '{"title": "Основи алгоритмів"}'),                      # заборонена дія
    ("book_info", '{"title": "Неіснуюча книжка"}'),                        # немає в довіднику
    ("calculate", '{"operation": "mul", "a": 999999, "b": 2}'),            # значення поза межами
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")
