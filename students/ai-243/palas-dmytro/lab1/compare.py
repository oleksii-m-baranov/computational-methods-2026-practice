import time
from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger("task3_compare", overwrite=True)

QUESTION = "Поясни різницю між HTTP і HTTPS. Коротко."

for name in ["local", "cloud"]:
    client, model = make_client(name)

    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": QUESTION}],
        temperature=0.7,
    )
    elapsed = time.perf_counter() - t0
    text = response.choices[0].message.content or ""

    logger.info(f"===== {name.upper()} ({model}) =====")
    logger.info(text)
    logger.info(f"Час: {elapsed:.2f} с")
    logger.info(f"Довжина, символів: {len(text)}")
    logger.info(f"USAGE: {response.usage}")
    logger.info("")
