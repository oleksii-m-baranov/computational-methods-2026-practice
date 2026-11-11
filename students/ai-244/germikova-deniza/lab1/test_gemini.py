
import time
import statistics
from providers import make_client


PROMPTS = {
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": (
        "Напиши інструкцію з 10 пунктів, як налаштувати "
        "робоче середовище розробника."
    ),
}


def measure(client, model, prompt):
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

    total = time.perf_counter() - start
    text = "".join(parts)

    return {
        "ttft_s": round(first_token_at - start, 3)
        if first_token_at is not None else round(total, 3),
        "total_s": round(total, 3),
        "chars_per_s": round(len(text) / total, 1)
        if total > 0 else 0,
    }


client, model = make_client("cloud")

for name, prompt in PROMPTS.items():
    print(f"\nПромпт: {name}")
    results = []

    for attempt in range(1, 4):
        try:
            result = measure(client, model, prompt)
            results.append(result)
            print(f"Спроба {attempt}: {result}")
        except Exception as e:
            print(f"Спроба {attempt}: ПОМИЛКА — {e}")

    if results:
        print("МЕДІАНА:", {
            "provider": "cloud",
            "model": model,
            "prompt": name,
            "ttft_s": statistics.median(
                r["ttft_s"] for r in results
            ),
            "total_s": statistics.median(
                r["total_s"] for r in results
            ),
            "chars_per_s": statistics.median(
                r["chars_per_s"] for r in results
            ),
        })
    else:
        print("Результатів немає — усі спроби завершилися помилкою.")

