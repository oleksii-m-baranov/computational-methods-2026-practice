
"""Перегляд чанків документів для лабораторної №5."""

import config
from chunking import load_documents, make_chunks


def main():
    documents = load_documents(config.DOC_DIRS)

    chunks = make_chunks(
        documents,
        method=config.CHUNK_METHOD,
        size=config.CHUNK_SIZE,
        overlap=config.CHUNK_OVERLAP,
        with_title=config.WITH_TITLE,
    )

    print(f"Документів: {len(documents)}")
    print(f"Чанків: {len(chunks)}")
    print("-" * 60)

    for chunk in chunks:
        print(f"ID: {chunk['id']}")
        print(f"Джерело: {chunk['source']}")
        print(f"Розмір: {len(chunk['text'])} символів")
        print(f"Текст: {chunk['text'][:120]}...")
        print("-" * 60)


if __name__ == "__main__":
    main()
