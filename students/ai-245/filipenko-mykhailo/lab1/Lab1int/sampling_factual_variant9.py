import json
import time
from pathlib import Path
from urllib.request import Request, urlopen

MODEL = "llama3.2:3b"
URL = "http://localhost:11434/api/generate"

PROMPT = "У якому році випустили перший iPhone? Відповідай лише роком."

OUTPUT = Path("sampling_factual_variant9.json")
results = []

for temperature in [0.0, 1.5]:
    for run in range(1, 6):
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
            data=json.dumps(
                data, ensure_ascii=False
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json; charset=utf-8"
            }
        )

        start = time.perf_counter()

        with urlopen(request, timeout=600) as response:
            response_data = json.loads(
                response.read().decode("utf-8")
            )

        elapsed = time.perf_counter() - start
        answer = response_data.get("response", "").strip()

        results.append({
            "model": MODEL,
            "prompt": PROMPT,
            "temperature": temperature,
            "top_p": 1.0,
            "run": run,
            "answer": answer,
            "correct": answer.strip().rstrip(".") == "2007",
            "seconds": round(elapsed, 2)
        })

        OUTPUT.write_text(
            json.dumps(
                results,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print(
            f"temperature={temperature} | "
            f"{run}/5 | {answer}",
            flush=True
        )

print("\nПІДСУМОК")

for temperature in [0.0, 1.5]:
    group = [
        x for x in results
        if x["temperature"] == temperature
    ]
    correct = sum(x["correct"] for x in group)

    print(
        f"temperature={temperature}: "
        f"{correct}/5 правильних"
    )

print(f"\nЗбережено {OUTPUT}")
