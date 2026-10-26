import csv
import matplotlib.pyplot as plt

NAMES = {"short": "короткий", "medium": "середній", "long": "довгий"}

with open("results.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

labels = [f"{r['model']}\n{NAMES[r['prompt']]}" for r in rows]
values = [float(r["chars_per_s"]) for r in rows]
colors = ["tab:blue" if r["provider"] == "local" else "tab:orange" for r in rows]

plt.figure(figsize=(10, 5))
bars = plt.bar(labels, values, color=colors)
plt.bar_label(bars, fmt="%.1f")
plt.ylabel("Символів за секунду")
plt.title("Швидкість генерації: модель × промпт")
plt.tight_layout()
plt.savefig("chart.png", dpi=150)
plt.show()
