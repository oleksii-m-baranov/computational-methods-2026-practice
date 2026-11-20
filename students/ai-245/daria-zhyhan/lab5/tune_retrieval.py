import eval_retrieval

configs = [
    ("fixed", 400, 0, False),
    ("fixed", 400, 80, False),
    ("fixed", 800, 0, False),
    ("fixed", 800, 150, False),
    ("paragraphs", 800, 0, False),
    ("paragraphs", 800, 0, True),
]

print(f"{'Метод':<12} {'Розмір':<7} {'Перекр.':<8} {'Title':<7} {'Чанків':<7} {'Hit@1':<8} {'Hit@3':<8} {'MRR':<7} {'MinPos':<8} {'MaxNeg':<8}")
print("-" * 88)

for method, size, overlap, title in configs:
    m = eval_retrieval.evaluate(method=method, size=size, overlap=overlap, with_title=title, top_k=3, verbose=False)
    print(f"{method:<12} {size:<7} {overlap:<8} {str(title):<7} {m['chunks']:<7} "
          f"{m['hit1']:<8.2%} {m['hitk']:<8.2%} {m['mrr']:<7.3f} {m['min_pos']:<8.4f} {m['max_neg']:<8.4f}")