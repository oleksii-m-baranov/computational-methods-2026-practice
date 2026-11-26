
import json
import time
from providers import local, cloud, LOCAL_MODEL, CLOUD_MODEL

PROMPT = "Поясни різницю між стеком і чергою. Коротко."

results = []

for client, model in [
    (local, LOCAL_MODEL),
    (cloud, CLOUD_MODEL)
]:
    start = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": PROMPT}
        ],
        temperature=0.7
    )

    elapsed = time.perf_counter() - start
    text = response.choices[0].message.content or ""

    result = {
        "model": model,
        "response": text,
        "time_s": round(elapsed, 3),
        "chars": len(text),
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }

    results.append(result)

    print(json.dumps(
        result, ensure_ascii=False, indent=2
    ))

with open("task3_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Результати збережено у task3_results.json")
