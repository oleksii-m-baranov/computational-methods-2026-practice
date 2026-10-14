"""Завдання 6. Керування випадковістю: temperature і top_p (варіант 7)."""
from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

client, model = make_client("local")

CREATIVE = "Назва застосунку обліку особистих витрат"
FACTUAL = "Рік першого кінопоказу братів Люм'єр"


def run(prompt, n=5, **params):
    """Запускає промпт n разів і повертає список відповідей."""
    answers = []
    for _ in range(n):
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **params,
        )
        answers.append(r.choices[0].message.content.strip())
    return answers


logger.info(f"===== SAMPLING | модель {model} =====")

# Крок 2. Творче завдання, вплив temperature
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    logger.info(f"[творче] temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        logger.info(f"    {a}")
    logger.info("")

# Крок 3. Творче завдання, вплив top_p при фіксованій temperature
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    logger.info(f"[творче] temperature=0.7, top_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        logger.info(f"    {a}")
    logger.info("")

# Крок 4. Фактичне питання (правильна відповідь – 1895)
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    correct = sum("1895" in a for a in answers)
    logger.info(f"[фактичне] temperature={t}: містять 1895 – {correct} з 5")
    for a in answers:
        logger.info(f"    {a}")
    logger.info("")

# Крок 5. Перевірка відтворюваності
answers = run(FACTUAL, n=10, temperature=0.0)
logger.info(f"[відтворюваність] 10 запусків, temperature=0.0: унікальних {len(set(answers))}")
logger.info(f"Усі відповіді однакові: {len(set(answers)) == 1}")
for a in answers:
    logger.info(f"    {a}")
