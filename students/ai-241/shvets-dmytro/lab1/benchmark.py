
import csv
import json
import time
import statistics
import subprocess
import matplotlib.pyplot as plt

from providers import (
    local, cloud,
    LOCAL_MODEL, QWEN_MODEL, CLOUD_MODEL
)

PROMPTS = {
    "short": "Столиця Японії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як налаштувати робоче середовище розробника."
}


def measure(client, model, prompt):
    start = time.perf_counter()
    first = None
    parts = []

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=True,
        temperature=0.7
    )

    for chunk in stream:
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content

        if content:
            if first is None:
                first = time.perf_counter()

            parts.append(content)

    end = time.perf_counter()
    text = "".join(parts)

    if first is None:
        raise RuntimeError(
            f"Модель {model} не повернула текст"
        )

    return {
        "ttft_s": round(first - start, 3),
        "total_s": round(end - start, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / (end - start), 1),
        "response": text
    }


rows = []
raw_runs = []

for provider, client, model in [
    ("local", local, LOCAL_MODEL),
    ("cloud", cloud, CLOUD_MODEL),
    ("qwen", local, QWEN_MODEL)
]:
    print(f"\n===== {model} =====")

    print("Прогрів...")
    measure(client, model, "розігрів")

    for name, prompt in PROMPTS.items():
        runs = []

        for i in range(3):
            print(f"{name}: запуск {i + 1}/3")

            result = measure(client, model, prompt)
            runs.append(result)

            raw_runs.append({
                "provider": provider,
                "model": model,
                "prompt": name,
                "run": i + 1,
                **result
            })

            print(
                f"TTFT: {result['ttft_s']} с; "
                f"Total: {result['total_s']} с; "
                f"Speed: {result['chars_per_s']} симв./с"
            )

        row = {
            "provider": provider,
            "model": model,
            "prompt": name,
            "ttft_s": statistics.median(
                r["ttft_s"] for r in runs
            ),
            "total_s": statistics.median(
                r["total_s"] for r in runs
            ),
            "chars_per_s": statistics.median(
                r["chars_per_s"] for r in runs
            )
        }

        rows.append(row)
        print("Медіана:", row)

with open("results.csv", "w", newline="",
          encoding="utf-8") as f:
    writer = csv.DictWriter(
        f, fieldnames=rows[0].keys()
    )
    writer.writeheader()
    writer.writerows(rows)

with open("benchmark_runs.json", "w",
          encoding="utf-8") as f:
    json.dump(raw_runs, f, ensure_ascii=False, indent=2)


# Холодний і теплий старт
print("\n===== Холодний і теплий старт =====")

subprocess.run(
    ["ollama", "stop", LOCAL_MODEL],
    check=True
)

cold = measure(local, LOCAL_MODEL, PROMPTS["short"])
warm = measure(local, LOCAL_MODEL, PROMPTS["short"])

starts = {
    "cold": cold,
    "warm": warm
}

with open("cold_warm.json", "w",
          encoding="utf-8") as f:
    json.dump(starts, f, ensure_ascii=False, indent=2)

print("Холодний старт:", cold)
print("Теплий старт:", warm)


# Стовпчикова діаграма для шести комбінацій
chart_rows = [
    r for r in rows
    if r["provider"] in ("local", "cloud")
]

names = {
    "short": "Короткий",
    "medium": "Середній",
    "long": "Довгий"
}

labels = [
    ("Llama" if r["provider"] == "local" else "GPT-OSS")
    + "\n" + names[r["prompt"]]
    for r in chart_rows
]

values = [r["chars_per_s"] for r in chart_rows]

plt.figure(figsize=(10, 5))

bars = plt.bar(labels, values)

plt.bar_label(bars, fmt="%.1f", padding=3)
plt.ylabel("Швидкість, символів/с")
plt.title("Порівняння швидкості генерації моделей")
plt.ylim(0, max(values) * 1.15)
plt.grid(axis="y", alpha=0.25)
plt.tight_layout()

plt.savefig("task4_chart.png", dpi=300)
plt.close()

print("\nУсі результати збережено.")
