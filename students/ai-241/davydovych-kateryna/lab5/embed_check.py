"""Перевірка моделі ембедингів: довжина вектора, норма, близькість трьох текстів."""
import time

import numpy as np

import embedder

texts = [
    "Скільки годин ноутбук пропрацює без розетки?",      # запит
    "Час автономної роботи від акумулятора",             # близька за змістом фраза
    "Кількість портів USB на корпусі"]                   # далека за змістом фраза
started = time.time()
vectors = np.array(embedder.embed(texts), dtype="float32")
print(f"Час: {time.time() - started:.1f} с (з кешем буде майже 0)")
print(f"Довжина вектора: {vectors.shape[1]}")
print(f"Довжина (норма) першого вектора: {np.linalg.norm(vectors[0]):.3f}  (1.000 - вектори вже нормалізовані)")

unit = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
print(f"Запит - 'Час автономної роботи'  : {float(unit[0] @ unit[1]):.3f}")
print(f"Запит - 'Кількість портів USB'   : {float(unit[0] @ unit[2]):.3f}")