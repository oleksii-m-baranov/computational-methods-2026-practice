import time
from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

QUESTION = "Поясни різницю між масивом і зв’язним списком. Коротко."

for name in ["local", "cloud"]:
    client, model = make_client(name)
    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": QUESTION}],
        temperature=0.7,
    )
    elapsed = time.perf_counter() - t0

    header = f"===== {name.upper()} ({model}) ====="
    content = response.choices[0].message.content
    timing = f"Час: {elapsed:.2f} с"
    usage_info = str(response.usage)

    print(header)
    print(content)
    print(timing)
    print(usage_info)
    print()
    logger.info(header)
    logger.info(content)
    logger.info(timing)
    logger.info(usage_info)
    logger.info('')