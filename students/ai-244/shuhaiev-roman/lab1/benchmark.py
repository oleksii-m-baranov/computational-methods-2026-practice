"""Завдання 4. Вимірювання швидкості: TTFT і залежність від довжини запиту.

python benchmark.py          - повний замір, результати в results.csv
python benchmark.py --cold   - холодний і теплий старт локальної моделі
"""
import csv
import statistics
import subprocess
import sys
import time

from providers import make_client, get_logger, save_json

log = get_logger()


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
    if first_token_at is None:
        first_token_at = t_end

    return {
        "ttft_s": round(first_token_at - t_start, 3),
        "total_s": round(t_end - t_start, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / (t_end - t_start), 1),
    }


PROMPTS = {
    "short":  "Столиця Бразилії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long":   "Напиши інструкцію з 10 пунктів, як підготуватися до технічної співбесіди.",
}


def full_benchmark():
    rows, raw = [], []
    for provider in ["local", "cloud"]:
        client, model = make_client(provider)

        measure(client, model, "розігрів")          # прогрів, не рахуємо

        for name, prompt in PROMPTS.items():
            runs = [measure(client, model, prompt) for _ in range(3)]
            raw.append({"provider": provider, "model": model, "prompt": name, "runs": runs})
            rows.append({
                "provider": provider,
                "model": model,
                "prompt": name,
                "ttft_s": statistics.median(r["ttft_s"] for r in runs),
                "total_s": statistics.median(r["total_s"] for r in runs),
                "chars_per_s": statistics.median(r["chars_per_s"] for r in runs),
            })
            print(rows[-1])
            log.info(f"[bench] {rows[-1]} runs={runs}")

    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    save_json("task4_runs.json", raw)


def cold_warm():
    client, model = make_client("local")
    subprocess.run(["ollama", "stop", model], check=False)
    time.sleep(2)
    cold = measure(client, model, PROMPTS["short"])
    warm = measure(client, model, PROMPTS["short"])
    print("Холодний:", cold)
    print("Теплий:  ", warm)
    log.info(f"[cold/warm] cold={cold} warm={warm}")
    save_json("task4_cold_warm.json", {"model": model, "cold": cold, "warm": warm})


if __name__ == "__main__":
    if "--cold" in sys.argv:
        cold_warm()
    else:
        full_benchmark()
