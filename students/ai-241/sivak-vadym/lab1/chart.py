"""Завдання 4, крок 5. Стовпчикова діаграма швидкості (симв./с) з results.csv."""
import csv

import matplotlib.pyplot as plt

PROMPT_UA = {"short": "короткий", "medium": "середній", "long": "довгий"}
COLORS = {"local": "#4C72B0", "cloud": "#DD8452"}

with open("results.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

labels = [f"{r['model'].split('/')[-1]}\n{PROMPT_UA[r['prompt']]}" for r in rows]
values = [float(r["chars_per_s"]) for r in rows]
colors = [COLORS[r["provider"]] for r in rows]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(labels, values, color=colors)
ax.bar_label(bars, fmt="%.1f")
ax.set_ylabel("Символів за секунду (медіана з 3)")
ax.set_title("Швидкість генерації: модель × промпт")
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for c in COLORS.values()],
          labels=["локальна", "хмарна"])
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig("speed_chart.png", dpi=150)
print("Збережено speed_chart.png")
