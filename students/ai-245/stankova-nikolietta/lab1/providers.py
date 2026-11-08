import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROVIDERS = {
    "llama": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "llama3.2:3b",
    },

    "qwen": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "qwen3:4b",
    },

    "cloud": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key": os.getenv("GEMINI_API_KEY"),
        "model": "gemini-3.8-flash",
    },
}

def make_client(name):
    cfg = PROVIDERS[name]

    client = OpenAI(
        base_url=cfg["base_url"],
        api_key=cfg["api_key"]
    )

    return client, cfg["model"]