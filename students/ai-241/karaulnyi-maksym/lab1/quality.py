from providers import make_client
import json

TEXT = """Одеський національний університет імені І. І. Мечникова — найстаріший вищий навчальний заклад на півдні України, заснований у 1865 році. До складу університету входять 11 факультетів та навчально-наукових інститутів. В університеті навчається понад 10 тисяч студентів за більш ніж 40 спеціальностями. ОНУ імені І. І. Мечникова є потужним науковим центром, який має 4 науково-дослідні інститути та обсерваторію. Це один із провідних закладів вищої освіти в Україні."""

TASKS = {
    "1_fact":     "Рік заснування Одеського національного університету імені І. І. Мечникова. Відповідай лише роком.",
    "2_format":   "Надай інформацію про Одеський національний університет імені І. І. Мечникова у форматі JSON: name, year, city. Без пояснень, без markdown, лише JSON.",
    "3_summary":  "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code":     "Напиши функцію is_palindrome(s), яка ігнорує пробіли й регістр. Лише код.",
    "5_logic":    "У групі 25 студентів, 12 знають Python, 9 Java, 4 обидві. Скільки не знають жодної? Покажи хід розв'язання.",
    "6_language": "Чим стек відрізняється від черги. Поясни українською, два абзаци.",
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