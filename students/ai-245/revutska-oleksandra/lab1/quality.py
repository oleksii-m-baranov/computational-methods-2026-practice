from providers import make_client
from openai import OpenAI
import json
import os

TEXT = """
Одеський державний університет відновив свою роботу в Одесі 21 квітня 1944 року.
У 1945 році йому було присвоєно ім’я І. І. Мечникова.
У 1965 році університет був нагороджений орденом Трудового Червоного Прапора.
У 1978 році його включили до переліку провідних університетів СРСР.
До кінця 1980-х років університет складався з 9 факультетів.
У 2020 році Одеський національний університет імені І. І. Мечникова відзначив 155-річчя від заснування.
"""

TASKS = {
    "1_fact":
        "У якому році засновано Одеський національний університет "
        "імені І. І. Мечникова? Відповідай лише роком.",

    "2_format":
        "Подай дані про Одеський національний університет імені "
        "І. І. Мечникова у JSON з полями name, year, city. "
        "Без пояснень, без markdown, лише JSON.",

    "3_summary":
        "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,

    "4_code":
        "Напиши функцію is_palindrome(s), яка перевіряє, чи є рядок "
        "паліндромом, ігноруючи пробіли й регістр. Лише код.",

    "5_logic":
        "У групі 25 студентів, 12 знають Python, 9 знають Java, "
        "4 знають обидві мови. Скільки студентів не знають жодної "
        "з цих мов? Покажи хід розв'язання.",

    "6_language":
        "Чим стек відрізняється від черги? "
        "Поясни українською, два абзаци.",
}

FILE_NAME = "quality.json"

# Якщо файл уже існує — читаємо збережені результати
if os.path.exists(FILE_NAME):
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            results = json.load(f)
    except:
        results = {}
else:
    results = {}


def save_results():
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2
        )


def run_model(client, model):
    if model not in results:
        results[model] = {}

    for task_id, prompt in TASKS.items():

        # Якщо завдання вже має два результати — пропускаємо
        if task_id in results[model] and len(results[model][task_id]) >= 2:
            print(f"{model} / {task_id} — вже готово")
            continue

        answers = results[model].get(task_id, [])

        while len(answers) < 2:

            attempt = len(answers) + 1

            print()
            print(
                f"{model} / {task_id} / "
                f"спроба {attempt} — виконується..."
            )

            try:
                r = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500,
                )

                answer = r.choices[0].message.content
                answers.append(answer)

                results[model][task_id] = answers

                # Зберігаємо одразу після кожної відповіді
                save_results()

                print(
                    f"{model} / {task_id} / "
                    f"спроба {attempt} — готово"
                )

            except Exception as e:
                print("ПОМИЛКА:", e)
                save_results()
                return


# 1. llama3.2:3b
local_client, local_model = make_client("local")
run_model(local_client, local_model)


# 2. qwen3:4b
qwen_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

run_model(qwen_client, "qwen3:4b")


# 3. Хмарна модель
cloud_client, cloud_model = make_client("cloud")
run_model(cloud_client, cloud_model)


save_results()

print()
print("================================")
print("ГОТОВО!")
print("Результати збережено у quality.json")
print("================================")