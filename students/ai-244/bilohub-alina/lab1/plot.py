import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LABELS = {"short": "короткий", "medium": "середній", "long": "довгий"}

with open("results.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

names = []
values = []
for r in rows:
    where = "локальна" if r["provider"] == "local" else "хмарна"
    names.append(f"{where}\n{LABELS[r['prompt']]}")
    values.append(float(r["chars_per_s"]))

colors = ["#4C78A8" if r["provider"] == "local" else "#F58518" for r in rows]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(names, values, color=colors)
ax.bar_label(bars, fmt="%.0f")
ax.set_ylabel("Швидкість, символів за секунду")
ax.set_title("Швидкість генерації: модель × промпт")
plt.tight_layout()
plt.savefig("speed_chart.png", dpi=150)
print("Діаграму збережено у speed_chart.png")
