import csv
import matplotlib.pyplot as plt

labels, values = [], []
with open("results.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        labels.append(f"{row['provider']}\n{row['prompt']}")
        values.append(float(row["chars_per_s"]))

plt.figure(figsize=(9, 5))
plt.bar(labels, values, color=["#4C72B0"] * 3 + ["#DD8452"] * 3)
plt.ylabel("Символів за секунду")
plt.title("Швидкість генерації: модель × промпт")
plt.tight_layout()
plt.savefig("speed_chart.png", dpi=150)
print("Збережено speed_chart.png")