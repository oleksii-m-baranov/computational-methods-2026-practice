import csv
import matplotlib.pyplot as plt

PROMPT_NAMES = {
    "short": "Короткий",
    "medium": "Середній",
    "long": "Довгий",
}

results = []
try:
    with open("results.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
except FileNotFoundError:
    print("results.csv not found, skipping chart generation for now.")
    exit(0)

prompts = ["short", "medium", "long"]
providers_models = list(dict.fromkeys((r["provider"], r["model"]) for r in results))

fig, ax = plt.subplots(figsize=(9, 5))
colors = ["#2b5c8f", "#d95f02", "#7570b3", "#1b9e77"]

width = 0.22
gap = 0.04

for i, (provider, model) in enumerate(providers_models):
    values = []
    for p in prompts:
        matching = [float(r["chars_per_s"]) for r in results if r["provider"] == provider and r["prompt"] == p]
        values.append(matching[0] if matching else 0.0)

    x = [k + (i - (len(providers_models) - 1) / 2) * (width + gap) for k in range(len(prompts))]
    color = colors[i % len(colors)]
    bars = ax.bar(x, values, width, color=color, label=f"{provider}: {model}")

    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.annotate(
                f"{h:.0f}",
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
            )

ax.set_xticks(range(len(prompts)))
ax.set_xticklabels([PROMPT_NAMES[p] for p in prompts], fontsize=11)
ax.set_xlabel("Тип промпту", fontsize=11, fontweight="bold")
ax.set_ylabel("Швидкість генерації, симв./с", fontsize=11, fontweight="bold")
ax.set_title("Порівняння швидкості генерації: локальні моделі vs хмарна (Groq)", fontsize=13, fontweight="bold")
ax.legend(frameon=True, fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("chart.png", dpi=300)
print("Saved chart to chart.png")
