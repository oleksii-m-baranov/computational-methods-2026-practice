"""Холодний і теплий старт локальної моделі (короткий промпт)."""
import json
import subprocess
import time
from providers import make_client
from benchmark import measure, PROMPTS

client, model = make_client("local")

subprocess.run(["ollama", "stop", model], check=False)
time.sleep(3)  # даємо моделі вивантажитись

cold = measure(client, model, PROMPTS["short"])   # холодний: без прогріву
warm = measure(client, model, PROMPTS["short"])   # теплий: модель уже в пам'яті
print("cold:", cold)
print("warm:", warm)

with open("coldwarm.json", "w", encoding="utf-8") as f:
    json.dump({"model": model, "cold": cold, "warm": warm}, f, ensure_ascii=False, indent=2)
