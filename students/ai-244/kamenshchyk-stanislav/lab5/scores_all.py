"""Схожість першого результату (як python check_retrieval.py scores) для всіх шести нарізань.
Потрібен, щоб вибрати нарізання і поріг MIN_SCORE за один запуск. Запуск: python scores_all.py"""
import json
import re

import chunking
import config
import rag

# ті самі шість нарізань, що в check_retrieval.py
CONFIGS = [
    {"name": "fixed-200-0",       "method": "fixed",      "size": 200,  "overlap": 0,   "title": False},
    {"name": "fixed-500-0",       "method": "fixed",      "size": 500,  "overlap": 0,   "title": False},
    {"name": "fixed-500-100",     "method": "fixed",      "size": 500,  "overlap": 100, "title": False},
    {"name": "fixed-1500-0",      "method": "fixed",      "size": 1500, "overlap": 0,   "title": False},
    {"name": "paragraphs-800",    "method": "paragraphs", "size": 800,  "overlap": 0,   "title": False},
    {"name": "paragraphs-800+title", "method": "paragraphs", "size": 800, "overlap": 0, "title": True},
]


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


with open("rag_cases.json", encoding="utf-8") as f:
    cases = json.load(f)
docs = chunking.load_documents(config.DOC_DIRS)

for cfg in CONFIGS:
    index = rag.Index.build(chunking.make_chunks(docs, cfg["method"], cfg["size"], cfg["overlap"], cfg["title"]))
    print(f"\n=== {cfg['name']}")
    good, bad = [], []
    for case in cases:
        top = index.search(case["question"], 1)[0]
        has = case["must_contain"] is not None and norm(case["must_contain"]) in norm(top["text"])
        (bad if case["kind"] == "none" else good).append(top["score"])
        mark = "-" if case["kind"] == "none" else ("так" if has else "НІ")
        print(f"{case['id']:4} {case['kind']:11} {top['score']:.3f}  {mark}  ({top['source']}, чанк {top['chunk']})")
    print(f"мін. з відповіддю {min(good):.3f} | макс. без відповіді {max(bad):.3f} | "
          + ("розділяються" if max(bad) < min(good) else "перекриваються"))
