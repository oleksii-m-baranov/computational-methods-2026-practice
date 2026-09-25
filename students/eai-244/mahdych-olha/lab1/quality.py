from providers import make_client
import json
from utils.lab_logger import custom_logger

logger = custom_logger("lab1")

TASKS = {
    "1_fact": "У якому році було відкрито Київський метрополітен? Відповідай коротко.",
    "2_format": (
        "Надай інформацію про Київський метрополітен у форматі JSON "
        "з полями city, year, lines_count. Виведи тільки JSON без markdown і без додаткового тексту."
    ),
    "3_summary": (
        "Стисни до двох речень, збережи всі числа.\n\n"
        "Міський транспорт є важливою частиною інфраструктури великих міст. "
        "Умовний автобусний маршрут має довжину 18 км і 24 зупинки. "
        "У години пік на маршруті працюють 12 автобусів. "
        "Середній інтервал руху становить 7 хвилин. "
        "Один автобус може перевозити до 80 пасажирів. "
        "За день маршрут може обслуговувати близько 9000 пасажирів."
    ),
    "4_code": (
        "Напиши функцію Python total_weight(items), яка повертає суму ваг "
        "зі списку словників. У кожному словнику вага міститься в полі 'weight'. Лише код."
    ),
    "5_logic": (
        "120 ящиків: 45 по 8 кг, решта по 12 кг. "
        "Вантажівка тримає 1200 кг. Скільки рейсів? Покажи хід розрахунку."
    ),
    "6_ukrainian": (
        "Чим контейнерне перевезення відрізняється від навалочного? "
        "Поясни українською, два абзаци."
    ),
}

def run_model(client, model):
    result = {}
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):
            print(f"{model} / {task_id} / прогін {attempt + 1}", flush=True)
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=512,
                timeout=120.0,
            )
            answers.append(r.choices[0].message.content.strip())
        result[task_id] = answers
        logger.info(f"{model} / {task_id} — готово")
    return result

results = {}

local_client, _ = make_client("local")
for model in ["llama3.2:3b", "qwen3:4b"]:
    results[model] = run_model(local_client, model)

cloud_client, cloud_model = make_client("cloud")
results[cloud_model] = run_model(cloud_client, cloud_model)

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Готово: quality.json")
