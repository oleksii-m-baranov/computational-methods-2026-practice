import json
import time
from urllib.request import Request, urlopen

MODEL = "llama3.2:3b"
URL = "http://localhost:11434/api/generate"

PROMPT = (
    "Придумай коротку оригінальну назву для "
    "робота-помічника. Відповідай тільки назвою."
)

RUNS = 10
results = []

for run in range(1, RUNS + 1):
    data = {
        "model": MODEL,
        "prompt": PROMPT,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0,
            "top_p": 1.0,
            "seed": 42,
            "num_predict": 100
        }
    }

    request = Request(
        URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    start = time.perf_counter()

    with urlopen(request, timeout=600) as response:
        response_data = json.loads(
            response.read().decode("utf-8")
        )

    elapsed = time.perf_counter() - start
    answer = response_data.get("response", "").strip()

    results.append({
        "run": run,
        "model": MODEL,
        "temperature": 0,
        "top_p": 1.0,
        "seed": 42,
        "answer": answer,
        "seconds": round(elapsed, 2),
        "status": "ok" if answer else "empty"
    })

    print(f"Запуск {run}: {answer} ({elapsed:.2f} с)")

unique_answers = len(set(
    item["answer"] for item in results if item["answer"]
))

print(f"\nУнікальних відповідей: {unique_answers} із {RUNS}")

with open(
    "sampling_reproducibility.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(results, file, ensure_ascii=False, indent=2)

print("Збережено sampling_reproducibility.json")
