from providers import make_client
import json
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

TEXT = """Одеський національний академічний театр опери та балету є однією з найвизначніших туристичних локацій Півдня України. 
Сучасна будівля театру була побудована у 1887 році за проєктом віденських архітекторів. 
Глядацька зала театру розрахована на 1635 посадкових місць. 
Щороку цю архітектурну пам'ятку відвідують близько 300 тисяч туристів з різних країн світу. 
У 2007 році завершилася масштабна реконструкція будівлі, яка тривала понад 10 років. 
Під час активного туристичного сезону тут щоденно проводиться до 5 організованих екскурсій."""

TASKS = {
    "1_fact": "Рік відкриття нинішньої будівлі Одеського оперного театру. Відповідай лише роком.",
    "2_format": "Рік відкриття нинішньої будівлі Одеського оперного театру. JSON: landmark, city, year. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "trip_cost(days, daily_cost, transport). Лише код.",
    "5_logic": "Поїздка 6 днів: житло 900/добу, їжа 500/день, дорога 2400. Троє, житло й дорога порівну. Скільки заплатить кожен? Покажи хід розв'язання.",
    "6_language": "Чим хостел відрізняється від готелю. Поясни українською, два абзаци.",
}

results = {}
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
