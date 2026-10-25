import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def make_client(name: str):
    if name == "llama":
        return OpenAI(base_url="http://localhost:11434/v1", api_key="ollama"), "llama3.2:3b"
    elif name == "qwen":
        return OpenAI(base_url="http://localhost:11434/v1", api_key="ollama"), "qwen3:4b"
    elif name == "cloud":
        return OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=os.getenv("CLOUD_API_KEY"),
        ), "gemini-3.5-flash-lite"
    else:
        raise ValueError(f"Unknown provider name: {name}")