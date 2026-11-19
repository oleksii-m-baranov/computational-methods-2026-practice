import json
import time

import openai
from providers import make_client

# Абзац 5–6 речень на тему астрономії, щонайменше з трьома числами
# (роки, кількості, відсотки). Вставити ДО першого запуску і більше не міняти.
TEXT = "Гравітаційні хвилі — це своєрідні «хвилі» у просторі-часі, які виникають під час дуже потужних космічних подій. Уперше їх безпосередньо зафіксували у 2015 році, коли зіткнулися дві чорні діри на відстані близько 1,3 млрд світлових років від Землі. Маса цих чорних дір становила приблизно 36 і 29 мас Сонця, а після злиття утворилася чорна діра масою близько 62 Сонць. Решта 3 сонячних мас перетворилася на енергію гравітаційних хвиль за частки секунди. Хвиля змінила довжину 4-кілометрових плечей детектора LIGO приблизно на величину, меншу за 1/10 000 діаметра протона. Цей сигнал став першим прямим доказом існування гравітаційних хвиль, передбачених Альбертом Ейнштейном ще 1916 року."

TASKS = {
    "1_fact": "У якому році відбувся перший політ людини в космос? Відповідай лише роком.",
    "2_format": "Дай JSON з полями event, year, person про перший політ людини в космос. "
                "Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію Python light_travel_time(distance_km), яка повертає час "
              "у секундах, за який світло долає відстань distance_km. Лише код.",
    "5_logic": "Космічний зонд летить зі швидкістю 60000 км/год. Відстань до цілі "
               "480 млн км. Скільки повних діб триватиме політ? Покажи хід розв'язання.",
    "6_language": "Чим зоря відрізняється від планети? Поясни українською, два абзаци.",
}

# local = llama3.2:3b, local_qwen = qwen3:4b, cloud = Gemini (див. providers.py)
PROVIDERS = ["local", "local_qwen", "cloud"]


def ask(client, model, prompt, attempts=6):
    """Один запит; при 503/429 від хмари чекає й повторює."""
    for i in range(attempts):
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return r.choices[0].message.content
        except (openai.InternalServerError, openai.RateLimitError) as e:
            wait = 5 * 2 ** i
            print(f"  помилка {e.status_code}, повтор через {wait} с...")
            time.sleep(wait)
    return "<ПОМИЛКА: сервер не відповів>"


def json_check(text):
    """Крок 4: 2 – парситься одразу, 1 – після зрізання обгортки, 0 – не парситься."""
    try:
        json.loads(text)
        return 2
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            json.loads(text[start:end + 1])
            return 1
        except json.JSONDecodeError:
            pass
    return 0


if "<встав" in TEXT:
    raise SystemExit("Спочатку встав свій абзац у змінну TEXT!")

results = {}

for provider in PROVIDERS:
    client, model = make_client(provider)
    results[model] = {}

    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):          # два прогони на завдання
            answers.append(ask(client, model, prompt))
        results[model][task_id] = answers
        print(f"{model} / {task_id} – готово")

    scores = [json_check(a) for a in results[model]["2_format"]]
    print(f"{model}: json.loads для завдання 2 -> {scores}")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nЗбережено у quality.json")
