import time
import statistics
import csv
from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger("lab1")

def measure(client, model, prompt):
    t_start = time.perf_counter()
    first_token_at = None
    parts = []

    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            if first_token_at is None:
                first_token_at = time.perf_counter()
            parts.append(piece)

    t_end = time.perf_counter()
    text = "".join(parts)

    return {
        "ttft_s": round(first_token_at - t_start, 3),
        "total_s": round(t_end - t_start, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / (t_end - t_start), 1),
    }

PROMPTS = {
    "short": "Столиця Японії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як налаштувати робоче середовище розробника.",
}
rows = []

for provider in ["local", "cloud"]:
    client, model = make_client(provider)

    # Прогрів — цей запуск не враховуємо
    measure(client, model, "розігрів")

    for name, prompt in PROMPTS.items():
        runs = [measure(client, model, prompt) for _ in range(3)]

        rows.append({
            "provider": provider,
            "model": model,
            "prompt": name,
            "ttft_s": statistics.median(r["ttft_s"] for r in runs),
            "total_s": statistics.median(r["total_s"] for r in runs),
            "chars": statistics.median(r["chars"] for r in runs),
            "chars_per_s": statistics.median(r["chars_per_s"] for r in runs),
        })

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "provider",
            "model",
            "prompt",
            "ttft_s",
            "total_s",
            "chars",
            "chars_per_s",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)

for row in rows:
    logger.info(row)

print("\nГотово. Результати збережено у results.csv")