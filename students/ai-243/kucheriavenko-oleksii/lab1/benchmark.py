import time
import statistics
import csv
import subprocess
import matplotlib.pyplot as plt
from providers import make_client

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
    "short": "Столиця Єгипту?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як почати працювати з Git.",
}

rows = []
for provider in ["local", "cloud"]:
    client, model = make_client(provider)
    measure(client, model, "розігрів")
    for name, prompt in PROMPTS.items():
        runs = [measure(client, model, prompt) for _ in range(3)]
        row = {
            "provider": provider,
            "model": model,
            "prompt": name,
            "ttft_s": round(statistics.median(r["ttft_s"] for r in runs), 3),
            "total_s": round(statistics.median(r["total_s"] for r in runs), 3),
            "chars_per_s": round(statistics.median(r["chars_per_s"] for r in runs), 1),
            "runs_ttft": [r["ttft_s"] for r in runs],
            "runs_total": [r["total_s"] for r in runs],
        }
        rows.append(row)
        print(row)

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["provider", "model", "prompt", "ttft_s", "total_s", "chars_per_s"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow({k: r[k] for k in fieldnames})

# Холодний і теплий старт локальної моделі
print("\n=== Холодний і теплий старт (llama3.2:3b) ===")
subprocess.run(["ollama", "stop", "llama3.2:3b"], check=False)
time.sleep(2)
local_client, local_model = make_client("local")
cold = measure(local_client, local_model, PROMPTS["short"])
warm = measure(local_client, local_model, PROMPTS["short"])
print("Холодний старт:", cold)
print("Теплий старт:", warm)

# Побудова стовпчикової діаграми chart.png
labels = [f"{r['provider']}\n({r['prompt']})" for r in rows]
values = [r["chars_per_s"] for r in rows]
colors = ["#3b82f6" if r["provider"] == "local" else "#10b981" for r in rows]

plt.figure(figsize=(9, 5))
bars = plt.bar(labels, values, color=colors)
plt.title("Швидкість генерації (символів/с) за моделями та довжиною промпту")
plt.ylabel("Символів за секунду")
plt.grid(axis="y", linestyle="--", alpha=0.5)
for bar, val in zip(bars, values):
    plt.text(bar.get_x() + bar.get_width()/2, val + 5, f"{val}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.savefig("chart.png", dpi=150)
print("Збережено results.csv та chart.png")
