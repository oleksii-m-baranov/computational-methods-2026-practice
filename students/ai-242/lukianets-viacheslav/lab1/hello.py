"""Завдання 2: вплив system-повідомлення (варіант 1)."""
from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger("lab1")

USER = "Поясни різницю між списком і кортежем у Python."
SYSTEMS = {
    "лаконічний асистент": "Ти лаконічний технічний асистент.",
    "українською, 2 речення": "Відповідай лише українською, максимум двома реченнями.",
}

for provider in ["local_llama", "local_qwen"]:
    client, model = make_client(provider)
    for label, system in SYSTEMS.items():
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": USER},
            ],
            temperature=0.7,
        )
        text = response.choices[0].message.content
        logger.info(f"===== hello / {model} / {label} =====")
        logger.info(text)
        logger.info(f"довжина відповіді, символів: {len(text)}")
        logger.info(response.usage)
