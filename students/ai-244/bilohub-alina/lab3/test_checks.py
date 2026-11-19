"""Перевірка ланцюжка перевірок без моделі: навмисно зламані виклики."""
from dispatcher import call_tool

cases = [
    ("зламаний JSON",          "book_info",    '{"title": "Мережі без таємниць"'),
    ("неправильний тип",       "calculate",    '{"operation": "mul", "a": "сто", "b": 5}'),
    ("відсутнє поле",          "calculate",    '{"operation": "mul", "a": 5}'),
    ("вигадане поле",          "search_books", '{"query": "фантастика", "genre": "легка"}'),
    ("неіснуючий інструмент",  "delete_all",   '{}'),
    ("заборонена дія",         "issue_book",   '{"title": "Мережі без таємниць"}'),
    ("немає в довіднику",      "book_info",    '{"title": "Книжка якої немає"}'),
    ("поза межами (клас)",     "calculate",    '{"operation": "mul", "a": -5, "b": 12}'),
    # додаткові випадки правил змісту
    ("правило з кількох арг.", "calculate",    '{"operation": "sub", "a": 5, "b": 12}'),
    ("порожній запит",         "search_books", '{"query": "   "}'),
    ("все питання в query",    "search_books", '{"query": "Я затримав книжку про алгоритми на 5 днів. Скільки штраф?"}'),
    ("коректний виклик",       "calculate",    '{"operation": "mul", "a": 5, "b": 12}'),
]

for label, name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"[{label}] {name}({raw})")
    print(f"{level:10} | {text}\n")
