"""Перевірка векторів ембединг-моделі."""
import time
import numpy as np
import embedder

texts = ["Скільки часу займає навчальна перевірка кота?",
         "Тривалість навчальної перевірки у хвилинах",
         "Правила перевезення макета переноски"]
started = time.time()
vectors = np.array(embedder.embed(texts), dtype="float32")
unit = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
print(f"Час: {time.time() - started:.1f} с")
print(f"Розмірність: {vectors.shape[1]}")
print(f"Норма: {np.linalg.norm(vectors[0]):.3f}")
print(f"Схожа тема: {float(unit[0] @ unit[1]):.3f}")
print(f"Інша тема: {float(unit[0] @ unit[2]):.3f}")
