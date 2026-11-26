"""Додаткове завдання ЛР №5: FAISS vs Chroma cosine vs Chroma default.

Запуск: python chroma_test.py
Потрібно Ollama (модель bge-m3), faiss-cpu, chromadb.
Читає питання D1 з rag_cases.json і використовує ОДНАКОВІ чанки та вектори.
Записує реальний вивід у results/chroma_test.txt і секцію 10 report.md.
Тимчасові БД chroma_cos/ і chroma_default/ ігноруються Git.
"""
from datetime import datetime
import json
import os
from pathlib import Path
import re

import chunking
import config
import embedder
import rag
from chroma_index import ChromaIndex

ROOT = Path(__file__).resolve().parent
SECTION = "## 10. Додаткове завдання"


def same_chunk(a, b):
    return (a["source"], int(a["chunk"]), a["text"]) == (b["source"], int(b["chunk"]), b["text"])


def main():
    os.chdir(ROOT)  # Усі шляхи config.DOC_DIRS та index/ відносні до каталогу lab5.
    cases = json.loads((ROOT / "rag_cases.json").read_text(encoding="utf-8"))
    case = next(c for c in cases if c["id"] == "D1")
    question = case["question"]
    docs = chunking.load_documents(config.DOC_DIRS)
    chunks = chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
                                  config.CHUNK_OVERLAP, config.WITH_TITLE)
    # Вектори обчислюються один раз для ВСІХ трьох індексів.
    vectors = embedder.embed([chunk["text"] for chunk in chunks])
    # Перший індекс — існуючий FAISS з нормалізацією та IndexFlatIP.
    faiss_top = rag.Index(chunks, vectors).search(question, 1)[0]
    cosine_top = ChromaIndex(chunks, vectors, path=str(ROOT / "chroma_cos"),
                             space="cosine").search(question, 1)[0]
    default_top = ChromaIndex(chunks, vectors, path=str(ROOT / "chroma_default"),
                              space=None).search(question, 1)[0]
    s = faiss_top["score"]
    d_cos = cosine_top["distance"]
    d_l2 = default_top["distance"]
    same_cos = same_chunk(faiss_top, cosine_top)
    same_default = same_chunk(faiss_top, default_top)
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    rows = [
        f"Дата: {timestamp}",
        f"Модель ембедингів: {config.EMBED_MODEL}",
        f"Нарізання: {config.CHUNK_METHOD}, {config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP}, title={config.WITH_TITLE}",
        f"Кількість однакових чанків: {len(chunks)}; розмірність вектора: {len(vectors[0])}",
        f"Питання D1: {question}",
        f"FAISS, cosine similarity: {s:.6f}; top-1: {faiss_top['source']} / {faiss_top['chunk']}",
        f"Chroma cosine, distance: {d_cos:.6f}; top-1: {cosine_top['source']} / {cosine_top['chunk']}",
        f"Chroma default L2, squared distance: {d_l2:.6f}; top-1: {default_top['source']} / {default_top['chunk']}",
        f"FAISS top-1 == Chroma cosine top-1: {same_cos}",
        f"FAISS top-1 == Chroma default top-1: {same_default}",
        f"Теоретично 1 - s = {1-s:.6f}",
        f"Теоретично 2 - 2*s = {2-2*s:.6f}",
    ]
    if same_cos and same_default:
        rows.append(f"Похибка cosine від 1-s: {abs(d_cos-(1-s)):.6g}")
        rows.append(f"Похибка L2 від 2-2*s: {abs(d_l2-(2-2*s)):.6g}")
    else:
        rows.append("Увага: топові чанки різні. Формули треба порівнювати на тих самих парах векторів.")
    output = ROOT / "results" / "chroma_test.txt"
    output.parent.mkdir(exist_ok=True)
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("\n".join(rows), flush=True)

    table = [
        SECTION, "",
        "Реалізовано `ChromaIndex` у `chroma_index.py` та проведено локальне порівняння",
        "трьох індексів скриптом `chroma_test.py` на тих самих чанках й ембедингах `bge-m3`.",
        f"Дата експерименту: **{timestamp}**. Питання **D1**: {question}", "",
        "| Індекс | Метрика, напрям | Значення | Найближчий чанк |",
        "|---|---|---:|---|",
        f"| FAISS `IndexFlatIP` | косинусна схожість (більше — краще) | {s:.6f} | `{faiss_top['source']}` / {faiss_top['chunk']} |",
        f"| Chroma `space=cosine` | косинусна відстань (менше — краще) | {d_cos:.6f} | `{cosine_top['source']}` / {cosine_top['chunk']} |",
        f"| Chroma за замовчуванням `l2` | квадрат евклідової відстані (менше — краще) | {d_l2:.6f} | `{default_top['source']}` / {default_top['chunk']} |", "",
        f"**Чи збіглися чанки?** FAISS/Chroma cosine — **{'так' if same_cos else 'ні'}**, "
        f"FAISS/Chroma default — **{'так' if same_default else 'ні'}**.", "",
        "Після L2-нормалізації векторів для тієї самої пари запит–документ:",
        f"косинусна відстань `1 − similarity` (для FAISS top-1: {1-s:.6f}); "
        f"квадрат L2-відстані `2 − 2·similarity` (для FAISS top-1: {2-2*s:.6f}).",
    ]
    if same_cos and same_default:
        table += [f"Виміряні відстані відповідають формулам з похибками "
                  f"**{abs(d_cos-(1-s)):.6g}** і **{abs(d_l2-(2-2*s)):.6g}** відповідно."]
    else:
        table += ["Частина top-1 результатів різниться; числові формули порівнюються лише для однакових векторів. "
                  "Це може бути наслідком наближеного пошуку HNSW або близьких за відстанню чанків."]
    table += ["", "**Пастка порога `MIN_SCORE`.** У FAISS `MIN_SCORE` — нижня межа "
              "*схожості* (`score >= MIN_SCORE`), а Chroma повертає *відстані*. "
              "Якщо механічно застосувати `distance >= MIN_SCORE` до Chroma, будуть "
              "відібрані більш далекі, нерелевантні фрагменти або відкинуті близькі. "
              "Для Chroma cosine еквівалентна умова `distance <= 1 − MIN_SCORE`, "
              "для Chroma L2 — `distance <= 2 − 2·MIN_SCORE` за нормалізованих векторів.", "",
              "Повний вивід ідентифікованого експерименту: `results/chroma_test.txt`.", ""]
    path = ROOT / "report.md"
    report = path.read_text(encoding="utf-8")
    pattern = r"(?ms)^## 10\. Додаткове завдання\s*\n.*?(?=^## 11\.)"
    new, count = re.subn(pattern, "\n".join(table) + "\n", report)
    if count != 1:
        raise RuntimeError("Не знайдено розділ 10 для оновлення report.md; результати збережено в results/chroma_test.txt")
    path.write_text(new, encoding="utf-8")
    print("\nРозділ 10 report.md оновлено за фактичним запуском Chroma.")


if __name__ == "__main__":
    main()
