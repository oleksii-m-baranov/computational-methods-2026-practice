import csv
import matplotlib.pyplot as plt
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Читаємо results.csv
rows = []
with open("results.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append(r)

# Формуємо підписи й значення
labels = []
values = []

for r in rows:
    label = f"{r['provider']}\n{r['prompt']}"
    labels.append(label)
    values.append(float(r["chars_per_s"]))

# Будуємо діаграму
fig, ax = plt.subplots(figsize=(10, 6))
colors = ["#e74c3c"] * 3 + ["#3498db"] * 3
bars = ax.bar(labels, values, color=colors)

# Підписуємо стовпці значеннями
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
            f"{val:.1f}", ha="center", fontsize=10)

ax.set_ylabel("Швидкість, символів/с")
ax.set_title("Швидкість генерації: локальна (червона) vs хмарна (синя)")
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("chart.png", dpi=150)
print("Збережено: chart.png")
