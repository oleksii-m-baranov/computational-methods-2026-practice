"""Завдання 4, крок 3. Холодний і теплий старт локальної моделі."""
import subprocess

from benchmark import measure, PROMPTS
from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

client, model = make_client("local")

# ollama stop llama3.2:3b – вивантажуємо модель з пам'яті
subprocess.run(["ollama", "stop", model], check=True)
logger.info(f"===== COLD/WARM | ollama stop {model} =====")

cold = measure(client, model, PROMPTS["short"])  # модель вантажиться з диска
logger.info(f"Холодний старт: {cold}")

warm = measure(client, model, PROMPTS["short"])  # модель уже в пам'яті
logger.info(f"Теплий старт:   {warm}")
