import json
import sys
from dispatcher import call_tool

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Використання: python try_tool.py search_docs "{\"query\":\"ноутбук для навчання\"}"')
        sys.exit(1)

    name = sys.argv[1]
    arguments = " ".join(sys.argv[2:])

    status, result = call_tool(name, arguments)
    print("Статус:", status)
    print("Результат:", result)

    if status != "ok":
        sys.exit(1)
