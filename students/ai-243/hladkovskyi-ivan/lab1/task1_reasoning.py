"""Завдання 1: міркувальна vs інструктивна модель (аналог curl до /api/generate)."""
import json
import requests

URL = "http://localhost:11434/api/generate"
MODELS = ["qwen3:4b", "llama3.2:3b"]
FACT = "Столиця України? Відповідай одним словом."
LOGIC = "Ручка і зошит разом коштують 110 грн. Ручка на 100 грн дешевша за зошит. Скільки коштує ручка?"


def ask(model, prompt):
    r = requests.post(URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=600)
    d = r.json()
    total_s = d["total_duration"] / 1e9
    tps = d["eval_count"] / (d["eval_duration"] / 1e9)
    return {
        "response": d["response"].strip(),
        "thinking_chars": len(d.get("thinking", "") or ""),
        "done_reason": d.get("done_reason"),
        "eval_count": d["eval_count"],
        "prompt_eval_count": d.get("prompt_eval_count"),
        "load_s": round(d.get("load_duration", 0) / 1e9, 2),
        "total_s": round(total_s, 2),
        "tokens_per_s": round(tps, 1),
    }


out = {"fact": {}, "logic": {}}
for m in MODELS:
    ask(m, "розігрів")  # щоб завантаження моделі не псувало вимір
    out["fact"][m] = ask(m, FACT)
    print(m, "fact:", out["fact"][m])
    out["logic"][m] = []
    for i in range(5):
        res = ask(m, LOGIC)
        out["logic"][m].append(res)
        print(m, f"logic #{i + 1}:", res["response"][:120].replace("\n", " "), "|", res["eval_count"], "ток.", res["total_s"], "с")

# середні значення для таблиці 2
for m in MODELS:
    runs = out["logic"][m]
    out.setdefault("logic_avg", {})[m] = {
        "eval_count": round(sum(r["eval_count"] for r in runs) / 5, 1),
        "total_s": round(sum(r["total_s"] for r in runs) / 5, 2),
    }
print(json.dumps(out["logic_avg"], ensure_ascii=False, indent=2))

with open("task1_raw.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("Правильних відповідей (5 грн) порахуйте вручну за task1_raw.json")
