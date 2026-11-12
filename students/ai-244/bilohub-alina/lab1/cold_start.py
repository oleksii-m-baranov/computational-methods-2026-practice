"""Холодний і теплий старт локальної моделі (короткий промпт, варіант 1)."""
import subprocess
import time

from benchmark import measure, PROMPTS
from providers import make_client

client, model = make_client("local")

# Вивантажуємо модель з пам'яті, щоб наступний запит був «холодним»
subprocess.run(["ollama", "stop", model])
time.sleep(3)

cold = measure(client, model, PROMPTS["short"])
warm = measure(client, model, PROMPTS["short"])

print(f"\nМодель: {model}")
print(f"ХОЛОДНИЙ старт: TTFT = {cold['ttft_s']} с, всього = {cold['total_s']} с")
print(f"ТЕПЛИЙ старт : TTFT = {warm['ttft_s']} с, всього = {warm['total_s']} с")
