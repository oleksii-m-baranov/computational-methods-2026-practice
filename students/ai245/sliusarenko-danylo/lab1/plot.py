import csv
import matplotlib.pyplot as plt
import numpy as np

# Зчитуємо дані з results.csv
data = {"local": {}, "cloud": {}}

with open("results.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        provider = row["provider"]
        prompt = row["prompt"]
        speed = float(row["chars_per_s"])
        data[provider][prompt] = speed

prompts_order = ["short", "medium", "long"]
labels = ["Короткий запит", "Середній запит", "Довгий запит"]

local_speeds = [data["local"][p] for p in prompts_order]
cloud_speeds = [data["cloud"][p] for p in prompts_order]

x = np.arange(len(labels))
width = 0.32

# Налаштування стилю
fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="#F8FAFC")
ax.set_facecolor("#FFFFFF")

# Нові кольори: стильний індиго та смарагдовий бірюзовий
bar1 = ax.bar(
    x - width / 2,
    local_speeds,
    width,
    label="Локальна (Llama 3.2 3B)",
    color="#4F46E5",
    edgecolor="#3730A3",
    linewidth=1.2,
    zorder=3,
)
bar2 = ax.bar(
    x + width / 2,
    cloud_speeds,
    width,
    label="Хмарна (Gemini 2.5 Flash)",
    color="#0D9488",
    edgecolor="#115E59",
    linewidth=1.2,
    zorder=3,
)

# Заголовок та підписи осей
ax.set_title(
    "Порівняння пропускної здатності генерації (симв/с)",
    fontsize=13,
    fontweight="bold",
    pad=18,
    color="#0F172A",
)
ax.set_ylabel("Швидкість генерації, симв./с", fontsize=11, fontweight="medium", color="#334155")
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=11, color="#1E293B", fontweight="medium")

# Легенда
ax.legend(
    frameon=True,
    facecolor="#F8FAFC",
    edgecolor="#E2E8F0",
    fontsize=10,
    loc="upper left",
)

# М'яка сітка
ax.grid(axis="y", linestyle=":", alpha=0.7, color="#CBD5E1", zorder=0)

# Прибираємо рамки зверху, праворуч і ліворуч для чистого сучасного вигляду
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#94A3B8")
ax.tick_params(left=False, colors="#64748B")

# Підписи з контрастними підкладками над стовпчиками
def add_labels(bars, color):
    for bar in bars:
        h = bar.get_height()
        ax.annotate(
            f"{h:.1f}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color=color,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#F1F5F9", edgecolor="none", alpha=0.8),
        )

add_labels(bar1, "#3730A3")
add_labels(bar2, "#115E59")

# Запас зверху, щоб плашки не впиралися в край графіка
ax.set_ylim(0, max(cloud_speeds) * 1.15)

plt.tight_layout()
plt.savefig("benchmark_plot.png", dpi=300)
print("Новий графік збережено у benchmark_plot.png")
plt.show()