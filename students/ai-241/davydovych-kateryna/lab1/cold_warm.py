import subprocess
import time
import statistics

from providers import make_client

MODEL = "llama3.2:3b"
PROMPT = "Столиця Туреччини?"

client, model = make_client("local")


def measure(prompt):
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
    return {
        "ttft_s": round(first_token_at - t_start, 3),
        "total_s": round(t_end - t_start, 3),
    }


# Холодний старт: перед кожним виміром вивантажуємо модель з пам'яті
cold = []
for i in range(3):
    subprocess.run(["ollama", "stop", MODEL], check=True)
    time.sleep(2)
    cold.append(measure(PROMPT))
    print("холодний:", cold[-1])

# Теплий старт: модель уже в пам'яті
warm = []
for i in range(3):
    warm.append(measure(PROMPT))
    print("теплий:  ", warm[-1])

print()
print(f"Холодний старт: TTFT={statistics.median(r['ttft_s'] for r in cold)} с, "
      f"всього={statistics.median(r['total_s'] for r in cold)} с")
print(f"Теплий старт:   TTFT={statistics.median(r['ttft_s'] for r in warm)} с, "
      f"всього={statistics.median(r['total_s'] for r in warm)} с")