from dispatcher import call_tool

cases = [
    ("search_books", '{"query": "фантастика"}'),  # валідний запит JSON
    ("search_books", '{"query": "123"}'),         # неіснуюча книжка
    ("delete_all", '{}'),                         # неіснуючий інструмент
    ("search_books", '{"query": фантастика}'),    # неправильний тип
    ("search_books", '{"text": "фантастика"}'),   # вигадане поля
]

if __name__ == '__main__':
    for name, raw in cases:
        level, text = call_tool(name, raw)
        print(f"{level:10} | {text}\n")
