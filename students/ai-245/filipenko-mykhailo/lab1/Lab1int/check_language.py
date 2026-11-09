import json
import re

with open("quality.json", "r", encoding="utf-8") as file:
    data = json.load(file)

print("ПЕРЕВІРКА УКРАЇНСЬКОЇ МОВИ")

for model, tasks in data.items():
    print("\nМодель:", model)

    total = 0
    ukrainian = 0

    for task_name, runs in tasks.items():
        for result in runs:
            answer = str(result.get("answer", ""))
            total += 1

            # Поширені українські літери та слова
            has_ukrainian_letters = bool(
                re.search(r"[іїєґІЇЄҐ]", answer)
            )

            ukrainian_words = [
                "це", "що", "для", "який",
                "яка", "від", "між", "та",
                "планета", "зірка", "відповідь"
            ]

            words = re.findall(
                r"[а-яіїєґА-ЯІЇЄҐ]+",
                answer.lower()
            )

            has_ukrainian_words = any(
                word in ukrainian_words for word in words
            )

            detected = (
                has_ukrainian_letters or has_ukrainian_words
            )

            if detected:
                ukrainian += 1

            print(
                f"{task_name}, прогін {result['run']}:",
                "UA-ознаки" if detected else "НЕ ВИЯВЛЕНО"
            )

    print(f"\nВиявлено UA-ознаки: {ukrainian}/{total}")
    print(
        f"Частка: {ukrainian / total * 100:.1f}%"
        if total else "Немає результатів"
    )

print("\nПеревірку завершено!")
