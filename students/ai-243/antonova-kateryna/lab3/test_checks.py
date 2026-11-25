
from dispatcher import call_tool

cases = [
    ("calculate", '{"operation": "mul", "a": 5, "b": 10'),              
    ("calculate", '{"operation": "mul", "a": "пять", "b": 10}'),       
    ("book_info", '{}'),                                               
    ("calculate", '{"operation": "mul", "a": 5, "b": 10, "x": 1}'),   
    ("delete_all", '{}'),                                              
    ("issue_book", '{"title": "Основи алгоритмів"}'),                  
    ("book_info", '{"title": "Книжка якої немає"}'),                   
    ("calculate", '{"operation": "mul", "a": -5, "b": 10}'),        
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")