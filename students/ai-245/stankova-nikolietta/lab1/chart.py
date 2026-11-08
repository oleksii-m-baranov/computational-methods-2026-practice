import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results.csv")

labels = []
values = []
colors = []

for _, row in df.iterrows():

    labels.append(f"{row['provider']}\n{row['prompt']}")

    if str(row["chars_per_s"]) == "ERROR":
        values.append(0)
        colors.append("red")
    else:
        values.append(float(row["chars_per_s"]))
        colors.append("steelblue")

plt.figure(figsize=(10, 5))

bars = plt.bar(
    labels,
    values,
    color=colors
)

for i, value in enumerate(values):

    if value == 0:
        plt.text(
            i,
            0.3,
            "ERROR",
            ha="center",
            color="red",
            fontweight="bold"
        )
    else:
        plt.text(
            i,
            value + 0.3,
            str(value),
            ha="center"
        )

plt.title("Швидкість генерації тексту")
plt.xlabel("Модель та промпт")
plt.ylabel("Символів за секунду")

plt.tight_layout()

plt.savefig("chart.png")
plt.show()

print("chart.png створено")