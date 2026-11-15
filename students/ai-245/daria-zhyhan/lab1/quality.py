
from providers import make_client
import json
import time

TEXT = """
У 1992 році в Україні використовували купоно-карбованці.
Грошова реформа відбулася з 2 до 16 вересня 1996 року.
У результаті реформи національною валютою стала гривня.
За 1 гривню обмінювали 100000 карбованців.
Одна гривня дорівнює 100 копійкам.
Літерний код української валюти — UAH, а цифровий — 980.
"""

TASKS = {
    "1_fact": (
        "У якому році гривню ввели як національну "
        "валюту України? Відповідай лише роком."
    ),
    "2_format": (
        "Надай інформацію про українську гривню "
        "у форматі JSON з полями currency, code, year. "
        "Без пояснень, без markdown, лише JSON."
    ),
    "3_summary": (
        "Стисни наступний текст до двох речень, "
        "збережи всі числа:\n\n" + TEXT
    ),
    "4_code": (
        "Напиши функцію Python "
        "compound_interest(principal, rate, years), "
        "яка обчислює кінцеву суму за формулою "
        "складних відсотків із щорічною капіталізацією. "
        "rate передається у відсотках. Лише код."
    ),
    "5_logic": (
        "Депозит становить 20000 грн під 12% річних. "
        "Податок 19,5% стягується з нарахованих відсотків. "
        "Скільки грошей буде на руках через один рік? "
        "Покажи хід розв'язання."
    ),
    "6_language": (
        "Поясни різницю між акцією та облігацією. "
        "Поясни українською мовою, два абзаци."
    )
}

MODELS = [
    ("local", "llama3.2:3b"),
    ("local", "qwen3:4b"),
    ("cloud", "openai/gpt-oss-120b")
]

results = {}

for provider, model in MODELS:
    client, _ = make_client(provider)
    results[model] = {}

    print(f"\n===== МОДЕЛЬ: {model} =====", flush=True)

    for task_id, prompt in TASKS.items():
        answers = []

        for attempt in range(2):
            print(
                f"{task_id}, запуск {attempt + 1}...",
                flush=True
            )

            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    timeout=180
                )

                answer = response.choices[0].message.content or ""

            except Exception as e:
                answer = f"ПОМИЛКА ЗАПИТУ: {e}"

            answers.append(answer)

        results[model][task_id] = answers
        print(f"{model} / {task_id} — готово", flush=True)

        with open("quality.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

print("\nУсі результати збережено у quality.json")
