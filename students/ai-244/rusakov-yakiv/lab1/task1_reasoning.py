"""Завдання 1. Те саме, що curl-запити з методички, але в циклі й з підрахунком показників.

Використовує лише стандартну бібліотеку: запити йдуть напряму на /api/generate.
"""
from logsetup import print  # друк іде і в консоль, і в lab1.log
import json
import re
import urllib.request

URL = "http://localhost:11434/api/generate"
MODELS = ["qwen3:4b", "llama3.2:3b"]
FACT = "Столиця України? Відповідай одним словом."
LOGIC = "Ручка і зошит разом коштують 110 грн. Ручка на 100 грн дешевша за зошит. Скільки коштує ручка?"
RUNS = 5


def generate(model, prompt):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.loads(r.read().decode("utf-8"))
    return {
        "response": d["response"].strip(),
        "eval_count": d["eval_count"],
        "done_reason": d.get("done_reason"),
        "time_s": d["total_duration"] / 1e9,
        "tokens_per_s": d["eval_count"] / (d["eval_duration"] / 1e9),
    }


def is_correct(text):
    """Орієнтовна автоперевірка: у фінальній частині відповіді є «5 грн», але немає «10 грн».
    Правильна відповідь — 5 грн; типова помилка — 10 грн (110 - 100)."""
    tail = text.lower().replace(",", ".")[-300:]
    return bool(re.search(r"(?<![\d.])5(\.0+)?\s*(грн|гривн)", tail)) and "10 грн" not in tail


out = {"fact": {}, "logic": {}}
for model in MODELS:
    out["fact"][model] = generate(model, FACT)
    print(model, "FACT", out["fact"][model])
    runs = []
    for i in range(RUNS):
        r = generate(model, LOGIC)
        r["correct_auto"] = is_correct(r["response"])   # автоперевірка лише орієнтовна — перечитайте відповіді!
        runs.append(r)
        print(model, f"LOGIC run {i + 1}: {r['time_s']:.1f} c, eval_count={r['eval_count']}, auto_correct={r['correct_auto']}")
    out["logic"][model] = runs

with open("task1_results.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("\nСереднє по задачі на міркування (5 запусків):")
for model, runs in out["logic"].items():
    n = len(runs)
    print(f"{model}: eval_count={sum(r['eval_count'] for r in runs) / n:.0f}, "
          f"час={sum(r['time_s'] for r in runs) / n:.1f} c, "
          f"правильних (авто)={sum(r['correct_auto'] for r in runs)} із {n}")
