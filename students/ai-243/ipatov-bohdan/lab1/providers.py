import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

PROVIDERS = {
    "local": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "llama3.2:3b",
    },
    "local2": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "qwen3:4b",
    },
    "cloud": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": os.getenv("CLOUD_API_KEY"),
        "model": "qwen/qwen3.8-27b",
    },
}


def make_client(name: str):
    """Return an OpenAI client and model name for the specified provider."""
    cfg = PROVIDERS[name]
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
    return client, cfg["model"]
