import os, urllib.request, json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
KEY = (os.getenv("CLOUD_API_KEY") or "").strip()

if KEY.startswith("AIza"):
    CLOUD_CFG = {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "api_key": KEY, "model": "gemini-2.5-flash"}
else:
    req = urllib.request.Request("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {KEY}", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        models = {m["id"] for m in json.loads(resp.read().decode())["data"]}
    preferred = ["openai/gpt-oss-120b", "qwen/qwen3-32b", "llama-3.1-8b-instant", "gemma2-9b-it"]
    chosen = next((m for m in preferred if m in models), sorted(models)[0])
    CLOUD_CFG = {"base_url": "https://api.groq.com/openai/v1", "api_key": KEY, "model": chosen}

PROVIDERS = {
    "local": {"base_url": "http://localhost:11434/v1", "api_key": "ollama", "model": "llama3.2:3b"},
    "local_reason": {"base_url": "http://localhost:11434/v1", "api_key": "ollama", "model": "qwen3:4b"},
    "cloud": CLOUD_CFG,
}

def make_client(name):
    cfg = PROVIDERS[name]
    return OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"]), cfg["model"]
