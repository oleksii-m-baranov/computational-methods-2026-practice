"""Об'єктивна перевірка завдання 2: json.loads() на відповідях із quality.json."""
import json
import re

with open("quality.json", encoding="utf-8") as f:
    results = json.load(f)


def score(text):
    try:
        json.loads(text)
        return 2, "парситься без правок"
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", text, re.S)          # вирізаємо обгортку / вступ
    if m:
        try:
            json.loads(m.group())
            return 1, "парситься після видалення обгортки"
        except json.JSONDecodeError:
            pass
    return 0, "не парситься"


for model, tasks in results.items():
    for i, ans in enumerate(tasks["2_format"], 1):
        s, why = score(ans)
        print(f"{model} прогін {i}: {s} бали - {why}")
