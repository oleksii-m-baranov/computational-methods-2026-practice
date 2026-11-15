"""Підрахунок перевіреної статистики RAG-агента за уточненим аудитом rag_reviewed.csv."""
import csv
import os
import statistics

CSV_PATH = "results/rag.csv"
REV_PATH = "results/rag_reviewed.csv"
OUT_SUMMARY = "results/summary_reviewed.txt"

with open(CSV_PATH, encoding="utf-8") as f:
    raw_rows = list(csv.DictReader(f))

with open(REV_PATH, encoding="utf-8") as f:
    rev_rows = list(csv.DictReader(f))

# Зв'язуємо рядки за ключем (config, repeat, id)
data_by_key = {}
for r in raw_rows:
    key = (r["config"], str(r["repeat"]), r["id"])
    data_by_key[key] = dict(r)

for r in rev_rows:
    key = (r["config"], str(r["repeat"]), r["id"])
    data_by_key[key].update(r)

all_records = list(data_by_key.values())

lines = []
def log(s=""):
    print(s)
    lines.append(s)

log("================================================================================")
log("             ПІДСУМКОВА СТАТИСТИКА RAG-ЕКСПЕРИМЕНТІВ (УТОЧНЕНИЙ АУДИТ)         ")
log("================================================================================\n")

# 1. Контрольні медіани за всіма 30 прогонами кожного опису
log("1. КОНТРОЛЬНІ МЕДІАНИ ЗА ВСІМА 30 ПРОГОНАМИ КОЖНОГО ОПИСУ:")
log(f"{'Опис':<6} | {'Кроків (медіана)':<18} | {'Вхідних токенів (медіана)':<28} | {'Час, с (медіана)':<18}")
log("-" * 78)
for cfg in ["A", "B", "C"]:
    part = [r for r in all_records if r["config"] == cfg]
    steps_med = statistics.median(int(r["steps"]) for r in part)
    tokens_med = statistics.median(int(r["prompt_tokens"]) for r in part)
    secs_med = statistics.median(float(r["seconds"]) for r in part)
    log(f"{cfg:<6} | {steps_med:<18.1f} | {tokens_med:<28.1f} | {secs_med:<18.2f}")

log("\n" + "=" * 80 + "\n")

# 2. Питання з відповіддю (24 прогони на кожен опис)
log("2. ПИТАННЯ З ВІДПОВІДДЮ (24 ПРОГОНИ НА ОПИС):")
log(f"{'Опис':<6} | {'ok':<5} | {'no_search':<10} | {'miss':<6} | {'ignored':<8} | {'Сума':<6} | {'Точність (ok/24)':<18}")
log("-" * 70)
for cfg in ["A", "B", "C"]:
    part = [r for r in all_records if r["config"] == cfg and r["kind"] != "none"]
    ok_cnt = sum(1 for r in part if r["reviewed_category"] == "ok")
    ns_cnt = sum(1 for r in part if r["reviewed_category"] == "no_search")
    miss_cnt = sum(1 for r in part if r["reviewed_category"] == "miss")
    ign_cnt = sum(1 for r in part if r["reviewed_category"] == "ignored")
    total_ans = len(part)
    assert total_ans == 24, f"Очікувалось 24 прогони, отримано {total_ans}"
    assert ok_cnt + ns_cnt + miss_cnt + ign_cnt == 24, "Сума категорій не дорівнює 24"
    log(f"{cfg:<6} | {ok_cnt:<5} | {ns_cnt:<10} | {miss_cnt:<6} | {ign_cnt:<8} | {total_ans:<6} | {ok_cnt}/{total_ans} ({ok_cnt/total_ans:.1%})")

