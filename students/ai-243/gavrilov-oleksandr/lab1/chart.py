import matplotlib.pyplot as plt
import pandas as pd

# 1. Зчитуємо дані з твого файлу
df = pd.read_csv("results.csv")

# 2. Створюємо підписи для вісі X (наприклад, "local\nshort")
df["label"] = df["provider"] + "\n" + df["prompt"]

# 3. Налаштовуємо кольори: синій для local, помаранчевий для cloud
colors = ["#1f77b4" if prov == "local" else "#ff7f0e" for prov in df["provider"]]

# 4. Малюємо діаграму
plt.figure(figsize=(10, 6))
bars = plt.bar(df["label"], df["chars_per_s"], color=colors, edgecolor="black")

# Додаємо точні цифри над кожним стовпчиком
for bar in bars:
    yval = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        yval + (yval * 0.02),
        f"{yval:.1f}",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )

# 5. Оформлюємо графік
plt.title("Швидкість генерації тексту (Символи за секунду)", fontsize=14, pad=15)
plt.ylabel("Символів за секунду (chars_per_s)", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

# 6. Зберігаємо як картинку
plt.savefig("chart.png", dpi=300)
print("Готово! Діаграму збережено у файл chart.png")
