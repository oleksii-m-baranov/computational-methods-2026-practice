from providers import make_client
import json
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

TEXT = """Перші сучасні Олімпійські ігри відбулися у 1896 році в Афінах. 
У змаганнях взяли участь 241 спортсмен із 14 країн світу. 
Програма ігор включала 43 комплекти нагород у 9 видах спорту. 
Найбільше медалей здобула команда Греції, виборовши 46 нагород різного ґатунку. 
Змагання тривали з 6 по 15 квітня 1896 року."""

TASKS = {
    "1_fact": (
        "Вкажи рік проведення перших сучасних Олімпійських ігор. Відповідай"
        " лише роком."
    ),
    "2_format": (
        "Створи JSON з полями event, year, city для перших сучасних Олімпійських"
        " ігор. Без пояснень, без markdown, лише JSON."
    ),
    "3_summary": (
        "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT
    ),
    "4_code": (
        "Напиши функцію win_rate(results), яка приймає список символів 'W',"
        " 'L', 'D' і повертає відсоток перемог ('W') від загальної кількості ігор."
        " Лише код."
    ),
    "5_logic": (
        "У турнірі беруть участь 8 команд, кожна грає з кожною по одному разу."
        " Скільки всього матчів буде зіграно? Якщо проводити по 4 матчі на день,"
        " скільки днів триватиме турнір? Покажи хід розв'язання."
    ),
    "6_language": (
        "Поясни, чим спринтерський біг відрізняється від стаєрського. Поясни"
        " українською, два абзаци."
    ),
}

results = {}

# for provider in ["local_llama", "local_qwen", "cloud"]:
for provider in ["local_qwen"]:
    client, model = make_client(provider)
    results[model] = {}

    for task_id, prompt in TASKS.items():
        answers = []

        for attempt in range(2):  # два прогони на завдання
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            answers.append(r.choices[0].message.content)
        results[model][task_id] = answers
        logger.info(f"{model} / {task_id} — готово")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
