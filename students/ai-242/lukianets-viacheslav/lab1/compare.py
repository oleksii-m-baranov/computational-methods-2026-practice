"""Завдання 3: локальна vs хмарна модель (варіант 1)."""
import time
from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger("lab1")

QUESTION = "Поясни різницю між списком і кортежем у Python. Коротко."

for name in ["local", "cloud"]:
    client, model = make_client(name)

    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": QUESTION}],
        temperature=0.7,
    )
    elapsed = time.perf_counter() - t0

    text = response.choices[0].message.content
    logger.info(f"===== {name.upper()} ({model}) =====")
    logger.info(text)
    logger.info(f"Час: {elapsed:.2f} с; символів: {len(text)}")
    logger.info(response.usage)
