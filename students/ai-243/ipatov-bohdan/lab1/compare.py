import json
import time
from providers import make_client

QUESTION = "Поясни різницю між списком і кортежем у Python. Коротко."

records = []

for name in ["local", "cloud"]:
    client, model = make_client(name)
    t0 = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": QUESTION}],
        temperature=0.7,
    )

    elapsed = time.perf_counter() - t0
    content = response.choices[0].message.content or ""
    usage = response.usage

    rec = {
        "provider": name,
        "model": model,
        "time_s": round(elapsed, 2),
        "content": content,
        "char_len": len(content),
        "completion_tokens": usage.completion_tokens if usage else 0,
        "prompt_tokens": usage.prompt_tokens if usage else 0,
        "total_tokens": usage.total_tokens if usage else 0,
    }
    records.append(rec)

    print(f"===== {name.upper()} ({model}) =====")
    print(content)
    print(f"Time: {elapsed:.2f} s")
    print(usage)
    print()

with open("compare_results.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print("Saved compare_results.json")
