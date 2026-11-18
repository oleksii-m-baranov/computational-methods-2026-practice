"""Завдання 2. Роль system-повідомлення (варіант 7)."""
from openai import OpenAI

from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

# Кажемо клієнту стукати не в OpenAI, а на наш комп'ютер
client = OpenAI(
    base_url="http://localhost:11434/v1",  # адреса локальної Ollama
    api_key="ollama",                      # Ollama ключ не перевіряє,
                                           # але поле обов'язкове
)

SYSTEMS = [
    "Ти лаконічний технічний асистент.",
    "Відповідай лише українською, максимум двома реченнями.",
]
USER = "Поясни різницю між процесом і потоком."

for model in ["llama3.2:3b", "qwen3:4b"]:
    for system in SYSTEMS:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": USER},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        logger.info(f"===== {model} | SYSTEM: {system}")
        logger.info(content)
        logger.info(f"Довжина відповіді: {len(content)} симв.")
        logger.info(response.usage)
