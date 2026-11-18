from dispatcher import call_tool

cases = [
    ("calculate", '{"operation": "mul", "a": 5, "b": 10'),                  # зламаний JSON
    ("calculate", '{"operation": "mul", "a": "п\'ять", "b": 10}'),          # неправильний тип
    ("calculate", '{"operation": "mul", "a": 5}'),                          # відсутнє обов'язкове поле
    ("search_books", '{"query": "фантастика", "limit": 5}'),                # вигадане поле
    ("reserve_book", '{"title": "Основи алгоритмів"}'),                     # неіснуючий інструмент
    ("issue_book", '{"title": "Основи алгоритмів"}'),                       # заборонена дія
    ("book_info", '{"title": "Квантова фізика для початківців"}'),          # значення немає в довіднику
    ("calculate", '{"operation": "mul", "a": -5, "b": 10}'),                # значення поза межами
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")

