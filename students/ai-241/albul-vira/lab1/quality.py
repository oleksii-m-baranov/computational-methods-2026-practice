from providers import make_client
import json
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

TEXT = """Одеський національний університет імені І. І. Мечникова — один із найстаріших вищих навчальних закладів України. Він був заснований 13 травня 1865 року як Імператорський Новоросійський університет. На момент відкриття в університеті навчалося 175 студентів на трьох факультетах. Наразі в ОНУ навчається понад 10000 студентів та працюють близько 1300 викладачів. Університет включає 11 факультетів та 4 навчально-наукові інститути."""

TASKS = {
    "1_fact":     "Рік заснування Одеського національного університету імені І. І. Мечникова. Відповідай лише роком.",
    "2_format":   "Створи JSON з полями name, year, city для Одеського національного університету імені І. І. Мечникова. Без пояснень, без markdown, лише JSON.",
    "3_summary":  "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT, 
    "4_code":     "Напиши функцію is_palindrome(s), яка перевіряє, чи є рядок паліндромом, ігноруючи пробіли й регістр. Лише код.",
    "5_logic":    "У групі 25 студентів, 12 знають Python, 9 Java, 4 обидві. Скільки не знають жодної? Покажи хід розв'язання.",
    "6_language": "Чим стек відрізняється від черги? Поясни українською, два абзаци.",
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
