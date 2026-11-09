from providers import make_client
import json
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

TEXT = """За даними поточної погоди для локації Одеса, Одеська область, зараз сонячно.
Температура повітря становить 22°C, проте відчувається як 24°C.
Спостерігається східний вітер зі швидкістю 3 милі на годину.
Вологість повітря складає 47%, а ймовірність дощу дорівнює 0%.
Ультрафіолетовий індекс знаходиться на позначці 5.
Протягом дня максимальна температура сягне 23°C, а мінімальна становитиме 14°C."""

TASKS = {
    "1_fact": "Рік відкриття нинішньої будівлі Одеського оперного театру. Відповідай лише роком.",
    "2_format": "Рік відкриття нинішньої будівлі Одеського оперного театру. JSON: event, year, city. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа: \n\n" + TEXT,
    "4_code": "is_palindrome(s), ігнорує пробіли й регістр. Лише код.",
    "5_logic": "Зал 180 місць, сеанс 1 год 45 хв + 15 хв перерва, робота з 10:00 до 23:00. Скільки сеансів і глядачів? Покажи хід розв'язання.",
    "6_language": "Чим хостел відрізняється від готелю. Поясни українською, два абзаци.",
}

results = {}

# for provider in ["local_llama", "local_qwen", "cloud"]:
for provider in ["cloud"]:
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
