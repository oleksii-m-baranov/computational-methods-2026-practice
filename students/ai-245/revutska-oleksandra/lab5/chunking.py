
"""Розбиття текстових документів на чанки для RAG."""

from pathlib import Path
import re


def load_documents(doc_dirs):
    """Завантажує всі TXT-документи із заданих папок."""
    documents = []

    for directory in doc_dirs:
        folder = Path(directory)

        if not folder.exists():
            continue

        for path in sorted(folder.rglob("*.txt")):
            text = path.read_text(encoding="utf-8-sig")

            if text.strip():
                documents.append({
                    "source": str(path),
                    "title": path.stem,
                    "text": text.strip(),
                })

    return documents


def split_fixed(text, size=800, overlap=0):
    """Розбиває текст на фрагменти фіксованого розміру."""
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Некоректний розмір чанка або overlap")

    chunks = []
    step = size - overlap

    for start in range(0, len(text), step):
        chunk = text[start:start + size].strip()
        if chunk:
            chunks.append(chunk)

        if start + size >= len(text):
            break

    return chunks


def split_paragraphs(text, size=800):
    """Об'єднує абзаци, не перевищуючи заданий розмір."""
    if size <= 0:
        raise ValueError("Розмір чанка має бути додатним")

    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    chunks = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > size:
            if current:
                chunks.append(current)
                current = ""

            chunks.extend(split_fixed(paragraph, size, 0))
            continue

        candidate = (
            current + "\n\n" + paragraph
            if current else paragraph
        )

        if len(candidate) <= size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = paragraph

    if current:
        chunks.append(current)

    return chunks


def make_chunks(
    documents,
    method="paragraphs",
    size=800,
    overlap=0,
    with_title=False,
):
    """Створює чанки з метаданими джерела."""
    result = []

    for document in documents:
        if method == "fixed":
            parts = split_fixed(document["text"], size, overlap)
        elif method == "paragraphs":
            parts = split_paragraphs(document["text"], size)
        else:
            raise ValueError(f"Невідомий метод: {method}")

        for number, part in enumerate(parts):
            text = part

            if with_title:
                text = document["title"] + "\n" + part

            result.append({
                "id": f"{document['title']}_{number:03d}",
                "source": document["source"],
                "title": document["title"],
                "text": text,
            })

    return result
