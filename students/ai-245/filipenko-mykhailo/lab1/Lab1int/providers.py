import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

PROVIDERS = {
    "llama": {
        "model": "llama3.2:3b",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    },
    "qwen": {
        "model": "qwen3:4b",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    },
    "cloud": {
        "model": "gemini-3.5-flash-lite",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
}


def make_client(provider):
    if provider not in PROVIDERS:
        raise ValueError(f"Невідомий провайдер: {provider}")

    config = PROVIDERS[provider]

    if not config["api_key"]:
        raise ValueError(
            f"Не налаштовано API-ключ для {provider}"
        )

    client = OpenAI(
        base_url=config["base_url"],
        api_key=config["api_key"],
    )

    return client, config["model"]


def ask_model(prompt, provider="llama", system="Відповідай українською."):
    client, model = make_client(provider)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content or ""


if __name__ == "__main__":
    question = "Поясни різницю між функцією і методом у Python."

    for provider in ["llama", "qwen"]:
        print(f"\nМодель: {PROVIDERS[provider]['model']}")
        print(ask_model(question, provider))
