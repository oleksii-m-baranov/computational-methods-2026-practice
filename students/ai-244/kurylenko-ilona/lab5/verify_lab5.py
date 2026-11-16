"""Повна локальна перевірка виправлень ЛР5 без звернень до моделі."""
import csv
import glob
import os
import re

CSV_PATH = "results/rag.csv"
REV_PATH = "results/rag_reviewed.csv"
LOG_DIR = "logs"

print("=== 1. ПЕРЕВІРКА CSV: 90 УНІКАЛЬНИХ ПРОГОНІВ ===")
with open(REV_PATH, encoding="utf-8") as f:
    rev_rows = list(csv.DictReader(f))

assert len(rev_rows) == 90, f"Кількість рядків у {REV_PATH} = {len(rev_rows)} (має бути 90)"
keys = [(r["config"], r["repeat"], r["id"]) for r in rev_rows]
assert len(set(keys)) == 90, f"Унікальних ключів = {len(set(keys))} (має бути 90)"
print(f"OK: Рівно 90 унікальних прогонів у {REV_PATH}")

print("\n=== 2. ПЕРЕВІРКА ВІДСУТНОСТІ ВИТОКУ СЛУЖБОВИХ РЯДКІВ У full_answer ===")
leaks = []
for r in rev_rows:
    cid = f"{r['config']}-r{r['repeat']}-{r['id']}"
    ans = r["full_answer"]
    if "INFO -" in ans or "#####" in ans or re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", ans):
        leaks.append((cid, ans))

assert len(leaks) == 0, f"Виявлено витік службових рядків у {len(leaks)} прогонах: {leaks}"
print("OK: Жодного службового рядка (timestamp, INFO, #####) у full_answer не виявлено")

print("\n=== 3. ПЕРЕВІРКА ПІДТВЕРДЖЕНИХ ВИПАДКІВ B-r2-N1 ТА B-r3-N1 ===")
b_r2_n1 = [r for r in rev_rows if r["config"] == "B" and r["repeat"] == "2" and r["id"] == "N1"][0]
b_r3_n1 = [r for r in rev_rows if r["config"] == "B" and r["repeat"] == "3" and r["id"] == "N1"][0]
assert b_r2_n1["full_answer"] == "", f"B-r2-N1 full_answer не порожня: {b_r2_n1['full_answer']!r}"
assert b_r3_n1["full_answer"] == "", f"B-r3-N1 full_answer не порожня: {b_r3_n1['full_answer']!r}"
assert b_r2_n1["reviewed_category"] == "empty_response", f"B-r2-N1 category={b_r2_n1['reviewed_category']}"
assert b_r3_n1["reviewed_category"] == "empty_response", f"B-r3-N1 category={b_r3_n1['reviewed_category']}"
print(f"OK: B-r2-N1 -> full_answer='', category='{b_r2_n1['reviewed_category']}'")
print(f"OK: B-r3-N1 -> full_answer='', category='{b_r3_n1['reviewed_category']}'")

print("\n=== 4. ПЕРЕВІРКА ЗБЕРЕЖЕННЯ БАГАТОРАДКОВИХ ВІДПОВІДЕЙ ===")
multiline = [r for r in rev_rows if "\n" in r["full_answer"]]
print(f"Знайдено багаторядкових відповідей у CSV: {len(multiline)}")
for r in multiline:
    cid = f"{r['config']}-r{r['repeat']}-{r['id']}"
    lines_count = len(r["full_answer"].split("\n"))
    print(f"  {cid}: {lines_count} рядків, починається з: {r['full_answer'].splitlines()[0][:50]!r}")
assert len(multiline) == 3, f"Очікувалось 3 багаторядкові відповіді, знайдено {len(multiline)}"
print("OK: Багаторядкові відповіді збережено коректно")

print("\n=== 5. ПЕРЕВІРКА ЗБІГУ searches ТА СУМ ТОКЕНІВ З ЛОГАМИ ===")
with open(CSV_PATH, encoding="utf-8") as f:
    orig_rows = list(csv.DictReader(f))

for orig in orig_rows:
    cid = f"{orig['config']}-r{orig['repeat']}-{orig['id']}"
    log_file = os.path.join(LOG_DIR, f"rag_{orig['config']}-r{orig['repeat']}.log")
    with open(log_file, encoding="utf-8") as lf:
        log_text = lf.read()
    pattern = rf"##### {re.escape(cid)}\n(.*?)(?=\n##### |\Z)"
    m = re.search(pattern, log_text, re.DOTALL)
    assert m, f"Не знайдено блок для {cid} у {log_file}"
    block = m.group(1)
    
    # Виклики search_docs
    search_calls = len(re.findall(r"виклик\s+:\s+search_docs\(", block))
    assert search_calls == int(orig["searches"]), f"{cid}: викликів search_docs у лозі {search_calls} != {orig['searches']}"
    
    # Перевірка prompt_tokens: у rag.csv фіксується сумарна кількість prompt_tokens за всі кроки прогону
    pt_matches = re.findall(r"prompt_tokens=(\d+)", block)
    if pt_matches:
        sum_pt = sum(int(x) for x in pt_matches)
        assert sum_pt == int(orig["prompt_tokens"]), f"{cid}: сума prompt_tokens у лозі {sum_pt} != {orig['prompt_tokens']}"
print("OK: searches та prompt_tokens для всіх 90 прогонів повністю узгоджені з логами")

print("\n=== 6. ПЕРЕВІРКА no_search ДЛЯ ПИТАНЬ З ВІДПОВІДДЮ ===")
for cfg, exp_ns in [("A", 21), ("B", 23), ("C", 22)]:
    part = [r for r in rev_rows if r["config"] == cfg and r["kind"] != "none"]
    ns_cnt = sum(1 for r in part if r["reviewed_category"] == "no_search")
    assert ns_cnt == exp_ns, f"{cfg}: no_search = {ns_cnt} != {exp_ns}"
    print(f"OK: Опис {cfg} -> no_search = {ns_cnt} (рівно {exp_ns})")

print("\n=== 7. ПЕРЕВІРКА ЧАСТКОВОГО ОНОВЛЕННЯ В measure_rag.py ===")
with open("measure_rag.py", encoding="utf-8") as f:
    measure_code = f.read()

assert "new_keys = {(r[\"config\"], str(r[\"repeat\"]), r[\"id\"]) for r in rows}" in measure_code, "Логіка оновлення за складеним ключем відсутня"
assert "not in new_keys" in measure_code, "Логіка фільтрації not in new_keys відсутня"
print("OK: measure_rag.py оновлює записи за унікальним складеним ключем (config, repeat, id), не видаляючи інші повтори")

print("\n=== УСІ ЛОКАЛЬНІ ПЕРЕВІРКИ ПРОЙДЕНО УСПІШНО! ===")
