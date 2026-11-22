
from pathlib import Path
import re

for name in ["none", "trim", "trim+state"]:
    for repeat in range(1, 4):
        path = Path("logs") / f"clean18nov_{name}_r{repeat}.log"

        print("\n" + "=" * 60)
        print(path.name)

        if not path.exists():
            print("Файл не знайдено")
            continue

        text = path.read_text(encoding="utf-8", errors="replace")

        progress = re.findall(r"ПРОГРЕС ПЛАНУ: (\d+/18)", text)
        calls = [line for line in text.splitlines() if "виклик" in line]

        stops = [
            line for line in text.splitlines()
            if any(word in line for word in [
                "Виконано",
                "Передчасна фінальна",
                "ліміт кроків",
                "ВІДПОВІДЬ:"
            ])
        ]

        print("Прогрес:", progress[-1] if progress else "немає")
        print("Кількість викликів:", len(calls))

        print("Останні виклики:")
        for line in calls[-3:]:
            print(line)

        print("Завершення:")
        for line in stops[-3:]:
            print(line)
