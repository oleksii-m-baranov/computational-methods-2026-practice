from providers import make_client
import json
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

TEXT = """Футбол залишається найпопулярнішим видом спорту у світі, збираючи біля екранів понад 3 мільярди 
вболівальників під час фіналів Чемпіонату світу. Баскетбольний майданчик має 
стандартні розміри 28 метрів у довжину та 15 метрів у ширину, що вимагає від гравців 
постійного руху та неабиякої витривалості. Видатний легкоатлет Усейн Болт встановив 
свій знаменитий світовий рекорд у 2009 році, пробігши дистанцію 100 метрів усього за 
9,58 секунди. Водночас професійний тенісний матч може тривати від 1 до 5 годин, 
залежно від кількості зіграних сетів та напруженості боротьби. А от під час класичного 
марафону бігуни долають виснажливу дистанцію рівно у 42 кілометри і 195 метрів, щоразу 
випробовуючи межі людських можливостей."""

TASKS = {
    "1_fact": "Рік перших сучасних Олімпійських ігор. Відповідай лише роком.",
    "2_format": "Рік перших сучасних Олімпійських ігор. JSON: event, year, city. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа: \n\n" + TEXT,
    "4_code": "win_rate(results) зі списку “W”/“L”/“D”. Лише код.",
    "5_logic": "8 команд, кожна з кожною по разу. Скільки матчів? При 4 матчах на день — скільки днів? Покажи хід розв'язання.",
    "6_language": "Чим спринт відрізняється від стаєрського бігу. Поясни українською, два абзаци.",
}

results = {}


# for provider in ["cloud"]:
for provider in ["local_llama", "local_qwen", "cloud"]:
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
