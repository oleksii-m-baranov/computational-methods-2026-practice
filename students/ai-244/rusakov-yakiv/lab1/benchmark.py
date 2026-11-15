"""Завдання 4. Вимірювання швидкості: TTFT і залежність від довжини запиту (варіант 8)."""
from logsetup import print  # друк іде і в консоль, і в lab1.log
import csv
import os
import statistics
import sys
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
        piece = chunk.choices[0].delta.content
        if piece:
            if first_token_at is None:
                first_token_at = time.perf_counter()   # зафіксували перший токен
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
    "short":  "Столиця Мексики?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long":   "Напиши інструкцію з 10 пунктів, як задокументувати проєкт.",
}

# `python benchmark.py cloud` — виміряти лише хмарну; рядки інших провайдерів зберігаються
providers = sys.argv[1:] or ["local", "cloud"]
rows = []
if os.path.exists("results.csv"):
    with open("results.csv", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["provider"] not in providers]

for provider in providers:
    client, model = make_client(provider)

    # Прогрів у таблицю не потрапляє, але його TTFT — це «холодний» (перший) запит.
    # Якщо перед запуском виконати `ollama stop llama3.2:3b`, запишіть це значення
    # як холодний старт; значення із рядків нижче — теплі.
    warm = measure(client, model, "розігрів")
    print(f"[{provider}] перший запит (розігрів): TTFT={warm['ttft_s']} с, всього={warm['total_s']} с")

    for name, prompt in PROMPTS.items():
        runs = [measure(client, model, prompt) for _ in range(3)]
        rows.append({
            "provider": provider,
            "model": model,
            "prompt": name,
            "ttft_s": statistics.median(r["ttft_s"] for r in runs),
            "total_s": statistics.median(r["total_s"] for r in runs),
            "chars_per_s": statistics.median(r["chars_per_s"] for r in runs),
        })
        print(rows[-1])
        print("   три повтори (TTFT):", [r["ttft_s"] for r in runs])

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
