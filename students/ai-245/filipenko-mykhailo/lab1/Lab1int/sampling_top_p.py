import json
import time
from urllib.request import Request, urlopen

MODEL = "llama3.2:3b"
URL = "http://localhost:11434/api/generate"

TOP_P_VALUES = [0.1, 0.5, 1.0]
RUNS = 5

PROMPT = (
    "Придумай коротку оригінальну назву для "
    "робота-помічника. Відповідай тільки назвою."
)

results = []

for top_p in TOP_P_VALUES:
    print(f"\nTOP_P = {top_p}")
    print("-" * 45)

    for run in range(1, RUNS + 1):
        data = {
            "model": MODEL,
            "prompt": PROMPT,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.7,
                "top_p": top_p,
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
            result = json.loads(
                response.read().decode("utf-8")
            )

        elapsed = time.perf_counter() - start
        answer = result.get("response", "").strip()

        record = {
            "model": MODEL,
            "top_p": top_p,
            "temperature": 0.7,
            "run": run,
            "prompt": PROMPT,
            "answer": answer,
            "seconds": round(elapsed, 2),
            "status": "ok" if answer else "empty"
        }

        results.append(record)

        print(
            f"Запуск {run}: {answer} "
            f"({record['seconds']} с)"
        )

    answers = [
        item["answer"]
        for item in results
        if item["top_p"] == top_p
        and item["answer"]
    ]

    print(
        f"Унікальних відповідей: "
        f"{len(set(answers))} із {len(answers)}"
    )

with open(
    "sampling_top_p.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        results,
        file,
        ensure_ascii=False,
        indent=2
    )

print("\nТестування завершено!")
print("Збережено sampling_top_p.json")
