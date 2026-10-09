import time

from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger("lab1")

QUESTION = "Поясни різницю між стеком і чергою. Коротко."

logger.info("===== TASK 3 =====")

for name in ["local", "cloud"]:
    client, model = make_client(name)

    start = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": QUESTION,
            }
        ],
        temperature=0.7,
    )

    elapsed = time.perf_counter() - start
    answer = response.choices[0].message.content

    logger.info(
        f"===== {name.upper()} ({model}) ====="
    )
    logger.info(answer)
    logger.info(f"TIME: {elapsed:.3f} s")
    logger.info(f"CHARS: {len(answer)}")
    logger.info(f"USAGE: {response.usage}")
