"""Завдання 1. Ціна роздумів: міркувальна vs інструктивна модель.

Робить ті самі запити, що й curl до /api/generate, і рахує час та токени/с.
"""
import json
import statistics
import urllib.request

from providers import get_logger, save_json

log = get_logger()

URL = "http://localhost:11434/api/generate"
MODELS = ["qwen3:4b", "llama3.2:3b"]
FACT = "Столиця України? Відповідай одним словом."
LOGIC = ("Ручка і зошит разом коштують 110 грн. Ручка на 100 грн дешевша "
         "за зошит. Скільки коштує ручка?")


def generate(model, prompt):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.loads(r.read().decode("utf-8"))
    data.pop("context", None)  # довгий список токенів, у звіт не потрібен
    data["time_s"] = round(data["total_duration"] / 1e9, 2)
    data["tok_per_s"] = round(data["eval_count"] / (data["eval_duration"] / 1e9), 1)
    return data


def is_correct(text):
    """Правильна відповідь - 5 грн. Шукаємо '5' як окреме число і відсутність '10 грн' як відповіді."""
    import re
    tail = text.strip().splitlines()[-1] if text.strip() else ""
    nums = re.findall(r"\b\d+(?:[.,]\d+)?\b", text)
    return ("5" in nums) and not re.search(r"\b10\s*грн\b", tail)


results = {"fact": {}, "logic": {}}

for model in MODELS:
    d = generate(model, FACT)
    results["fact"][model] = d
    log.info(f"[fact] {model}: response={d['response'].strip()!r} "
             f"eval_count={d['eval_count']} time={d['time_s']}s tok/s={d['tok_per_s']}")

for model in MODELS:
    runs = []
    for i in range(5):
        d = generate(model, LOGIC)
        d["auto_correct"] = is_correct(d["response"])
        runs.append(d)
        log.info(f"[logic] {model} #{i + 1}: eval_count={d['eval_count']} "
                 f"time={d['time_s']}s auto_correct={d['auto_correct']}")
    results["logic"][model] = {
        "runs": runs,
        "auto_correct_of_5": sum(r["auto_correct"] for r in runs),
        "mean_eval_count": round(statistics.mean(r["eval_count"] for r in runs), 1),
        "mean_time_s": round(statistics.mean(r["time_s"] for r in runs), 2),
    }

print("\n=== Задача на міркування (середнє з 5) ===")
for model in MODELS:
    s = results["logic"][model]
    print(f"{model}: правильних (авто) {s['auto_correct_of_5']}/5, "
          f"eval_count {s['mean_eval_count']}, час {s['mean_time_s']} с")

print("Збережено:", save_json("task1_reasoning.json", results))
