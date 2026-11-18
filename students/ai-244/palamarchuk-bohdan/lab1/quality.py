import sys
import os
import json
import time
from providers import make_client

TEXT = """Перші сучасні Олімпійські ігри відбулися в Афінах і тривали з 6 по 15 квітня 1896 року. Вони проходили під егідою Міжнародного олімпійського комітету. У змаганнях узяв участь 241 спортсмен із 14 країн. Розіграли 43 комплекти медалей у 9 видах спорту. Ігри пройшли з великим успіхом, і після них лунали заклики проводити всі наступні Олімпіади саме в Афінах. Проте наступні змагання вже були заплановані в Парижі, тож до Греції Олімпійські ігри повернулися лише через 108 років, у 2004 році."""

TASKS = {
    "1_fact":     "У якому році відбулися перші сучасні Олімпійські ігри? Відповідай лише роком.",
    "2_format":   "Дай інформацію про перші сучасні Олімпійські ігри у форматі JSON з полями event, year, city. Без пояснень, без markdown, лише JSON.",
    "3_summary":  "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code":     "Напиши функцію Python win_rate(results), яка приймає список результатів матчів зі значеннями \"W\", \"L\", \"D\" і повертає частку перемог. Лише код.",
    "5_logic":    "8 команд грають турнір, кожна з кожною по одному разу. Скільки всього матчів? Якщо грати по 4 матчі на день, скільки днів триватиме турнір? Покажи хід розв'язання.",
    "6_language": "Чим спринт відрізняється від стаєрського бігу. Поясни українською, два абзаци.",
}

PAUSE = {"cloud": 15}   # пауза між запитами до хмари, щоб не впертися в ліміт
FILE = "quality.json"

def ask(client, model, prompt):
    for _ in range(6):
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return r.choices[0].message.content
        except Exception as e:
            print("ПОМИЛКА:", str(e)[:300])
            print("повтор через 65 с")
            time.sleep(65)
    raise RuntimeError("не вдалося виконати запит")

results = {}
if os.path.exists(FILE):
    with open(FILE, encoding="utf-8") as f:
        results = json.load(f)

for provider in sys.argv[1:] or ["local", "qwen", "cloud"]:
    client, model = make_client(provider)
    results.setdefault(model, {})
    for task_id, prompt in TASKS.items():
        if len(results[model].get(task_id, [])) == 2:
            continue                       # це завдання вже пораховане
        answers = []
        for attempt in range(2):           # два прогони на завдання
            answers.append(ask(client, model, prompt))
            time.sleep(PAUSE.get(provider, 0))
        results[model][task_id] = answers
        print(f"{model} / {task_id} - готово")
        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
