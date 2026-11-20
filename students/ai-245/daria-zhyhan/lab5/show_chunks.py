import chunking
import config

docs = chunking.load_documents(config.DOC_DIRS)
configs = [
    ("fixed", 400, 0),
    ("fixed", 400, 80),
    ("fixed", 800, 0),
    ("fixed", 800, 150),
    ("paragraphs", 800, 0),
]

print(f"{'Метод':<12} {'Розмір':<8} {'Перекриття':<12} {'Чанків':<8} {'Середн. довжина':<17} {'Мін':<6} {'Макс':<6}")
print("-" * 75)
for method, size, overlap in configs:
    chunks = chunking.make_chunks(docs, method, size, overlap)
    lengths = [len(c["text"]) for c in chunks]
    avg_len = sum(lengths) / len(lengths)
    print(f"{method:<12} {size:<8} {overlap:<12} {len(chunks):<8} {avg_len:<17.1f} {min(lengths):<6} {max(lengths):<6}")