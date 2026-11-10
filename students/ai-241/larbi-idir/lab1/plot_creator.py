import matplotlib.pyplot as plt
import numpy as np

prompts = ['Короткий', 'Середній', 'Довгий']
local_chars_per_s = [15.3, 76.7, 121.3]
cloud_chars_per_s = [118.4, 895.4, 1808.6]

x = np.arange(len(prompts))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 5))
rects1 = ax.bar(x - width/2, local_chars_per_s, width, label='Локальна (llama3.2:3b)', color='#2b579a')
rects2 = ax.bar(x + width/2, cloud_chars_per_s, width, label='Хмарна (gpt-oss-20b)', color='#41a05d')

ax.set_ylabel('Символів / секунду')
ax.set_title('Швидкість генерації моделей (симв./с)')
ax.set_xticks(x)
ax.set_xticklabels(prompts)
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

for rect in rects1 + rects2:
    height = rect.get_height()
    ax.annotate(f'{height:.1f}',
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('benchmark_plot.png', dpi=300)
plt.show()