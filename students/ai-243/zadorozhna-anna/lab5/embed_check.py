
"""Перевірка моделі ембедингів: довжина вектора, норма, близькість трьох текстів."""
import time

import numpy as np

import embedder

texts = [
    "Скільки води потрібно для варіння овочів?",
    "Обсяг води для приготування овочів",
    "Правила догляду за кухонними ножами"
]

started = time.time()
vectors = np.array(embedder.embed(texts), dtype="float32")

print(f"Час: {time.time() - started:.1f} с (з кешем буде майже 0)")
print(f"Довжина вектора: {vectors.shape[1]}")
print(
    f"Довжина (норма) першого вектора: "
    f"{np.linalg.norm(vectors[0]):.3f}  "
    "(1.000 - вектори вже нормалізовані)"
)

unit = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

print(
    f"Запит - 'Обсяг води для приготування овочів' : "
    f"{float(unit[0] @ unit[1]):.3f}"
)
print(
    f"Запит - 'Правила догляду за кухонними ножами': "
    f"{float(unit[0] @ unit[2]):.3f}"
)
