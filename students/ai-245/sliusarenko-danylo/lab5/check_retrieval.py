"""Перевірка пошуку без агента."""
import json
import re
import sys

import chunking
import config
import rag

CONFIGS = [
    {"name": "fixed-200-0",          "method": "fixed",      "size": 200,  "overlap": 0,   "title": False},
    {"name": "fixed-500-0",          "method": "fixed",      "size": 500,  "overlap": 0,   "title": False},
    {"name": "fixed-500-100",        "method": "fixed",      "size": 500,  "overlap": 100, "title": False},
    {"name": "fixed-1500-0",         "method": "fixed",      "size": 1500, "overlap": 0,   "title": False},
    {"name": "paragraphs-800",       "method": "paragraphs", "size": 800,  "overlap": 0,   "title": False},
    {"name": "paragraphs-800+title", "method": "paragraphs", "size": 800,  "overlap": 0,   "title": True},
]
KS = [1, 3, 5]


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


with open("rag_cases.json", encoding="utf-8") as f:
    cases = json.load(f)
answerable = [c for c in cases if c["kind"] != "none"]
docs = chunking.load_documents(config.DOC_DIRS)

if len(sys.argv) > 1 and sys.argv[1] == "scores":
    index = rag.Index.build(
        chunking.make_chunks(
            docs, config.CHUNK_METHOD, config.CHUNK_SIZE, config.CHUNK_OVERLAP, config.WITH_TITLE
        )
    )
    print(
        f"Параметри: {config.CHUNK_METHOD}, розмір {config.CHUNK_SIZE}, перекриття {config.CHUNK_OVERLAP}, "
        f"заголовок {config.WITH_TITLE}\n"
    )
    print("id   вид         схожість першого результату   чи містить потрібну фразу")
    good, bad = [], []
    for case in cases:
        top = index.search(case["question"], 1)[0]
        has = case["must_contain"] is not None and norm(case["must_contain"]) in norm(top["text"])
        (bad if case["kind"] == "none" else good).append(top["score"])
        mark = "-" if case["kind"] == "none" else ("так" if has else "НІ")
        print(f"{case['id']:4} {case['kind']:11} {top['score']:.3f}                         {mark}")
    print(f"\nНайнижча схожість серед питань з відповіддю: {min(good):.3f}")
    print(f"Найвища схожість серед питань без відповіді: {max(bad):.3f}")
    if max(bad) < min(good):
        print(f"Межі не перекриваються: поріг MIN_SCORE можна вибрати між {max(bad):.3f} і {min(good):.3f}")
    else:
        print("Межі перекриваються: жоден поріг не розділяє питання ідеально, виберіть компроміс і опишіть його")
    sys.exit(0)

print(
    f"{'конфігурація':22} {'чанків':>6} {'сер.довжина':>11} "
    + " ".join(f"{'hit@' + str(k):>6}" for k in KS)
    + f" {'hit@3 прямі':>12} {'hit@3 перефр.':>14} {'токенів (k=3)':>14}"
)


def hit_rate(index, subset, k):
    hits = sum(
        1
        for case in subset
        if any(norm(case["must_contain"]) in norm(r["text"]) for r in index.search(case["question"], k))
    )
    return hits / len(subset)


direct = [c for c in answerable if c["kind"] == "direct"]
paraphrase = [c for c in answerable if c["kind"] == "paraphrase"]
for cfg in CONFIGS:
    chunks = chunking.make_chunks(docs, cfg["method"], cfg["size"], cfg["overlap"], cfg["title"])
    index = rag.Index.build(chunks)
    mean_len = sum(len(c["text"]) for c in chunks) / len(chunks)
    row = [hit_rate(index, answerable, k) for k in KS]
    print(
        f"{cfg['name']:22} {len(chunks):6} {mean_len:11.0f} "
        + " ".join(f"{h:6.2f}" for h in row)
        + f" {hit_rate(index, direct, 3):12.2f} {hit_rate(index, paraphrase, 3):14.2f} {3 * mean_len / 2.5:14.0f}"
    )