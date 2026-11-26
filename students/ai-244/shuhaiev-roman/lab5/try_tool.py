"""Перевірка інструмента search_docs через диспетчер, без моделі.
Запуск: python try_tool.py D1"""
import json
import sys

import dispatcher

with open("rag_cases.json", encoding="utf-8") as f:
    cases = {c["id"]: c for c in json.load(f)}

question = cases[sys.argv[1]]["question"]
print("ПИТАННЯ:", question, "\n")
level, text = dispatcher.call_tool("search_docs", json.dumps({"query": question}, ensure_ascii=False))
print(f"рівень: {level}\n{text}\n")

level, text = dispatcher.call_tool("search_docs", '{"query": "а"}')
print(f"Занадто короткий запит -> рівень: {level}\n{text}")
