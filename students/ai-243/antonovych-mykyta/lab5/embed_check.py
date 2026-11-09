"""Перевірка моделі ембедингів: довжина вектора, норма, близькість трьох текстів."""
import time

import numpy as np

import embedder

texts = [
    "Як довго зберігати мариновану грушу?",
    "Термін зберігання закритого лотка маринованої груші",
    "Догляд за платформою кухонних ваг",
]
started = time.time()
vectors = np.array(embedder.embed(texts), dtype="float32")
print(f"Час: {time.time() - started:.1f} с (з кешем буде майже 0)")
print(f"Довжина вектора: {vectors.shape[1]}")
print(f"Довжина (норма) першого вектора: {np.linalg.norm(vectors[0]):.3f}  (1.000 - вектори вже нормалізовані)")

unit = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
for label, vector in zip(texts[1:], unit[1:]):
    print(f"Запит — {label}: {float(unit[0] @ vector):.3f}")
