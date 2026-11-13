"""Крок 5 завдання 4: стовпчикова діаграма швидкості (символів за секунду) з results.csv."""
from logsetup import print  # друк іде і в консоль, і в lab1.log
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

with open("results.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

labels = [f"{r['model']}\n{r['prompt']}" for r in rows]
values = [float(r["chars_per_s"]) for r in rows]
colors = ["#4C78A8" if r["provider"] == "local" else "#F58518" for r in rows]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(labels, values, color=colors)
ax.bar_label(bars, fmt="%.1f")
ax.set_ylabel("символів за секунду")
ax.set_title("Швидкість генерації: модель × промпт (медіана з 3 запусків)")
plt.xticks(fontsize=8)
plt.tight_layout()
plt.savefig("chart.png", dpi=150)
print("Збережено chart.png")
