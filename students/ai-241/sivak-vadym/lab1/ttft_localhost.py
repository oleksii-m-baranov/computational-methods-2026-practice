"""Завдання 4, додатково: з чого складається TTFT локальної моделі.
На Windows 'localhost' спершу резолвиться в IPv6 ::1, а Ollama слухає лише IPv4 127.0.0.1,
тому кожне нове з'єднання чекає ~2 с на відкат до IPv4. Порівнюємо дві адреси."""
import socket
import statistics

from openai import OpenAI

from benchmark import measure, PROMPTS
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

MODEL = "llama3.2:3b"
logger.info("===== TTFT: localhost vs 127.0.0.1 =====")
logger.info(f"getaddrinfo('localhost'): {[a[4][0] for a in socket.getaddrinfo('localhost', 11434, type=socket.SOCK_STREAM)]}")

for host in ["localhost", "127.0.0.1"]:
    client = OpenAI(base_url=f"http://{host}:11434/v1", api_key="ollama")
    measure(client, MODEL, "розігрів")  # прогрів, не рахуємо
    runs = [measure(client, MODEL, PROMPTS["short"]) for _ in range(3)]
    logger.info(f"{host:10} | 3 повтори: {runs}")
    logger.info(f"{host:10} | медіана TTFT={statistics.median(r['ttft_s'] for r in runs)} с, "
                f"всього={statistics.median(r['total_s'] for r in runs)} с")
