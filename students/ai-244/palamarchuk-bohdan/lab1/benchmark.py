import sys
import os
import time
import statistics
import csv
from providers import make_client

CSV = "results.csv"
FIELDS = ["provider", "model", "prompt", "ttft_s", "total_s", "chars_per_s"]
PAUSE = {"local": 0, "cloud": 15}   # пауза між запитами, щоб не впертися в ліміт

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
                first_token_at = time.perf_counter()  # зафіксували перший токен
            parts.append(piece)

    t_end = time.perf_counter()
    text = "".join(parts)

    return {
        "ttft_s": round(first_token_at - t_start, 3),
        "total_s": round(t_end - t_start, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / (t_end - t_start), 1),
    }

def measure_retry(client, model, prompt, pause, attempts=6):
    """При помилці сервера (429, 503) чекаємо і пробуємо знову."""
    for _ in range(attempts):
        try:
            result = measure(client, model, prompt)
            time.sleep(pause)
            return result
        except Exception as e:
            print("ПОМИЛКА:", str(e)[:400])
            print("повтор через 65 с")
            time.sleep(65)
    raise RuntimeError("не вдалося виконати запит")

PROMPTS = {
    "short": "Столиця Бразилії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як підготуватися до технічної співбесіди.",
}

rows = []
if os.path.exists(CSV):
    with open(CSV, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
done = {(r["provider"], r["prompt"]) for r in rows}

def save():
    with open(CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

providers = sys.argv[1:] or ["local", "cloud"]
for provider in providers:
    todo = [n for n in PROMPTS if (provider, n) not in done]
    if not todo:
        continue
    client, model = make_client(provider)
    pause = PAUSE.get(provider, 0)

    measure_retry(client, model, "розігрів", pause)   # прогрів, не рахуємо

    for name in todo:
        runs = [measure_retry(client, model, PROMPTS[name], pause) for _ in range(3)]
        rows.append({
            "provider": provider,
            "model": model,
            "prompt": name,
            "ttft_s": statistics.median(r["ttft_s"] for r in runs),
            "total_s": statistics.median(r["total_s"] for r in runs),
            "chars_per_s": statistics.median(r["chars_per_s"] for r in runs),
        })
        print(rows[-1])
        save()
