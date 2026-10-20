
import time
import statistics
import csv
from providers import make_client


def measure(client, model, prompt):
    t_start = time.perf_counter()
    first_token_at = None
    parts = []

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=True
    )

    for chunk in stream:
        piece = chunk.choices[0].delta.content

        if piece:
            if first_token_at is None:
                first_token_at = time.perf_counter()
            parts.append(piece)

    t_end = time.perf_counter()
    answer = "".join(parts)

    if first_token_at is None:
        raise RuntimeError("Модель не повернула текст")

    total = t_end - t_start

    return {
        "ttft_s": round(first_token_at - t_start, 3),
        "total_s": round(total, 3),
        "chars": len(answer),
        "chars_per_s": round(len(answer) / total, 1)
    }


PROMPTS = {
    "short": "Столиця Єгипту?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як почати працювати з Git."
}

rows = []

for provider in ["local", "cloud"]:
    client, model = make_client(provider)

    print(f"\n===== {provider.upper()} ({model}) =====")

    # Прогрів моделі
    print("Прогрів...")
    measure(client, model, "Привіт!")

    for name, prompt in PROMPTS.items():
        print(f"\nПромпт: {name}")

        runs = []

        for i in range(3):
            result = measure(client, model, prompt)
            runs.append(result)
            print(f"Запуск {i + 1}: {result}")

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

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\nРезультати збережено у results.csv")
