"""Нарізання документів на чанки."""
import glob
import os
import re


def split_fixed(text, size, overlap=0):
    """Ріже текст на шматки по size символів; наступний шматок починається на overlap символів раніше."""
    if overlap >= size:
        raise ValueError("overlap має бути меншим за size")
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step) if text[i:i + size].strip()]


def split_paragraphs(text, size):
    """Ріже за порожніми рядками (абзацами); сусідні абзаци склеює, поки вони вміщуються в size."""
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, current = [], ""
    for p in parts:
        if current and len(current) + 2 + len(p) > size:
            chunks.append(current)
            current = p
        else:
            current = (current + "\n\n" + p) if current else p
    if current:
        chunks.append(current)
    return chunks


def load_documents(dirs):
    """Читає всі .txt з каталогів. Перший рядок файла - назва документа."""
    docs = []
    for directory in dirs:
        for path in sorted(glob.glob(os.path.join(directory, "*.txt"))):
            with open(path, encoding="utf-8") as f:
                text = f.read().strip()
            docs.append({"source": os.path.basename(path), "title": text.split("\n", 1)[0].strip(), "text": text})
    return docs


def make_chunks(docs, method, size, overlap=0, with_title=False):
    """Повертає список чанків: {"source": файл, "chunk": номер, "text": текст}."""
    chunks = []
    for doc in docs:
        if method == "fixed":
            parts = split_fixed(doc["text"], size, overlap)
        elif method == "paragraphs":
            parts = split_paragraphs(doc["text"], size)
        else:
            raise ValueError(f"Невідомий спосіб нарізання: {method}")
        for number, part in enumerate(parts):
            if with_title and not part.startswith(doc["title"]):
                part = doc["title"] + "\n" + part
            chunks.append({"source": doc["source"], "chunk": number, "text": part})
    return chunks