log("\n   Деталізація підтипів no_search (взаємовиключний розподіл):")
log(f"   {'Опис':<6} | {'wrong_tool':<12} | {'empty_response':<16} | {'direct_answer':<15} | {'retry_limit':<13} | {'Сума підтипів':<15}")
log("   " + "-" * 75)
for cfg in ["A", "B", "C"]:
    part = [r for r in all_records if r["config"] == cfg and r["kind"] != "none" and r["reviewed_category"] == "no_search"]
    wt = sum(1 for r in part if r["failure_subtype"] == "wrong_tool")
    er = sum(1 for r in part if r["failure_subtype"] == "empty_response")
    da = sum(1 for r in part if r["failure_subtype"] == "direct_answer")
    rl = sum(1 for r in part if r["failure_subtype"] == "retry_limit")
    sub_sum = wt + er + da + rl
    log(f"   {cfg:<6} | {wt:<12} | {er:<16} | {da:<15} | {rl:<13} | {sub_sum:<15} (очікувалось {len(part)})")
    assert sub_sum == len(part), f"Сума підтипів {sub_sum} != {len(part)}"

log("\n" + "=" * 80 + "\n")

# 3. Питання без відповіді (6 прогонів на кожен опис)
log("3. ПИТАННЯ БЕЗ ВІДПОВІДІ (N1, N2 — 6 ПРОГОНІВ НА ОПИС):")
log(f"{'Опис':<6} | {'refused':<8} | {'wrong_tool':<12} | {'technical_fail':<16} | {'empty_response':<16} | {'invented':<10} | {'Сума':<6}")
log("-" * 80)
for cfg in ["A", "B", "C"]:
    part = [r for r in all_records if r["config"] == cfg and r["kind"] == "none"]
    ref_cnt = sum(1 for r in part if r["reviewed_category"] == "refused")
    wt_cnt = sum(1 for r in part if r["reviewed_category"] == "wrong_tool")
    tf_cnt = sum(1 for r in part if r["reviewed_category"] == "technical_failure")
    er_cnt = sum(1 for r in part if r["reviewed_category"] == "empty_response")
    inv_cnt = sum(1 for r in part if r["reviewed_category"] == "invented")
    total_none = len(part)
    assert total_none == 6, f"Очікувалось 6 прогонів, отримано {total_none}"
    assert ref_cnt + wt_cnt + tf_cnt + er_cnt + inv_cnt == 6, "Сума категорій не дорівнює 6"
    log(f"{cfg:<6} | {ref_cnt:<8} | {wt_cnt:<12} | {tf_cnt:<16} | {er_cnt:<16} | {inv_cnt:<10} | {total_none:<6}")

log("\n" + "=" * 80 + "\n")

# 4. Загальна точність
log("4. ЗВЕДЕНА ТОЧНІСТЬ ТА ВИКЛИКИ ПОШУКУ:")
log(f"{'Опис':<6} | {'З відповіддю (ok/24)':<22} | {'Без відповіді (refused/6)':<28} | {'Загальна (ok+ref)/30':<22} | {'Викликів search_docs':<20}")
log("-" * 105)
for cfg in ["A", "B", "C"]:
    ans_part = [r for r in all_records if r["config"] == cfg and r["kind"] != "none"]
    none_part = [r for r in all_records if r["config"] == cfg and r["kind"] == "none"]
    all_part = [r for r in all_records if r["config"] == cfg]
    
    ok_c = sum(1 for r in ans_part if r["reviewed_category"] == "ok")
    ref_c = sum(1 for r in none_part if r["reviewed_category"] == "refused")
    tot_correct = ok_c + ref_c
    searches_total = sum(int(r["searches"]) for r in all_part)
    searches_none = sum(int(r["searches"]) for r in none_part)
    
    log(f"{cfg:<6} | {ok_c}/24 ({ok_c/24:.1%}){'':<11} | {ref_c}/6 ({ref_c/6:.1%}){'':<17} | {tot_correct}/30 ({tot_correct/30:.1%}){'':<11} | {searches_total} (з них на N1/N2: {searches_none})")

log("\n================================================================================")

with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"\nПідсумковий звіт збережено у {OUT_SUMMARY}")
