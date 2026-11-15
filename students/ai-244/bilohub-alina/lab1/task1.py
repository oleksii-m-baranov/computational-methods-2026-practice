"""Завдання 1: міркувальна (qwen3:4b) vs інструктивна (llama3.2:3b) модель.

Скрипт робить ті самі запити, що й curl у завданні, і одразу рахує показники.
Потрібен лише Python 3 (без додаткових бібліотек). Ollama має бути запущена.
"""
import json
import statistics
import urllib.request

URL = "http://localhost:11434/api/generate"
MODELS = ["qwen3:4b", "llama3.2:3b"]

FACT = "Столиця України? Відповідай одним словом."
REASON = ("Ручка і зошит разом коштують 110 грн. "
          "Ручка на 100 грн дешевша за зошит. Скільки коштує ручка?")


def ask(model, prompt):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def metrics(d):
    seconds = d["total_duration"] / 1e9
    tps = d["eval_count"] / (d["eval_duration"] / 1e9)
    return seconds, tps


log = {}

print("=" * 60)
print("КРОК 1. Фактичне питання")
print("=" * 60)
for model in MODELS:
    d = ask(model, FACT)
    seconds, tps = metrics(d)
    log[f"{model}|fact"] = d
    print(f"\n--- {model} ---")
    print("response    :", d["response"].strip())
    print("eval_count  :", d["eval_count"])
    print(f"Час, с      : {seconds:.2f}")
    print(f"Токенів/с   : {tps:.1f}")

print()
print("=" * 60)
print("КРОК 2. Задача на міркування (5 запусків на модель)")
print("=" * 60)
for model in MODELS:
    counts, times = [], []
    log[f"{model}|reason"] = []
    print(f"\n--- {model} ---")
    for i in range(1, 6):
        d = ask(model, REASON)
        seconds, tps = metrics(d)
        counts.append(d["eval_count"])
        times.append(seconds)
        log[f"{model}|reason"].append(d)
        answer = d["response"].strip().replace("\n", " ")
        print(f"[{i}] eval_count={d['eval_count']}, {seconds:.1f} с")
        print(f"    відповідь: {answer[:300]}")
    print(f"\nСЕРЕДНЄ для {model}: eval_count = {statistics.mean(counts):.0f}, "
          f"час = {statistics.mean(times):.1f} с")
    print("Тепер вручну порахуйте, у скількох із 5 відповіді вийшло 5 грн.")

with open("task1_raw.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
print("\nПовні відповіді збережено у task1_raw.json")
