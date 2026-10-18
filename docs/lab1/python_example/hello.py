import time
from openai import OpenAI

from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

# Кажемо клієнту стукати не в OpenAI, а на наш комп'ютер

client = OpenAI(
    base_url="http://localhost:11434/v1",  # адреса локальної Ollama
    api_key="ollama",  # Ollama ключ не перевіряє,
    # але поле обов'язкове
)

# for model in ('gemma4:26b-a4b-it-qat', 'llama3.2:3b', 'qwen3:4b', 'qwen3:8b'):
for model in ('llama3.2:3b', 'qwen3:4b'):
    logger.info(model)
    start = time.perf_counter()
    response = client.chat.completions.create(
        # model="qwen3:4b",
        model=model,
        messages=[
            {"role": "system", "content": "Ти лаконічний технічний асистент."},
            {"role": "user", "content": "Поясни різницю між списком і кортежем у Python."},
        ],
        temperature=0.7,
    )

    logger.info(f"Duration: {round(time.perf_counter() - start, 3)}")
    logger.info(response.choices[0].message.content)
    # logger.info(response.usage)  # скільки токенів витрачено
    # logger.info(response.to_json(indent=4))
