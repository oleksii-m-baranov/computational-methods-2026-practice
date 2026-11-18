import csv
import json
import time
from urllib.request import Request, urlopen

MODELS = ["llama3.2:3b", "qwen3:4b"]
URL = "http://localhost:11434/api/generate"

PROMPT = (
    "Поясни різницю між функцією і методом "
    "у Python. Наведи короткий приклад."
)

results = []


def unload_model(model):
    data = {
        "model": model,
        "prompt": "",
        "stream": False,
        "keep_alive": 0
    }

    request = Request(
        URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urlopen(request, timeout=600) as response:
        response.read()


def measure(model, run):
    data = {
        "model": model,
        "prompt": PROMPT,
        "stream": True,
        "keep_alive": "10m",
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

    start = time.perf_counter()
    first_token_time = None
    chunks = []
    final_response = {}

    with urlopen(request, timeout=600) as response:
        for line in response:
            if not line.strip():
                continue

            event = json.loads(line.decode("utf-8"))
            text = event.get("response", "")

            if text:
                if first_token_time is None:
                    first_token_time = time.perf_counter() - start
                chunks.append(text)

            if event.get("done"):
                final_response = event

    wall_seconds = time.perf_counter() - start
    answer = "".join(chunks)

    result = {
        "model": model,
        "run": run,
        "start_type": "cold" if run == 1 else "warm",
        "ttft_seconds": (
            round(first_token_time, 3)
            if first_token_time is not None else None
        ),
        "wall_seconds": round(wall_seconds, 3),
        "total_seconds": round(
            final_response.get("total_duration", 0) / 1e9, 3
        ),
        "load_seconds": round(
            final_response.get("load_duration", 0) / 1e9, 3
        ),
        "eval_seconds": round(
            final_response.get("eval_duration", 0) / 1e9, 3
        ),
        "tokens": final_response.get("eval_count", 0),
        "characters": len(answer),
        "status": "ok" if answer.strip() else "empty"
    }

    results.append(result)

    print(
        f"Запуск {run} ({result['start_type']}): "
        f"TTFT={result['ttft_seconds']} с, "
        f"повний час={result['wall_seconds']} с, "
        f"статус={result['status']}"
    )


for model in MODELS:
    print(f"\nМодель: {model}")
    unload_model(model)

    for run in range(1, 4):
        measure(model, run)

with open(
    "benchmark_ttft.csv", "w",
    newline="", encoding="utf-8-sig"
) as file:
    writer = csv.DictWriter(
        file, fieldnames=results[0].keys()
    )
    writer.writeheader()
    writer.writerows(results)

with open(
    "benchmark_ttft.json", "w", encoding="utf-8"
) as file:
    json.dump(results, file, ensure_ascii=False, indent=2)

print("\nГотово! Результати збережено.")
