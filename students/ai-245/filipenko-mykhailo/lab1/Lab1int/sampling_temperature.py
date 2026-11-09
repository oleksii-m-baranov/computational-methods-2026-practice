import json
import time
from urllib.request import Request, urlopen

MODEL = "llama3.2:3b"
URL = "http://localhost:11434/api/generate"

TEMPERATURES = [0.0, 0.7, 1.5]
RUNS = 5

PROMPT = (
    "Придумай коротку оригінальну назву для "
    "робота-помічника. Відповідай тільки назвою."
)

results = []

for temperature in TEMPERATURES:
    print(f"\nTEMPERATURE = {temperature}")
    print("-" * 45)

    for run in range(1, RUNS + 1):
        data = {
            "model": MODEL,
            "prompt": PROMPT,
            "stream": False,
            "think": False,
            "options": {
                "temperature": temperature,
                "top_p": 1.0,
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
            "temperature": temperature,
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
        if item["temperature"] == temperature
        and item["answer"]
    ]

    print(
        f"Унікальних відповідей: "
        f"{len(set(answers))} із {len(answers)}"
    )

with open(
    "sampling_temperature.json",
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
print("Збережено sampling_temperature.json")
