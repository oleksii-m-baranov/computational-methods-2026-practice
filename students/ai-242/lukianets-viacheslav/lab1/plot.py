"""Крок 5 завдання 4: стовпчикова діаграма символів/с з results.csv."""
import csv
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

with open("results.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

labels = [f"{r['model']}\n{r['prompt']}" for r in rows]
values = [float(r["chars_per_s"]) for r in rows]
colors = ["tab:blue" if r["provider"] == "local" else "tab:orange" for r in rows]

plt.figure(figsize=(10, 5))
plt.bar(labels, values, color=colors)
plt.ylabel("символів / с")
plt.title("Швидкість генерації: модель × промпт (синій — локальна, помаранчевий — хмарна)")
plt.xticks(fontsize=8)
plt.tight_layout()
plt.savefig("speed_chart.png", dpi=150)
