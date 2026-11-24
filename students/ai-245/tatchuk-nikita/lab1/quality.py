from providers import make_client
import json

TEXT = """Паризьку угоду ухвалили 12 грудня 2015 року всі 196 сторін Рамкової конвенції ООН про зміну клімату на конференції COP21 у Парижі. Угоду відкрили для підписання 22 квітня 2016 року в штаб-квартирі ООН у Нью-Йорку. Того дня її підписали 175 сторін — 174 країни та Європейський Союз, що стало рекордом для першого дня підписання міжнародного договору. Щоб угода набрала чинності, її мали ратифікувати щонайменше 55 сторін, на які припадає не менше 55 % світових викидів парникових газів. Цей поріг було досягнуто 5 жовтня 2016 року, і 4 листопада 2016 року угода набрала чинності."""

TASKS = {
    "1_fact": "Рік підписання Паризької кліматичної угоди. Відповідай лише роком.",
    "2_format": "JSON: agreement, year, city для Паризької кліматичної угоди. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію sort_waste(items), яка сортує відходи за словником категорій. Лише код.",
    "5_logic": "500 т сміття: 40% органіка, 25% пластик. Переробляють 60% пластику. Скільки тонн пластику на полігон? Покажи хід розв'язання.",
    "6_language": "Чим відновлювані джерела енергії відрізняються від невідновлюваних. Поясни українською, два абзаци.",
}

results = {}
for provider in ["local", "local_qwen", "cloud"]:
    client, model = make_client(provider)
    results[model] = {}
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):  
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

for model, tasks in results.items():
    for i, answer in enumerate(tasks["2_format"], 1):
        try:
            json.loads(answer)
            verdict = "2 бали — парситься без правок"
        except json.JSONDecodeError:
            stripped = answer.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            start, end = stripped.find("{"), stripped.rfind("}")
            try:
                json.loads(stripped[start:end + 1])
                verdict = "1 бал — парситься після видалення обгортки"
            except json.JSONDecodeError:
                verdict = "0 балів — не парситься"
        print(f"{model} / прогін {i}: {verdict}")
