import csv
import matplotlib.pyplot as plt

with open("benchmark_results.csv", encoding="utf-8-sig") as file:
    data = list(csv.DictReader(file))

labels = [
    f"{row['model']}\n{row['start_type']} {row['run']}"
    for row in data
]

speeds = [
    float(row["chars_per_second"].replace(",", "."))
    for row in data
]

plt.figure(figsize=(11, 6))
bars = plt.bar(labels, speeds)

plt.title("Швидкість генерації локальних моделей")
plt.ylabel("Символів за секунду")
plt.xlabel("Модель і тип запуску")

for bar, speed in zip(bars, speeds):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2,
        f"{speed:.2f}",
        ha="center"
    )

plt.ylim(0, max(speeds) * 1.2)
plt.tight_layout()
plt.savefig("benchmark_chart.png", dpi=200)
plt.show()

print("Діаграму збережено: benchmark_chart.png")
