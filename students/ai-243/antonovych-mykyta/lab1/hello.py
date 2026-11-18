import re

from openai import OpenAI
from utils.lab_logger import custom_logger

logger = custom_logger("lab1")

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

USER = "Поясни різницю між стеком і чергою."

SYSTEMS = {
    "short": "Ти лаконічний технічний асистент.",
    "ukrainian_two_sentences":
        "Відповідай лише українською, максимум двома реченнями.",
}

MODELS = [
    "llama3.2:3b",
    "qwen3:4b",
]


def approximate_sentence_count(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return len([p for p in parts if p])


logger.info("===== TASK 2 =====")

for model in MODELS:
    for system_name, system_prompt in SYSTEMS.items():

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": USER,
                },
            ],
            temperature=0.7,
        )

        text = response.choices[0].message.content

        logger.info(f"MODEL: {model}")
        logger.info(f"SYSTEM: {system_name}")
        logger.info(f"SYSTEM TEXT: {system_prompt}")
        logger.info(f"ANSWER: {text}")
        logger.info(f"CHARS: {len(text)}")
        logger.info(
            f"SENTENCES_APPROX: "
            f"{approximate_sentence_count(text)}"
        )
        logger.info(f"USAGE: {response.usage}")
