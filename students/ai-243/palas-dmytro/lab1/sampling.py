from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger("task6_sampling", overwrite=True)

client, model = make_client("local")

CREATIVE = "Назва освітнього проєкту з астрономії"
FACTUAL = "Рік підписання Паризької кліматичної угоди"


def run(prompt: str, n: int = 5, **params):
    """Запускає промпт n разів і повертає список відповідей."""
    answers = []
    for _ in range(n):
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **params,
        )
        answers.append((r.choices[0].message.content or "").strip())
    return answers


logger.info(f"Model: {model}")
logger.info("--- Творче завдання: temperature ---")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    logger.info(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for idx, a in enumerate(answers, 1):
        logger.info(f"  [{idx}] {a}")

logger.info("--- Творче завдання: top_p (temperature=0.7) ---")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    logger.info(f"top_p={p}: унікальних {len(set(answers))} з 5")
    for idx, a in enumerate(answers, 1):
        logger.info(f"  [{idx}] {a}")

logger.info("--- Фактичне питання: temperature ---")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    logger.info(f"temperature={t}: {answers}")

logger.info("--- Перевірка відтворюваності (n=10, temperature=0.0) ---")
answers = run(FACTUAL, n=10, temperature=0.0)
logger.info(f"Унікальних відповідей: {len(set(answers))}")
logger.info(f"Усі відповіді однакові: {len(set(answers)) == 1}")
for idx, a in enumerate(answers, 1):
    logger.info(f"  [{idx}] {a}")
