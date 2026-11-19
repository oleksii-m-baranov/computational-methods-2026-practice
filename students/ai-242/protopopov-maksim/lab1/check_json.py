import json

with open("quality.json", encoding="utf-8") as f:
    data = json.load(f)

for model, tasks in data.items():
    for answer in tasks["2_format"]:
        try:
            json.loads(answer)
            print(f"{model}: OK, парситься без правок")
        except json.JSONDecodeError:
            # пробуем срезать markdown-обёртку ```json ... ```
            stripped = answer.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            try:
                json.loads(stripped)
                print(f"{model}: парситься тільки після зрізання обгортки (1 бал)")
            except json.JSONDecodeError:
                print(f"{model}: НЕ парситься (0 балів)")