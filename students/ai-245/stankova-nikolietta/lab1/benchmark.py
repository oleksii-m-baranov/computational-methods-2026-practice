import time
import statistics
import csv

from providers import ollama_client, gemini_client


def measure(client, model, prompt):

    t_start = time.perf_counter()

    first_token_at = None
    parts = []

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
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
    "short": "Столиця Єгипту?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як почати працювати з Git.",
}

rows = []

configs = [
    ("local", ollama_client(), "llama3.2:3b"),
    ("cloud", gemini_client(), "gemini-3.8-flash"),
]

for provider, client, model in configs:

    for name, prompt in PROMPTS.items():

        try:

            runs = [measure(client, model, prompt) for _ in range(3)]

            row = {
                "provider": provider,
                "model": model,
                "prompt": name,
                "ttft_s": statistics.median(r["ttft_s"] for r in runs),
                "total_s": statistics.median(r["total_s"] for r in runs),
                "chars_per_s": statistics.median(r["chars_per_s"] for r in runs),
            }

            rows.append(row)

            print(row)

        except Exception as e:

            print(f"Помилка для {provider} / {name}: {e}")

            rows.append({
                "provider": provider,
                "model": model,
                "prompt": name,
                "ttft_s": "ERROR",
                "total_s": "ERROR",
                "chars_per_s": "ERROR",
            })

        # записуємо файл після КОЖНОГО результату
        with open(
            "results.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=rows[0].keys()
            )

            writer.writeheader()
            writer.writerows(rows)

print("results.csv створено")