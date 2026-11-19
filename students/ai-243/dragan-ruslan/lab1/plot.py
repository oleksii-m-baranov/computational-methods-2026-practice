import csv
import matplotlib.pyplot as plt

# Зчитування даних із файлу results.csv
labels = []
speeds = []
colors = []

with open("results.csv", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Формуємо зрозумілу мітку для осі X: наприклад, "llama3.2:3b\n(короткий)"
        label = f"{row['model']}\n({row['prompt']})"
        labels.append(label)
        speeds.append(float(row["chars_per_s"]))
        
        # Кольори: локальна — синій, хмарна — помаранчевий
        if row["provider"] == "local":
            colors.append("skyblue")
        else:
            colors.append("orange")

# Побудова стовпчикової діаграми
plt.figure(figsize=(10, 6))
bars = plt.bar(labels, speeds, color=colors, edgecolor="black")

# Додавання підписів та заголовків
plt.xlabel("Комбінація (Модель × Промпт)", fontsize=12)
plt.ylabel("Швидкість (символів / с)", fontsize=12)
plt.title("Порівняння швидкості генерації (симв./с)", fontsize=14, fontweight="bold")
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Додавання числових значень над стовпчиками
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2.0,
        height + 10,
        f"{height:.1f}",
        ha="center",
        va="bottom",
        fontsize=10,
    )

plt.tight_layout()

# Збереження графіка у файл та показ
plt.savefig("speed_chart.png", dpi=300)
print("Діаграму успішно збережено у файл 'speed_chart.png'!")
