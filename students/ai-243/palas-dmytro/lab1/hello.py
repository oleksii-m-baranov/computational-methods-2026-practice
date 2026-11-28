from openai import OpenAI
from utils.lab_logger import custom_logger

logger = custom_logger("task2_hello", overwrite=True)

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    timeout=900.0,
)

SYSTEMS = [
    ("concise", "Ти лаконічний технічний асистент."),
    ("uk_two_sentences", "Відповідай лише українською, максимум двома реченнями."),
]
USER = "Поясни різницю між HTTP і HTTPS."

for model in ["llama3.2:3b", "qwen3:4b"]:
    for label, system_prompt in SYSTEMS:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER},
            ],
            temperature=0.7,
        )
        text = response.choices[0].message.content or ""
        logger.info(f"===== {model} | {label} =====")
        logger.info(f"SYSTEM: {system_prompt}")
        logger.info(f"CHARS: {len(text)}")
        logger.info(f"RESPONSE:\n{text}")
        logger.info(f"USAGE: {response.usage}")
        logger.info("")
