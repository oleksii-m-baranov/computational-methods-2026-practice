import csv
import matplotlib.pyplot as plt

rows = []
with open("results.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows.append(row)

prompts = ["short", "medium", "long"]
prompt_labels = ["Короткий\n(Столиця Індії?)", "Середній\n(Рекурсія)", "Довгий\n(БД, 10 пунктів)"]

local_vals = [float(next(r["chars_per_s"] for r in rows if r["provider"] == "local" and r["prompt"] == p)) for p in prompts]
cloud_vals = [float(next(r["chars_per_s"] for r in rows if r["provider"] == "cloud" and r["prompt"] == p)) for p in prompts]

local_model = next(r["model"] for r in rows if r["provider"] == "local")
cloud_model = next(r["model"] for r in rows if r["provider"] == "cloud")

x = range(len(prompts))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 4.8), dpi=180)
bars1 = ax.bar([i - width / 2 for i in x], local_vals, width, label=f"Локальна ({local_model})", color="#4C78A8")
bars2 = ax.bar([i + width / 2 for i in x], cloud_vals, width, label=f"Хмарна ({cloud_model})", color="#F58518")

ax.set_ylabel("Швидкість генерації, символів/с")
ax.set_title("Порівняння швидкості генерації: локальна vs хмарна модель")
ax.set_xticks(list(x))
ax.set_xticklabels(prompt_labels)
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.4)

for bar in list(bars1) + list(bars2):
    h = bar.get_height()
    ax.annotate(
        f"{h:.1f}",
        xy=(bar.get_x() + bar.get_width() / 2, h),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=9,
    )

ax.set_ylim(0, max(local_vals + cloud_vals) * 1.15)
plt.tight_layout()
plt.savefig("benchmark_chart.png", dpi=180)
print("Saved benchmark_chart.png")
