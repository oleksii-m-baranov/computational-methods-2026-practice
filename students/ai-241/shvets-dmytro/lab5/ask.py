"""Одне питання з rag_cases.json агентові.
Запуск: python ask.py D1"""
import json
import sys

import agent

with open("rag_cases.json", encoding="utf-8") as f:
    cases = {c["id"]: c for c in json.load(f)}

answer = agent.run_agent(cases[sys.argv[1]]["question"])
print("\nВІДПОВІДЬ:", answer)
