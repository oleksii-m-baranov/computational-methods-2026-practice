"""Перевірка моделі ембедингів: довжина вектора, норма, близькість трьох текстів."""
import time

import numpy as np

import embedder

texts = [
    "Скільки корму давати коту щодня?",
    "Денна норма харчування кота",
    "Графік роботи ветеринарної клініки"
]
started = time.time()
vectors = np.array(embedder.embed(texts), dtype="float32")
print(f"Час: {time.time() - started:.1f} с (з кешем буде майже 0)")
print(f"Довжина вектора: {vectors.shape[1]}")
print(f"Довжина (норма) першого вектора: {np.linalg.norm(vectors[0]):.3f}  (1.000 - вектори вже нормалізовані)")

unit = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
print(f"Запит - 'Денна норма харчування кота'       : {float(unit[0] @ unit[1]):.3f}")
print(f"Запит - 'Графік роботи ветеринарної клініки': {float(unit[0] @ unit[2]):.3f}")
