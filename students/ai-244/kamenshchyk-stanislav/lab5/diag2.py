"""Діагностика 2: чи губить Ollama виклики інструментів, яких немає в списку tools.
Запуск: python diag2.py   (результат - у logs/diag2.txt)"""
import copy
import json
import sys
import urllib.request

import config
import schemas

sys.stdout = open("logs/diag2.txt", "w", encoding="utf-8")


def call(path, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request("http://localhost:11434" + path, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode("utf-8"))


print("Ollama:", call("/api/version"))
with open("rag_cases.json", encoding="utf-8") as f:
    cases = json.load(f)

# до списку інструментів додаємо «пастку»: старий search_service. Якщо модель кличе його,
# Ollama тепер поверне виклик, а не порожню відповідь.
trap = copy.deepcopy([s for s in schemas.SCHEMAS if s["function"]["name"] == "search_docs"][0])
trap["function"]["name"] = "search_service"

for desc in ["A", "B", "C"]:
    schemas.set_description("search_docs", schemas.RAG_DESCRIPTIONS[desc])
    for case in cases[:4] + cases[8:]:
        messages = [{"role": "system", "content": config.SYSTEM}, {"role": "user", "content": case["question"]}]
        out = []
        for tools in (schemas.SCHEMAS, schemas.SCHEMAS + [trap]):
            r = call("/api/chat", {"model": config.MODEL, "messages": messages, "tools": tools, "stream": False,
                                   "options": {"temperature": 0}})
            m = r["message"]
            calls = [c["function"]["name"] + json.dumps(c["function"]["arguments"], ensure_ascii=False)
                     for c in m.get("tool_calls") or []]
            out.append(calls or repr(m.get("content", ""))[:60])
        print(f"{desc} {case['id']}: звичайні tools -> {out[0]} | + search_service -> {out[1]} "
              f"| eval_count={r.get('eval_count')}")
