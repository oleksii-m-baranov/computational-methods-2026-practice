"""Допоміжний скрипт: змінює розмір вікна в config.py (MODEL, NUM_CTX, COMPRESS_AT).

Запуск:  python set_window.py 3072
Допустимі значення: 4096, 3072, 2048, 1920.
"""
import re
import sys

WINDOWS = {
    4096: ("qwen25-4k", 2800),
    3072: ("qwen25-3k", 2150),
    2048: ("qwen25-2k", 1400),
    1920: ("qwen25-1920", 1450),
    1600: ("qwen25-1600", 1200),
}

size = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
if size not in WINDOWS:
    raise SystemExit(f"Допустимі значення: {sorted(WINDOWS)}")
model, compress_at = WINDOWS[size]

with open("config.py", encoding="utf-8") as f:
    text = f.read()

text = re.sub(r'^MODEL = .*$', f'MODEL = "{model}"      # нова модель з малим вікном', text, flags=re.M)
text = re.sub(r'^NUM_CTX = .*$', f'NUM_CTX = {size}          # розмір вікна, який ви задасте в кроці 1', text, flags=re.M)
text = re.sub(r'^COMPRESS_AT = .*$', f'COMPRESS_AT = {compress_at}      # скорочуємо, коли prompt_tokens перевищив це число', text, flags=re.M)

with open("config.py", "w", encoding="utf-8") as f:
    f.write(text)
print(f"Готово: MODEL={model}, NUM_CTX={size}, COMPRESS_AT={compress_at}")
