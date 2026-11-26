
import requests
import json
import statistics

URL = "http://localhost:11434/api/generate"

MODELS = ["qwen3:4b", "llama3.2:3b"]

FACT = "Столиця України? Відповідай одним словом."

LOGIC = (
    "Ручка і зошит разом коштують 110 грн. "
    "Ручка на 100 грн дешевша за зошит. "
    "Скільки коштує ручка?"
)


def measure(model, prompt):
    response = requests.post(
        URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        },
        timeout=600
    )

    response.raise_for_status()
    data = response.json()

    return {
        "response": data["response"],
        "thinking": data.get("thinking", ""),
        "eval_count": data["eval_count"],
        "time_s": round(data["total_duration"] / 1e9, 3),
        "tokens_per_s": round(
            data["eval_count"] /
            (data["eval_duration"] / 1e9), 2
        ),
        "done_reason": data.get("done_reason")
    }


results = {}

for model in MODELS:
    print(f"\n===== {model} =====")

    print("\nФактичне питання:")
    fact = measure(model, FACT)
    print(json.dumps(fact, ensure_ascii=False, indent=2))

    logic_runs = []

    for i in range(5):
        print(f"\nЛогічна задача: запуск {i + 1}/5")

        result = measure(model, LOGIC)
        logic_runs.append(result)

        print("Відповідь:", result["response"])
        print("Токенів:", result["eval_count"])
        print("Час:", result["time_s"], "с")

    summary = {
        "avg_eval_count": round(statistics.mean(
            r["eval_count"] for r in logic_runs
        ), 2),
        "avg_time_s": round(statistics.mean(
            r["time_s"] for r in logic_runs
        ), 3)
    }

    results[model] = {
        "fact": fact,
        "logic_runs": logic_runs,
        "logic_summary": summary
    }

    print("\nСередні показники:", summary)

with open("task1_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nРезультати збережено у task1_results.json")
