import csv
import json
import statistics
import subprocess
import time
from providers import make_client


def measure(client, model: str, prompt: str):
    """Run a single streaming measurement, returning TTFT, total duration, and char rate."""
    t_start = time.perf_counter()
    first_token_at = None
    parts = []

    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in stream:
        if chunk.choices and len(chunk.choices) > 0:
            piece = chunk.choices[0].delta.content
            if piece:
                if first_token_at is None:
                    first_token_at = time.perf_counter()
                parts.append(piece)

    t_end = time.perf_counter()
    text = "".join(parts)

    ttft = (first_token_at - t_start) if first_token_at else (t_end - t_start)
    total = t_end - t_start

    return {
        "ttft_s": round(ttft, 3),
        "total_s": round(total, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / total, 1) if total > 0 else 0.0,
    }


# 1. Cold vs Warm start for local model
print("=== Measuring Cold vs Warm Start for llama3.2:3b ===")
client_local, model_local = make_client("local")

# Stop model in Ollama to ensure cold state
try:
    ollama_path = r"C:\Users\To4ilochka\AppData\Local\Programs\Ollama\ollama.exe"
    subprocess.run([ollama_path, "stop", "llama3.2:3b"], check=False, stdout=subprocess.DEVNULL)
    time.sleep(1)
except Exception as e:
    print("Could not stop model:", e)

cold_run = measure(client_local, model_local, "Столиця Франції?")
print("Cold run:", cold_run)

# Warm run immediately after without stopping
warm_run = measure(client_local, model_local, "Столиця Франції?")
print("Warm run:", warm_run)

startup_data = {
    "cold": cold_run,
    "warm": warm_run,
}
with open("startup_results.json", "w", encoding="utf-8") as f:
    json.dump(startup_data, f, ensure_ascii=False, indent=2)


# 2. Main Benchmarks across providers
PROMPTS = {
    "short": "Столиця Франції?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як почати вивчати Python.",
}

rows = []
for provider in ["local", "local2", "cloud"]:
    client, model = make_client(provider)
    print(f"\nTesting provider: {provider} | model: {model}")

    # Warm-up run (not included in statistics)
    try:
        measure(client, model, "розігрів")
    except Exception as e:
        print(f"Warm-up failed for {provider}: {e}")

    for name, prompt in PROMPTS.items():
        runs = []
        for i in range(3):
            try:
                res = measure(client, model, prompt)
                runs.append(res)
            except Exception as e:
                print(f"Run {i+1} failed for {provider}/{name}: {e}")

        if runs:
            row = {
                "provider": provider,
                "model": model,
                "prompt": name,
                "ttft_s": statistics.median(r["ttft_s"] for r in runs),
                "total_s": statistics.median(r["total_s"] for r in runs),
                "chars_per_s": statistics.median(r["chars_per_s"] for r in runs),
            }
            rows.append(row)
            print(f"  Prompt [{name}]: TTFT={row['ttft_s']}s, Total={row['total_s']}s, Rate={row['chars_per_s']} chars/s")

if rows:
    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print("\nSaved results to results.csv")
