import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from statistics import mean

URL = "http://localhost:11434/api/generate"

MODELS = ["qwen3:4b"]

TASKS = {
    "fact": {
        "prompt": "Столиця України? Відповідай одним словом.",
        "repeats": 1
    },
    "logic": {
        "prompt": (
            "Ручка і зошит разом коштують 110 грн. "
            "Ручка на 100 грн дешевша за зошит. "
            "Скільки коштує ручка?"
        ),
        "repeats": 5
    }
}

results = []

def ask_ollama(model, prompt):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
           "num_predict": 4096
        }
    }

    request = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    start = time.perf_counter()

    with urllib.request.urlopen(request, timeout=600) as response:
        data = json.loads(response.read().decode("utf-8"))

    wall_time = round(time.perf_counter() - start, 2)

    eval_count = data.get("eval_count", 0)
    eval_duration = data.get("eval_duration", 0)

    tokens_per_second = (
        round(eval_count / (eval_duration / 1e9), 2)
        if eval_duration else 0
    )

    return {
        "model": model,
        "prompt": prompt,
        "response": data.get("response", "").strip(),
        "eval_count": eval_count,
        "total_seconds": round(
            data.get("total_duration", 0) / 1e9, 2
        ),
        "wall_seconds": wall_time,
        "tokens_per_second": tokens_per_second,
        "done_reason": data.get("done_reason", ""),
        "thinking_tokens_included": bool(data.get("thinking")),
        "status": "success"
    }


output = Path(__file__).parent / "reasoning_qwen_retry.json"

for model in MODELS:
    print("\n" + "=" * 55)
    print("МОДЕЛЬ:", model)
    print("=" * 55)

    for task_name, task in TASKS.items():
        for attempt in range(1, task["repeats"] + 1):
            print(f"\nЗавдання: {task_name}")
            print(f"Запуск: {attempt}/{task['repeats']}")

            try:
                result = ask_ollama(model, task["prompt"])
                result["task"] = task_name
                result["attempt"] = attempt

                print("Відповідь:", result["response"])
                print("Токенів:", result["eval_count"])
                print("Час:", result["total_seconds"], "с")
                print(
                    "Швидкість:",
                    result["tokens_per_second"],
                    "токенів/с"
                )
                print("Причина завершення:", result["done_reason"])

            except Exception as error:
                print("Помилка:", type(error).__name__)

                result = {
                    "model": model,
                    "task": task_name,
                    "attempt": attempt,
                    "status": "error",
                    "error_type": type(error).__name__
                }

            results.append(result)

            # Зберігаємо після кожного запуску
            output.write_text(
                json.dumps(
                    results,
                    ensure_ascii=False,
                    indent=4
                ),
                encoding="utf-8"
            )


print("\n" + "=" * 55)
print("ПІДСУМКИ")
print("=" * 55)

for model in MODELS:
    logic_runs = [
        r for r in results
        if r["model"] == model
        and r["task"] == "logic"
        and r["status"] == "success"
    ]

    print("\nМодель:", model)
    print("Успішних запусків:", len(logic_runs), "/5")

    if logic_runs:
        print(
            "Середній час:",
            round(mean(r["total_seconds"] for r in logic_runs), 2),
            "с"
        )
        print(
            "Середня кількість токенів:",
            round(mean(r["eval_count"] for r in logic_runs), 2)
        )

print("\nРезультати збережено у reasoning_results.json")
