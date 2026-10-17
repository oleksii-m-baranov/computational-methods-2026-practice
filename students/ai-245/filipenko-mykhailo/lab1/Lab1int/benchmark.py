import time
import csv
from providers import ask_model

# Варіант 9
prompt = "Поясни різницю між функцією і методом. Коротко."

models = ["llama3.2:3b", "qwen3:4b"]
results = []

for model in models:
    print(f"\nТестування моделі: {model}")

    times = []

    for i in range(3):
        print(f"\nЗапуск {i + 1}")

        start = time.perf_counter()
        answer = ask_model(prompt, model)
        duration = time.perf_counter() - start

        print("Відповідь:", answer)
        print(f"Час: {duration:.2f} секунд")

        times.append(duration)
        results.append([model, i + 1, round(duration, 2)])

    average = sum(times) / len(times)
    print(f"\nСередній час {model}: {average:.2f} секунд")

with open("results.csv", "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["model", "run", "time_seconds"])
    writer.writerows(results)

print("\nТестування завершено!")
print("Результати збережено у results.csv")