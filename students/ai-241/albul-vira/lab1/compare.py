import time
from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

QUESTION = "Поясни різницю між стеком і чергою в Python. Коротко."
for name in ["local", "cloud"]:
# for name in ["cloud"]:
    client, model = make_client(name)
    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": QUESTION}],
        temperature=0.7,
    )
    elapsed = time.perf_counter() - t0
    logger.info(f"===== {name.upper()} ({model}) =====")
    logger.info(response.choices[0].message.content)
    logger.info(f"Час: {elapsed:.2f} с")
    logger.info(response.usage)
    logger.info('')
