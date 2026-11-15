import json
from providers import make_client


TEXT = """
Гривня була введена в обіг як національна валюта України 2 вересня 1996 року. 
Обмін купоно-карбованців на нову валюту здійснювався за фіксованим курсом 100 000 карбованців за 1 гривню. 
На момент реформи Національний банк України випустив в обіг 3,1 мільярда гривень готівкою. 
Період паралельного обігу обох валют тривав 15 днів і завершився 16 вересня 1996 року.
"""

TASKS = {
    "1_fact": "Рік уведення гривні як національної валюти. Відповідай лише роком.",
    "2_format": "Створи JSON про українську валюту з полями: currency, code, year. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію compound_interest(principal, rate, years), яка рахує суму на руках через рік. Депозит 20000 грн під 12% річних, податок 19,5% з відсотків. Лише код.",
    "5_logic": "8 команд, кожна з кожною по разу. Скільки матчів? При 4 матчах на день - скільки днів? Покажи хід розв'язання.",
    "6_language": "Чим акція відрізняється від облігації. Поясни українською, два абзаци."
}

results = {}

for provider in ["local", "cloud"]:
    client, model = make_client(provider)
    results[model] = {}
    
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):  # два прогони на завдання для перевірки стабільності
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            answers.append(r.choices[0].message.content)
            
        results[model][task_id] = answers
        print(f"{model} / {task_id} - готово")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nОцінювання завершено. Результати збережено у quality.json")