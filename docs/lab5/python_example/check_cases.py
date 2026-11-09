"""Перевірка файла rag_cases.json: кожен факт має бути в документах рівно в одному місці."""
import collections
import json
import re
import sys

import chunking
import config


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


with open("rag_cases.json", encoding="utf-8") as f:
    cases = json.load(f)

docs = chunking.load_documents(config.DOC_DIRS)
whole = " ".join(norm(d["text"]) for d in docs)
problems = []

ids = [c["id"] for c in cases]
if len(ids) != len(set(ids)):
    problems.append("Повторюються id питань")
kinds = collections.Counter(c["kind"] for c in cases)
for kind, need in [("direct", 4), ("paraphrase", 4), ("none", 2)]:
    if kinds[kind] != need:
        problems.append(f"Питань виду {kind}: {kinds[kind]}, а треба {need}")

for case in cases:
    if case["kind"] == "none":
        if case["must_contain"] is not None or case["expected"] is not None:
            problems.append(f"{case['id']}: у питання без відповіді must_contain і expected мають бути null")
        continue
    found = whole.count(norm(case["must_contain"]))
    if found != 1:
        problems.append(f"{case['id']}: фраза '{case['must_contain']}' зустрічається в документах {found} раз(ів), а треба рівно 1")
    if case["expected"] not in case["must_contain"]:
        problems.append(f"{case['id']}: expected '{case['expected']}' не міститься у must_contain")

total_chars = sum(len(d["text"]) for d in docs)
tokens = total_chars / 2.5
print(f"Документів: {len(docs)}; символів: {total_chars}; приблизно токенів: {tokens:.0f} (вікно {config.NUM_CTX})")
if tokens < config.NUM_CTX:
    problems.append("Усі документи вміщуються у вікно моделі: додайте текст, інакше пошук не потрібен")
print(f"Питань: {len(cases)} ({dict(kinds)})")
if problems:
    print("\nПроблеми:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("Усе гаразд")
