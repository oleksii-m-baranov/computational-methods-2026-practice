
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

local = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

cloud = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("CLOUD_API_KEY")
)

LOCAL_MODEL = "llama3.2:3b"
QWEN_MODEL = "qwen3:4b"
CLOUD_MODEL = "openai/gpt-oss-120b"
