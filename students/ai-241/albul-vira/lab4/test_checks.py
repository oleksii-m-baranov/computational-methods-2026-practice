from dispatcher import call_tool

cases = [
    ("book_info", '{"title": "Основи алгоритмів"'),                         # 1. Зламаний JSON
    ("calculate", '{"operation": "mul", "a": "п\'ять", "b": 10}'),         # 2. Неправильний тип
    ("calculate", '{"operation": "mul", "a": 5}'),                         # 3. Відсутнє обов'язкове поле
    ("book_info", '{"title": "Основи алгоритмів", "author": "Кнут"}'),     # 4. Вигадане поле
    ("delete_book", '{}'),                                                 # 5. Неіснуючий інструмент
    ("issue_book", '{"title": "Основи алгоритмів"}'),                      # 6. Заборонена дія
    ("book_info", '{"title": "Квантова фізика для початківців"}'),         # 7. Значення немає в довіднику
    ("calculate", '{"operation": "mul", "a": -5, "b": 10}'),               # 8. Значення поза межами
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{name}({raw}) -> {level}\n{text}\n{'-' * 50}")