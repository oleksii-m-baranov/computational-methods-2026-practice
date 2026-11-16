import csv
import json
import time
from urllib.request import Request, urlopen

MODELS = ["llama3.2:3b", "qwen3:4b"]

PROMPT = (
    "Поясни різницю між функцією і методом "
    "у Python. Наведи короткий приклад."
)

URL = "http://localhost:11434/api/generate"

results = []


def ollama_request(model, prompt, keep_alive):
    data = {
        "model": model,
        "prompt": prompt,
       "stream": False,
"keep_alive": keep_alive,
"think": False,
"options": {
    "temperature": 0,
    "num_predict": 512
}
    }

    request = Request(
        URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urlopen(request, timeout=600) as response:
        return json.loads(response.read().decode("utf-8"))


for model in MODELS:
    print(f"\nМодель: {model}")

    # Вивантажуємо модель перед холодним стартом
    ollama_request(model, "", 0)

    for run in range(1, 4):
        start = time.perf_counter()

        response = ollama_request(model, PROMPT, "10m")

        wall_seconds = time.perf_counter() - start
        answer = response.get("response", "")

        total_seconds = response.get("total_duration", 0) / 1e9
        load_seconds = response.get("load_duration", 0) / 1e9
        eval_seconds = response.get("eval_duration", 0) / 1e9
        tokens = response.get("eval_count", 0)

        characters = len(answer)
        chars_per_second = (
            characters / eval_seconds
            if eval_seconds > 0 else 0
        )

        result = {
            "model": model,
            "run": run,
            "start_type": "cold" if run == 1 else "warm",
            "wall_seconds": round(wall_seconds, 2),
            "total_seconds": round(total_seconds, 2),
            "load_seconds": round(load_seconds, 2),
            "eval_seconds": round(eval_seconds, 2),
            "tokens": tokens,
            "characters": characters,
            "chars_per_second": round(chars_per_second, 2),
            "status": "ok" if answer.strip() else "empty"
        }

        results.append(result)

        print(
            f"Запуск {run}: "
            f"{result['start_type']}, "
            f"час {result['wall_seconds']} с, "
            f"завантаження {result['load_seconds']} с, "
            f"швидкість {result['chars_per_second']} симв./с, "
            f"статус {result['status']}"
        )

with open(
    "benchmark_results.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=results[0].keys()
    )
    writer.writeheader()
    writer.writerows(results)

with open(
    "benchmark_results.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(results, file, ensure_ascii=False, indent=2)

print("\nТестування завершено!")
print("Збережено benchmark_results.csv і benchmark_results.json")
