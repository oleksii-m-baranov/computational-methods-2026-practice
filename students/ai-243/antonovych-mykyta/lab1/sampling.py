from providers import make_client
from utils.lab_logger import custom_logger


logger = custom_logger("lab1")

client, model = make_client("local")


CREATIVE = (
    "Запропонуй назву застосунку "
    "нагадувань про ліки."
)

FACTUAL = (
    "Рік відкриття Київського метрополітену. "
    "Відповідай лише роком."
)


def run(prompt, n=5, **params):

    answers = []

    for _ in range(n):

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            **params,
        )

        answer = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        answers.append(answer)

    return answers


logger.info("===== TASK 6 =====")


# TEMPERATURE — ТВОРЧЕ
for t in [0.0, 0.7, 1.5]:

    answers = run(
        CREATIVE,
        temperature=t,
    )

    logger.info(
        f"CREATIVE / temperature={t}: "
        f"unique={len(set(answers))}/5"
    )

    for answer in answers:
        logger.info(answer)


# TOP_P — ТВОРЧЕ
for p in [0.1, 0.5, 1.0]:

    answers = run(
        CREATIVE,
        temperature=0.7,
        top_p=p,
    )

    logger.info(
        f"CREATIVE / top_p={p}: "
        f"unique={len(set(answers))}/5"
    )

    for answer in answers:
        logger.info(answer)


# ФАКТИЧНЕ ПИТАННЯ
for t in [0.0, 1.5]:

    answers = run(
        FACTUAL,
        temperature=t,
    )

    logger.info(
        f"FACTUAL / temperature={t}"
    )

    for answer in answers:
        logger.info(answer)


# ВІДТВОРЮВАНІСТЬ
answers = run(
    FACTUAL,
    n=10,
    temperature=0.0,
)

logger.info(
    "REPRODUCIBILITY / "
    f"unique={len(set(answers))}/10"
)

logger.info(
    "ALL SAME: "
    f"{len(set(answers)) == 1}"
)

for answer in answers:
    logger.info(answer)
