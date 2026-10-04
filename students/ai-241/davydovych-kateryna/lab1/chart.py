import csv
import matplotlib.pyplot as plt

# Читаємо результати, які зберіг benchmark.py
with open("results.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

PROMPT_NAMES = {"short": "Короткий", "medium": "Середній", "long": "Довгий"}
prompts = ["short", "medium", "long"]
providers = [
    ("local", "#2a78d6"),   # синій
    ("cloud", "#eb6834"),   # помаранчевий
]

fig, ax = plt.subplots(figsize=(8, 5))
width = 0.38
gap = 0.02  # маленький проміжок між сусідніми стовпчиками

for i, (provider, color) in enumerate(providers):
    data = [r for r in rows if r["provider"] == provider]
    model = data[0]["model"]
    values = [float(next(r for r in data if r["prompt"] == p)["chars_per_s"])
              for p in prompts]
    x = [k + (i - 0.5) * (width + gap) for k in range(len(prompts))]

    bars = ax.bar(x, values, width, color=color, label=f"{model} ({provider})")
    ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=10, color="#333333")

ax.set_xticks(range(len(prompts)))
ax.set_xticklabels([PROMPT_NAMES[p] for p in prompts])
ax.set_xlabel("Промпт")
ax.set_ylabel("Швидкість, символів/с")
ax.set_title("Швидкість відповіді: локальна vs хмарна модель")

# Приглушена сітка й рамка, щоб увага була на стовпчиках
ax.grid(axis="y", color="#dddddd", linewidth=0.8)
ax.set_axisbelow(True)
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
ax.spines["left"].set_color("#999999")
ax.spines["bottom"].set_color("#999999")

ax.legend(frameon=False, loc="upper left")
ax.margins(y=0.12)

plt.tight_layout()
plt.savefig("speed_chart.png", dpi=200)
plt.show()
