"""Завдання 3: локальна vs хмарна модель (варіант 7)."""
import json
import time
from providers import make_client

QUESTION = "Поясни різницю між процесом і потоком. Коротко."

rows = []
for name in ["local", "cloud"]:
    client, model = make_client(name)
    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": QUESTION}],
        temperature=0.7,
    )
    elapsed = time.perf_counter() - t0
    text = response.choices[0].message.content
    print(f"===== {name.upper()} ({model}) =====")
    print(text)
    print(f"Час: {elapsed:.2f} с")
    print(response.usage)
    print()
    rows.append({
        "provider": name,
        "model": model,
        "time_s": round(elapsed, 2),
        "completion_tokens": response.usage.completion_tokens,
        "chars": len(text),
        "text": text,
    })

with open("compare_results.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
