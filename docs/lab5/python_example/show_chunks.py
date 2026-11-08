"""Показує, як документ нарізається на чанки.
Запуск: python show_chunks.py data/docs/d01.txt fixed 200 0
        python show_chunks.py data/docs/d01.txt paragraphs 800"""
import sys

import chunking

path, method, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
overlap = int(sys.argv[4]) if len(sys.argv) > 4 else 0

with open(path, encoding="utf-8") as f:
    text = f.read().strip()
parts = chunking.split_fixed(text, size, overlap) if method == "fixed" else chunking.split_paragraphs(text, size)

cut = 0
for number, part in enumerate(parts, 1):
    ends_ok = part.rstrip().endswith((".", "!", "?", "…", ":"))
    cut += 0 if ends_ok else 1
    print(f"--- чанк {number}, {len(part)} символів" + ("" if ends_ok else "  [закінчується посеред речення]"))
    print(part)
print(f"\nУсього чанків: {len(parts)}; закінчуються посеред речення: {cut}")