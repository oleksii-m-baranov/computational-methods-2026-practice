import matplotlib.pyplot as plt
import numpy as np

prompts = ['Короткий промпт', 'Середній промпт', 'Довгий промпт']
local_speeds = [112.3, 139.6, 131.8]
cloud_speeds = [100.7, 1066.6, 1853.4]

x = np.arange(len(prompts))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))

rects1 = ax.bar(x - width/2, local_speeds, width, label='Локальна (llama3.2:3b)', color='#4c72b0')
rects2 = ax.bar(x + width/2, cloud_speeds, width, label='Хмарна (gpt-oss-20b)', color='#dd8452')

ax.set_ylabel('Швидкість генерації (символів/с)', fontsize=12)
ax.set_title('Порівняння швидкості локальної та хмарної моделі за типами промптів', fontsize=14, pad=15)
ax.set_xticks(x)
ax.set_xticklabels(prompts, fontsize=11)
ax.legend(fontsize=11)

ax.bar_label(rects1, padding=3, fmt='%.1f', fontsize=9)
ax.bar_label(rects2, padding=3, fmt='%.1f', fontsize=9)

plt.tight_layout()
plt.savefig('chart.png', dpi=300)
print('Стовпчикову діаграму успішно згенеровано та збережено у файл chart.png!')