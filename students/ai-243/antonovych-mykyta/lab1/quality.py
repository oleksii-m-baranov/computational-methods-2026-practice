import json
import time
from pathlib import Path

from openai import RateLimitError, InternalServerError

from providers import make_client
from utils.lab_logger import custom_logger


logger = custom_logger("lab1")
LAB_DIR = Path(__file__).resolve().parent


# Джерело даних для тексту:
# офіційний Портал Києва, матеріали про Київський метрополітен.
TEXT = """
Першу ділянку Київського метрополітену ввели в експлуатацію у 1960 році.
Вона мала 5 станцій, а її експлуатаційна довжина становила 5,2 км.
З 24 травня 2003 року ця лінія працює від станції «Академмістечко» до станції «Лісова» та має довжину 22,76 км і 18 станцій.
На відкритій ділянці лінії є 2 мостові переходи та 2 шляхопроводи.
У годину пік лінія може пропускати до 40 пар поїздів на годину, а експлуатаційна швидкість становить 36,34 км/год.
""".strip()


TASKS = {
    "1_fact":
        "Рік відкриття Київського метрополітену. "
        "Відповідай лише роком.",

    "2_format":
        "Київський метрополітен. "
        "JSON: city, year, lines_count. "
        "Без пояснень, без markdown, лише JSON.",

    "3_summary":
        "Стисни наступний текст до двох речень, "
        "збережи всі числа:\n\n"
        + TEXT,

    "4_code":
        "Напиши функцію total_weight(items), "
        "яка повертає суму ваг зі списку словників. "
        "Лише код.",

    "5_logic":
        "120 ящиків: 45 по 8 кг, решта по 12 кг. "
        "Вантажівка тримає 1200 кг. "
        "Скільки рейсів? "
        "Покажи хід розв'язання.",

    "6_language":
        "Чим контейнерне перевезення "
        "відрізняється від навалочного. "
        "Поясни українською, два абзаци.",
}


PROVIDERS = [
    "local_llama",
    "local_qwen",
    "cloud",
]


def request_with_retry(client, model, prompt):
    while True:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.7,
            )

            return response

        except RateLimitError:
            logger.info(
                "429 Rate limit. Чекаємо 65 секунд..."
            )
            time.sleep(65)

        except InternalServerError:
            logger.info(
                "503 Cloud model перевантажена. "
                "Чекаємо 30 секунд..."
            )
            time.sleep(30)


results = {}

logger.info("===== TASK 5 =====")


for provider in PROVIDERS:
    client, model = make_client(provider)

    logger.info(
        f"===== PROVIDER: {provider} / {model} ====="
    )

    results[model] = {}

    for task_id, prompt in TASKS.items():
        answers = []

        for attempt in range(1, 3):

            # Gemini free tier має обмеження
            # на кількість запитів за хвилину.
            if provider == "cloud":
                time.sleep(15)

            response = request_with_retry(
                client,
                model,
                prompt,
            )

            answer = (
                response
                .choices[0]
                .message
                .content
            )

            answers.append(answer)

            logger.info(
                f"MODEL: {model}, "
                f"TASK: {task_id}, "
                f"ATTEMPT: {attempt}"
            )

            logger.info(
                f"PROMPT:\n{prompt}"
            )

            logger.info(
                f"ANSWER:\n{answer}"
            )

            if task_id == "2_format":
                try:
                    parsed = json.loads(answer)

                    logger.info(
                        "JSON_LOADS: SUCCESS"
                    )

                    logger.info(
                        f"JSON_VALUE: {parsed}"
                    )

                except Exception as error:
                    logger.info(
                        "JSON_LOADS: FAILED "
                        f"({error})"
                    )

        results[model][task_id] = answers


output = LAB_DIR / "quality.json"

with open(
    output,
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        results,
        file,
        ensure_ascii=False,
        indent=2,
    )


logger.info(
    f"Saved quality results to {output}"
)

logger.info(
    "===== TASK 5 FINISHED ====="
)
