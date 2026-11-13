"""Показує КІНЕЦЬ кожної відповіді на задачу про ручку (там і лежить фінальна цифра)."""
import json

with open("task1_raw.json", encoding="utf-8") as f:
    data = json.load(f)

for key in ["qwen3:4b|reason", "llama3.2:3b|reason"]:
    print("=" * 60)
    print(key)
    print("=" * 60)
    for i, d in enumerate(data[key], 1):
        text = d["response"].strip().replace("\n", " ")
        print(f"[{i}] ... {text[-250:]}")
        print()
