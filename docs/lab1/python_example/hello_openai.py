from openai import OpenAI
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

client = OpenAI(
    base_url="http://localhost:11434/v1",  # адреса локальної Ollama
    api_key="ollama",  # Ollama ключ не перевіряє,
    # але поле обов'язкове
)

SYSTEM = ["Ти лаконічний технічний асистент.", "Відповідай лише українською, максимум двома реченнями."]
USER = "Поясни різницю між списком і кортежем у Python."

for s in SYSTEM:
    logger.info(s)
    response = client.chat.completions.create(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": s},
            {"role": "user", "content": USER},
        ],
        temperature=0.7,
    )
    logger.info(response.choices[0].message.content)
    logger.info(response.usage)
    # logger.info(f"prompt_tokens: {response.usage.prompt_tokens}")
    # logger.info(f"completion_tokens: {response.usage.completion_tokens}")
    # logger.info(f"total_tokens: {response.usage.total_tokens}")
