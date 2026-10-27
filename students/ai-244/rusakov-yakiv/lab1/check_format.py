"""Крок 4 завдання 5: об'єктивна перевірка завдання 2 через json.loads() для кожної моделі.

0 балів — не парситься; 1 — парситься після видалення markdown-обгортки / вступної фрази; 2 — парситься одразу.
"""
from logsetup import print  # друк іде і в консоль, і в lab1.log
import json
import re

with open("quality.json", encoding="utf-8") as f:
    data = json.load(f)

for model, tasks in data.items():
    for i, answer in enumerate(tasks["2_format"], 1):
        try:
            json.loads(answer)
            score, note = 2, "парситься без правок"
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", answer, re.S)
            try:
                json.loads(m.group(0)) if m else None
                score, note = (1, "парситься після зрізання обгортки") if m else (0, "не парситься")
            except json.JSONDecodeError:
                score, note = 0, "не парситься"
        print(f"{model:28} прогін {i}: {score} — {note} | markdown: {'```' in answer}")
