from providers import make_client

TEXT = """Перший в історії публічний платний кіносеанс відбувся 28 грудня 1895 року в Парижі.
Його організували брати Люм'єри. На цьому показі було присутньо всього 33 глядачі. 
Кожен з них заплатив за квиток 1 франк. 
У програмі було показано 10 короткометражних фільмів загальною тривалістю близько 20 хвилин."""

TASKS = {
    "1_fact":     "Рік першого публічного кінопоказу братів Люм'єр. Відповідай лише роком.",
    "2_format":   "JSON: event, year, city для першого публічного кінопоказу братів Люм'єр. Без пояснень, без markdown, лише JSON.",
    "3_summary":  "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code":     "Напиши функцію top_rated(films, n) — n найкращих за рейтингом. Лише код.",
    "5_logic":    "Зал 180 місць, сеанс 1 год 45 хв + 15 хв перерва, робота з 10:00 до 23:00. Скільки сеансів і глядачів?. Покажи хід розв'язання.",
    "6_language": "Чим документальне кіно відрізняється від художнього. Поясни українською, два абзаци.",
}

with open("quality_results.txt", "w", encoding="utf-8") as f:
    for provider in ["local", "cloud"]:
        client, model = make_client(provider)
        f.write(f"\n{'='*50}\nПРОВАЙДЕР: {provider} ({model})\n{'='*50}\n")
        
        for task_id, prompt in TASKS.items():
            f.write(f"\n--- ЗАВДАННЯ: {task_id} ---\n")
            for run in range(1, 3):
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                ans = response.choices[0].message.content
                f.write(f"Прогін {run}:\n{ans}\n\n")
