import time
import statistics
import csv
from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')


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
        piece = chunk.choices[0].delta.content
        if piece:
            if first_token_at is None:
                first_token_at = time.perf_counter()
            parts.append(piece)

    t_end = time.perf_counter()
    text = "".join(parts)

    ttft = (first_token_at - t_start) if first_token_at is not None else (t_end - t_start)
    total = t_end - t_start
    chars_speed = len(text) / total if total > 0 else 0

    return {
        "ttft_s": round(ttft, 3),
        "total_s": round(total, 3),
        "chars": len(text),
        "chars_per_s": round(chars_speed, 1),
    }


PROMPTS = {
    "short": "Столиця Єгипту?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як почати працювати з Git.",
}

rows = []

for provider in ["local", "cloud"]:
    print(f"\n>>> Тестуємо провайдер: {provider.upper()}")
    client, model = make_client(provider)

    print("  Прогрів моделі")
    measure(client, model, "розігрів")

    for name, prompt in PROMPTS.items():
        print(f"  Вимірюємо '{name}' (3 прогони)")
        runs = [measure(client, model, prompt) for _ in range(3)]

        entry = {
            "provider": provider,
            "model": model,
            "prompt": name,
            "ttft_s": statistics.median(r["ttft_s"] for r in runs),
            "total_s": statistics.median(r["total_s"] for r in runs),
            "chars_per_s": statistics.median(r["chars_per_s"] for r in runs),
        }
        rows.append(entry)
        print(f"    -> {entry}")
        logger.info(entry)

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\nРезультати успішно збережено у results.csv!")