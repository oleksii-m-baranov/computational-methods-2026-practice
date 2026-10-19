import csv
import statistics
import time
from providers import make_client


def measure(client, model, prompt):
    """Один вимір: повертає TTFT, загальний час і довжину відповіді."""
    t_start = time.perf_counter()
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
        delta = chunk.choices[0].delta
        piece = getattr(delta, "content", None)

        if piece:
            if first_token_at is None:
                first_token_at = time.perf_counter()  # зафіксували перший токен
            parts.append(piece)

    t_end = time.perf_counter()
    text = "".join(parts)

    # Якщо перший токен не спіймали (наприклад, дуже коротка чи пуста відповідь)
    if first_token_at is None:
        first_token_at = t_end

    total_time = max(t_end - t_start, 0.001)

    return {
        "ttft_s": round(first_token_at - t_start, 3),
        "total_s": round(total_time, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / total_time, 1),
    }


PROMPTS = {
    "short": "Столиця Норвегії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як провести код-рев’ю.",
}

rows = []

for provider in ["local", "cloud"]:
    print(f"\n--- Запуск для провайдера: {provider} ---")
    client, model = make_client(provider)

    print("Прогрів моделі...")
    measure(client, model, "розігрів")  # прогрів, не рахуємо

    for name, prompt in PROMPTS.items():
        print(f"Тестування запиту '{name}' (3 ітерації)...")
        runs = [measure(client, model, prompt) for _ in range(3)]

        row = {
            "provider": provider,
            "model": model,
            "prompt": name,
            "ttft_s": round(statistics.median(r["ttft_s"] for r in runs), 3),
            "total_s": round(statistics.median(r["total_s"] for r in runs), 3),
            "chars_per_s": round(
                statistics.median(r["chars_per_s"] for r in runs), 1
            ),
        }
        rows.append(row)
        print(f"  Результат: {row}")

# Збереження результатів у CSV
with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\nВсі вимірювання завершено. Дані збережено у файл 'results.csv'!")
