"""Стовпчикова діаграма швидкості (символів/с) для 6 комбінацій модель x промпт."""
import csv
import matplotlib.pyplot as plt

with open("results.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

names = {"short": "короткий", "medium": "середній", "long": "довгий"}
labels = [f"{r['model']}\n{names[r['prompt']]}" for r in rows]
values = [float(r["chars_per_s"]) for r in rows]
colors = ["#4C72B0" if r["provider"] == "local" else "#DD8452" for r in rows]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(labels, values, color=colors)
ax.bar_label(bars, fmt="%.0f")
ax.set_ylabel("Символів за секунду")
ax.set_title("Швидкість генерації: локальна vs хмарна модель")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("speed.png", dpi=150)
print("Збережено speed.png")
