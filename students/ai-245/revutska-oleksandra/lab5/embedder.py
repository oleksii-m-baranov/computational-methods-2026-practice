
"""Створення ембедингів тексту через Ollama."""

import numpy as np
from openai import OpenAI

import config


def get_client():
    return OpenAI(
        base_url=config.BASE_URL,
        api_key=config.API_KEY,
    )


def embed_texts(texts, model=None):
    """Перетворює список текстів на нормалізовані вектори."""
    if not texts:
        return np.empty((0, 0), dtype=np.float32)

    client = get_client()
    model = model or config.EMBED_MODEL
    vectors = []

    for text in texts:
        response = client.embeddings.create(
            model=model,
            input=text,
        )
        vectors.append(response.data[0].embedding)

    array = np.asarray(vectors, dtype=np.float32)

    norms = np.linalg.norm(array, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)

    return array / norms


def embed_query(query, model=None):
    """Створює вектор одного пошукового запиту."""
    return embed_texts([query], model=model)[0]
