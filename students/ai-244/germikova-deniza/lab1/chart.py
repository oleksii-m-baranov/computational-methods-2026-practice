
import matplotlib.pyplot as plt

labels = [
    "Llama 3.2 3B\nкороткий",
    "Llama 3.2 3B\nсередній",
    "Llama 3.2 3B\nдовгий",
    "Gemini Flash\nкороткий",
    "Gemini Flash\nсередній",
]

speeds = [56.5, 127.1, 124.8, 0.2, 6.25]

plt.figure(figsize=(10, 6))
bars = plt.bar(labels, speeds)

plt.title("Швидкість генерації для різних моделей і промптів")
plt.xlabel("Модель і тип промпту")
plt.ylabel("Швидкість, символів/с")
plt.bar_label(bars, fmt="%.2f")

plt.tight_layout()
plt.savefig("chart.png", dpi=300)
plt.show()

