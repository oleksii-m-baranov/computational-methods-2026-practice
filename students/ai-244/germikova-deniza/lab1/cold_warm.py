
import time
from providers import make_client

client, model = make_client("local")
prompt = "Столиця Японії?"


def measure():
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

    ttft = (
        first_token_at - start
        if first_token_at is not None
        else end - start
    )
    total = end - start

    return round(ttft, 3), round(total, 3)


print("Виконується холодний старт...")
cold_ttft, cold_total = measure()
print(f"Холодний старт — TTFT: {cold_ttft} с")
print(f"Холодний старт — Всього: {cold_total} с")

print("\nВиконується теплий старт...")
warm_ttft, warm_total = measure()
print(f"Теплий старт — TTFT: {warm_ttft} с")
print(f"Теплий старт — Всього: {warm_total} с")

