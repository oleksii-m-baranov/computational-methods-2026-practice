import time
import statistics
import csv

import openai
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
        if not chunk.choices:        # службові чанки без тексту (буває в Gemini)
            continue

        piece = chunk.choices[0].delta.content

        if piece:
            if first_token_at is None:
                first_token_at = time.perf_counter()  # зафіксували перший токен

            parts.append(piece)

    t_end = time.perf_counter()
    text = "".join(parts)

    if first_token_at is None:       # модель нічого не повернула
        first_token_at = t_end

    return {
        "ttft_s": round(first_token_at - t_start, 3),
        "total_s": round(t_end - t_start, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / (t_end - t_start), 1),
    }


def measure_retry(client, model, prompt, attempts=6):
    """Повторює measure(), якщо сервер перевантажений (503) або вичерпано ліміт (429).
    Час кожної спроби міряється заново, тому очікування не псує TTFT."""
    for i in range(attempts):
        try:
            return measure(client, model, prompt)
        except (openai.InternalServerError, openai.RateLimitError) as e:
            wait = 5 * 2 ** i        # 5, 10, 20, 40, 80, 160 секунд
            print(f"  помилка {e.status_code}, повтор через {wait} с...")
            time.sleep(wait)
    raise RuntimeError(f"{model}: сервер так і не відповів після {attempts} спроб")


PROMPTS = {
    "short": "Столиця Туреччини?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як оптимізувати повільний застосунок.",
}


rows = []

for provider in ["local", "cloud"]:
    client, model = make_client(provider)

    measure_retry(client, model, "розігрів")  # прогрів, не рахуємо

    for name, prompt in PROMPTS.items():
        runs = [measure_retry(client, model, prompt) for _ in range(3)]

        rows.append({
            "provider": provider,
            "model": model,
            "prompt": name,
            "ttft_s": statistics.median(r["ttft_s"] for r in runs),
            "total_s": statistics.median(r["total_s"] for r in runs),
            "chars_per_s": statistics.median(
                r["chars_per_s"] for r in runs
            ),
        })

        print(rows[-1])
        print("   повтори TTFT:", [r["ttft_s"] for r in runs],
              "всього:", [r["total_s"] for r in runs])


with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)