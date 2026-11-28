import json
from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger("task5_quality", overwrite=True)

TEXT = (
    "За звітом Міжнародного агентства з відновлюваної енергетики (IRENA), у 2024 році "
    "глобальні потужності зеленої енергетики зросли на 585 ГВт, що на 15% більше за "
    "показник попереднього року. Частка відновлюваних джерел сягнула 46% у загальній "
    "встановленій потужності електростанцій світу, а серед усіх нових об'єктів генерації "
    "вони забезпечили 92%. Головним рушієм зростання стала сонячна енергетика, на яку "
    "припало 452 ГВт нових потужностей. Вітрова енергетика додала ще 113 ГВт, зберігши "
    "друге місце серед нових відновлюваних станцій. У Європейському Союзі частка відновлюваних джерел "
    "у виробництві електроенергії у 2024 році досягла 50%, а в другому кварталі 2025 року "
    "піднялася до 54%."
)

TASKS = {
    "1_fact": "Рік підписання Паризької кліматичної угоди. Відповідай лише роком.",
    "2_format": "Рік підписання Паризької кліматичної угоди. JSON: agreement, year, city. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію Python sort_waste(items), яка групує переданий список елементів items за словником категорій (пластик, скло, папір, органіка) у словник вигляду {категорія: [елементи]}. Лише код.",
    "5_logic": "500 т сміття: 40% органіка, 25% пластик. Переробляють 60% пластику. Скільки тонн пластику на полігон? Покажи хід розв'язання.",
    "6_language": "Чим відновлювані джерела енергії відрізняються від невідновлюваних. Поясни українською, два абзаци.",
}

results = {}

for provider in ["local", "local_qwen", "cloud"]:
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
            content = r.choices[0].message.content or ""
            answers.append(content)
            if task_id == "2_format":
                try:
                    json.loads(content)
                    logger.info(f"  [{model}] 2_format attempt {attempt + 1}: json.loads OK")
                except Exception as exc:
                    logger.info(f"  [{model}] 2_format attempt {attempt + 1}: json.loads FAIL ({exc})")
        results[model][task_id] = answers
        logger.info(f"{model} / {task_id} — готово")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
logger.info("Saved quality.json")
