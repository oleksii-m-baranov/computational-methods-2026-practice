
import csv
import json
import statistics
import time

import matplotlib.pyplot as plt
from providers import make_client, PROVIDERS

PROMPTS = {
    "short": "Столиця Туреччини?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як оптимізувати повільний застосунок."
}

MODELS = {
    "llama": "Локальна Llama 3.2",
    "cloud": "Хмарна Gemini"
}

results = []


def measure(provider, prompt_type, prompt, run):
    client = make_client(provider)
    model = PROVIDERS[provider]["model"]

    start = time.perf_counter()
    first_token_time = None
    chunks = []

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        stream=True,
        max_tokens=512
    )

    try:
        for chunk in stream:
            if not chunk.choices:
                continue

            text = chunk.choices[0].delta.content or ""

            if text:
                if first_token_time is None:
                    first_token_time = time.perf_counter() - start
                chunks.append(text)
    finally:
        stream.close()

    total_seconds = time.perf_counter() - start
    answer = "".join(chunks)
    characters = len(answer)

    result = {
        "provider": provider,
        "model": model,
        "prompt_type": prompt_type,
        "run": run,
        "ttft_seconds": round(first_token_time, 3) if first_token_time is not None else None,
        "total_seconds": round(total_seconds, 3),
        "characters": characters,
        "chars_per_second": round(characters / total_seconds, 2) if total_seconds > 0 else 0,
        "status": "ok" if answer.strip() else "empty"
    }

    if run > 0:
        results.append(result)

    print(
        f"{MODELS[provider]} | {prompt_type} | "
        f"{'прогрів' if run == 0 else 'запуск ' + str(run)} | "
        f"TTFT={result['ttft_seconds']} с | "
        f"час={result['total_seconds']} с | "
        f"статус={result['status']}",
        flush=True
    )


for provider in MODELS:
    for prompt_type, prompt in PROMPTS.items():
        print(f"\n=== {MODELS[provider]} / {prompt_type} ===")

        for run in range(4):
            try:
                measure(provider, prompt_type, prompt, run)
            except Exception as error:
                print(f"Помилка: {error}", flush=True)
                if run > 0:
                    results.append({
                        "provider": provider,
                        "model": PROVIDERS[provider]["model"],
                        "prompt_type": prompt_type,
                        "run": run,
                        "ttft_seconds": None,
                        "total_seconds": None,
                        "characters": 0,
                        "chars_per_second": 0,
                        "status": "error"
                    })

with open("benchmark_variant9.csv", "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=[
        "provider", "model", "prompt_type", "run",
        "ttft_seconds", "total_seconds", "characters",
        "chars_per_second", "status"
    ])
    writer.writeheader()
    writer.writerows(results)

with open("benchmark_variant9.json", "w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=2)

summary = []

for provider in MODELS:
    for prompt_type in PROMPTS:
        group = [
            row for row in results
            if row["provider"] == provider
            and row["prompt_type"] == prompt_type
            and row["status"] == "ok"
            and row["ttft_seconds"] is not None
        ]

        if len(group) != 3:
            print(f"Увага: недостатньо результатів для {provider}/{prompt_type}")
            continue

        summary.append({
            "model": MODELS[provider],
            "prompt_type": prompt_type,
            "median_ttft": round(statistics.median(
                row["ttft_seconds"] for row in group
            ), 3),
            "median_total": round(statistics.median(
                row["total_seconds"] for row in group
            ), 3),
            "median_chars_per_second": round(statistics.median(
                row["chars_per_second"] for row in group
            ), 2)
        })

with open("benchmark_variant9_summary.csv", "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=[
        "model", "prompt_type", "median_ttft",
        "median_total", "median_chars_per_second"
    ])
    writer.writeheader()
    writer.writerows(summary)

if summary:
    labels = [
        f"{row['model']}\n{row['prompt_type']}"
        for row in summary
    ]
    speeds = [
        row["median_chars_per_second"]
        for row in summary
    ]

    plt.figure(figsize=(12, 6))
    plt.bar(labels, speeds)
    plt.title("Швидкість генерації: локальна та хмарна моделі")
    plt.ylabel("Символів за секунду")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig("benchmark_variant9_chart.png", dpi=200)
    plt.show()

print("\nГотово! Результати збережено.")
