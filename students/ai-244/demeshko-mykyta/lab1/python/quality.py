import json
from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

TEXT = """Грошова реформа в незалежній Україні відбулася в період з 2 по 16 вересня 1996 року.
Національний банк України ввів у готівковий обіг перші банкноти номіналом від 1 до 100 гривень.
Обмін здійснювався за фіксованим курсом 100000 українських карбованців за одну нову гривню.
За перші 15 днів реформи з обігу було вилучено понад 311 трильйонів карбованців.
Офіційний курс нової національної валюти на момент введення становив 1,76 гривні за 1 долар США.
Загалом під час реформи населення успішно обміняло понад 97% усієї маси старих купоно-карбованців."""

TASKS = {
    "1_fact": "Рік уведення гривні як національної валюти. Відповідай лише роком.",
    "2_format": "Рік уведення гривні як національної валюти. JSON: currency, code, year. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни до двох речень, збережи всі числа: \n\n" + TEXT,
    "4_code": "compound_interest(principal, rate, years). Лише код.",
    "5_logic": "Депозит 20000 грн під 12% річних, податок 19,5% з відсотків. Скільки на руках через рік? Покажи хід розв'язання.",
    "6_language": "Чим акція відрізняється від облігації?. Поясни українською, два абзаци.",
}

PROVIDERS_TO_TEST = ["local_llama", "local_qwen", "cloud"]

try:
    with open("quality.json", "r", encoding="utf-8") as f:
        results = json.load(f)
except Exception:
    results = {}

for provider in PROVIDERS_TO_TEST:
    client, model = make_client(provider)

    if model in results and len(results[model]) == len(TASKS):
        print(f"\n[SKIP] Дані для {model} ({provider}) вже є у quality.json, пропускаємо.")
        continue

    print(f"\n>>> Запуск генерації для: {model} ({provider})")
    results[model] = {}

    for task_id, prompt in TASKS.items():
        answers = []
        print(f"  Виконуємо {task_id} (2 спроби)...")
        for attempt in range(2):
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            ans = r.choices[0].message.content.strip()
            answers.append(ans)
        results[model][task_id] = answers
        logger.info(f"{model} / {task_id} — готово")

        with open("quality.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

print("\nВсі три моделі успішно збережено у quality.json!")