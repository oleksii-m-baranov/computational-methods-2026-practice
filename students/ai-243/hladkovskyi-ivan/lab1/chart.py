"""Стовпчикова діаграма: символи за секунду для 6 комбінацій модель x промпт."""
import csv
import matplotlib.pyplot as plt

with open("results.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

labels = [f"{'local' if r['provider'] == 'local' else 'cloud'}\n{r['prompt']}" for r in rows]
values = [float(r["chars_per_s"]) for r in rows]
colors = ["#4C72B0" if r["provider"] == "local" else "#DD8452" for r in rows]
models = {r["provider"]: r["model"] for r in rows}

fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.bar(labels, values, color=colors)
ax.bar_label(bars, padding=2)
ax.set_ylabel("Символів за секунду")
ax.set_title(f"Швидкість генерації: локальна ({models.get('local')}) vs хмарна ({models.get('cloud')})")
fig.tight_layout()
fig.savefig("speed_chart.png", dpi=150)
print("Збережено speed_chart.png")
