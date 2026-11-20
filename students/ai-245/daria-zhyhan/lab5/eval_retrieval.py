import json
import re

import config
import rag


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def evaluate(method=None, size=None, overlap=None, with_title=None, top_k=None, verbose=True):
    top_k = top_k if top_k is not None else config.TOP_K
    idx = rag.build_index(method=method, size=size, overlap=overlap, with_title=with_title)

    with open("rag_cases.json", encoding="utf-8") as f:
        cases = json.load(f)

    answerable = [c for c in cases if c["kind"] != "none"]
    unanswerable = [c for c in cases if c["kind"] == "none"]

    hits_1 = 0
    hits_k = 0
    rr_sum = 0.0
    pos_scores = []
    neg_scores = []

    if verbose:
        print(f"\n{'ID':<4} {'Тип':<11} {'Ранг':<6} {'Top1 Score':<11} {'Знайдено джерело':<20} {'Питання'}")
        print("-" * 95)

    for c in answerable:
        res = idx.search(c["question"], top_k=top_k, min_score=0.0)
        top1_score = res[0]["score"] if res else 0.0
        pos_scores.append(top1_score)

        target = norm(c["must_contain"])
        rank = None
        found_src = "-"
        for i, r in enumerate(res, 1):
            if target in norm(r["text"]):
                rank = i
                found_src = f"{r['source']}#{r['chunk']}"
                break

        if rank == 1:
            hits_1 += 1
        if rank is not None:
            hits_k += 1
            rr_sum += 1.0 / rank

        if verbose:
            rank_str = str(rank) if rank else "MISS"
            print(f"{c['id']:<4} {c['kind']:<11} {rank_str:<6} {top1_score:<11.4f} {found_src:<20} {c['question'][:42]}...")

    for c in unanswerable:
        res = idx.search(c["question"], top_k=top_k, min_score=0.0)
        top1_score = res[0]["score"] if res else 0.0
        neg_scores.append(top1_score)
        if verbose:
            top_src = f"{res[0]['source']}#{res[0]['chunk']}" if res else "-"
            print(f"{c['id']:<4} {c['kind']:<11} {'N/A':<6} {top1_score:<11.4f} {top_src:<20} {c['question'][:42]}...")

    n = len(answerable)
    metrics = {
        "chunks": len(idx.chunks),
        "hit1": hits_1 / n,
        "hitk": hits_k / n,
        "mrr": rr_sum / n,
        "min_pos": min(pos_scores),
        "max_neg": max(neg_scores),
    }
    if verbose:
        print("-" * 95)
        print(f"Чанків: {metrics['chunks']} | Hit@1: {metrics['hit1']:.2%} ({hits_1}/{n}) | "
              f"Hit@{top_k}: {metrics['hitk']:.2%} ({hits_k}/{n}) | MRR: {metrics['mrr']:.3f}")
        print(f"Мін. Top1 score для питань з відповіддю: {metrics['min_pos']:.4f} | "
              f"Макс. Top1 score для питань без відповіді (none): {metrics['max_neg']:.4f}")
    return metrics


if __name__ == "__main__":
    evaluate()