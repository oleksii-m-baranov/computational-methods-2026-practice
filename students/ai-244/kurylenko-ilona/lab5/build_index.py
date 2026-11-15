"""Будує індекс за параметрами з config.py і зберігає в каталог index/."""
import config
import rag


index = rag.build_from_config()
index.save()
lengths = [len(c["text"]) for c in index.chunks]
print(f"Чанків: {len(index.chunks)}; середня довжина {sum(lengths) / len(lengths):.0f} символів; "
      f"найкоротший {min(lengths)}, найдовший {max(lengths)}")
print(f"Модель: {config.EMBED_MODEL}; довжина вектора: {index.faiss.d}")
