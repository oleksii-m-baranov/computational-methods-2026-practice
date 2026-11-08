from providers import make_client
import json

TEXT = "Перші сучасні Олімпійські ігри пройшли у 1896 році в місті Афіни, Греція. У змаганнях взяли участь 241 спортсмен із 14 країн світу, які змагалися у 9 видах спорту. Найбільшу кількість медалей завоювала команда США — 11 золотих нагород. Ігри тривали 10 днів, завершившись 15 квітня 1896 року."

TASKS = {
    "1_fact":     "Рік перших сучасних Олімпійських ігор. Відповідай лише роком.",
    "2_format":   "Сформуй JSON з полями event, year, city для перших сучасних Олімпійських ігор. Без пояснень, без markdown, лише JSON.",
    "3_summary":  "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code":     "Напиши функцію win_rate(results), яка приймає список результатів у вигляді рядків 'W', 'L', 'D' та повертає відсоток перемог (wins / total). Лише код.",
    "5_logic":    "8 команд грають у турнірі кожна з кожною по разу. Скільки всього буде матчів? Якщо за день проводиться 4 матчі, скільки днів триватиме турнір? Покажи хід розв'язання.",
    "6_language": "Поясни українською, чим спринт відрізняється від стаєрського бігу. Два абзаци.",
}

results = {}

for provider in ["local", "cloud"]:
    client, model = make_client(provider)
    results[model] = {}
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):          # два прогони на завдання
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            answers.append(r.choices[0].message.content)
        results[model][task_id] = answers
        print(f"{model} / {task_id} — готово")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)