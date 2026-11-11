import time
import statistics
import csv
from providers import make_client


def measure(client, model, prompt):
    """Вимірює TTFT, загальний час і швидкість відповіді."""
    start = time.perf_counter()
    first_token_at = None
    parts = []

    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in stream:
        if not chunk.choices:
            continue

        piece = chunk.choices[0].delta.content

        if piece:
            if first_token_at is None:
                first_token_at = time.perf_counter()
            parts.append(piece)

    end = time.perf_counter()
    text = "".join(parts)
    total = end - start

    return {
        "ttft_s": round(first_token_at - start, 3)
        if first_token_at is not None else total,
        "total_s": round(total, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / total, 1)
        if total > 0 else 0,
    }


PROMPTS = {
    "short": "Столиця Японії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": (
        "Напиши інструкцію з 10 пунктів, як налаштувати "
        "робоче середовище розробника."
    ),
}

rows = []

for provider in ["local", "cloud"]:
    client, model = make_client(provider)

    # Прогрів: результат не враховуємо
    measure(client, model, "Тестовий запит для прогріву.")

    for name, prompt in PROMPTS.items():
        runs = [measure(client, model, prompt) for _ in range(3)]

        result = {
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
            ),
        }

        rows.append(result)
        print(result)

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\nРезультати збережено у файлі results.csv")
