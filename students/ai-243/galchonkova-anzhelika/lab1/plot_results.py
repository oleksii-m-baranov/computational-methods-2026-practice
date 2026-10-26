import matplotlib.pyplot as plt

# Дані з наших вимірювань (chars_per_s)
labels = ['Лок. короткий', 'Лок. середній', 'Лок. довгий', 'Хмар. короткий', 'Хмар. середній', 'Хмар. довгий']
speeds = [9.9, 88.5, 207.9, 3.9, 48.8, 156.4]
colors = ['#4A90E2', '#4A90E2', '#4A90E2', '#F5A623', '#F5A623', '#F5A623']

plt.figure(figsize=(10, 6))
bars = plt.bar(labels, speeds, color=colors)

plt.title('Швидкість генерації (символів за секунду) для моделей і промптів')
plt.xlabel('Комбінація «модель × промпт»')
plt.ylabel('Швидкість, символів/с')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Додаємо значення над стовпчиками
for bar in bars:
    height = bar.get_height()
    plt.annotate(f'{height}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom')

plt.tight_layout()
plt.savefig('speed_chart.png')
plt.show()