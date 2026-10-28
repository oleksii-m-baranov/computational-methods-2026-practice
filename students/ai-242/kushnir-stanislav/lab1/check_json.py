import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("quality.json", encoding="utf-8") as f:
    data = json.load(f)

for model, tasks in data.items():
    print(f"\n=== {model} ===")
    for attempt, ans in enumerate(tasks["2_format"], 1):
        try:
            json.loads(ans)
            print(f"  Прогін {attempt}: OK (парситься без правок)")
        except json.JSONDecodeError:
            cleaned = ans.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()
            try:
                json.loads(cleaned)
                print(f"  Прогін {attempt}: парситься після зрізання markdown")
            except json.JSONDecodeError:
                print(f"  Прогін {attempt}: НЕ парситься")
        print(f"    Текст: {ans[:200]}")
