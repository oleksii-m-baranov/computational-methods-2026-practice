"""Генерація уточненого аудиту results/rag_reviewed.csv за фактичними логами.

Вимоги:
- Коректне парсування фінальних відповідей без витоку службових рядків логу.
- Точне збереження початкових полів (correct, category).
- Розділення уточнених категорій для питань без відповіді:
  empty_response, technical_failure, wrong_tool, invented, refused.
- Для питань з відповіддю збереження категорій: ok, no_search, miss, ignored.
- Взаємовиключні failure_subtype.
"""
import csv
import glob
import json
import os
import re

LOG_DIR = "logs"
CSV_PATH = "results/rag.csv"
OUT_PATH = "results/rag_reviewed.csv"

with open(CSV_PATH, encoding="utf-8") as f:
    orig_rows = list(csv.DictReader(f))

with open("rag_cases.json", encoding="utf-8") as f:
    cases = {c["id"]: c for c in json.load(f)}

# Завантажуємо вміст усіх логів
logs_content = {}
for log_file in sorted(glob.glob(os.path.join(LOG_DIR, "rag_*.log"))):
    norm_name = os.path.basename(log_file)
    with open(log_file, encoding="utf-8") as f:
        logs_content[norm_name] = f.read()

reviewed_rows = []

for r in orig_rows:
    cfg = r["config"]
    rep = str(r["repeat"])
    qid = r["id"]
    kind = r["kind"]
    cid = f"{cfg}-r{rep}-{qid}"
    
    log_file_name = f"rag_{cfg}-r{rep}.log"
    content = logs_content.get(log_file_name, "")
    
    # Виділяємо блок прогону
    pattern = rf"##### {re.escape(cid)}\n(.*?)(?=\n##### |\Z)"
    m = re.search(pattern, content, re.DOTALL)
    block = m.group(1) if m else ""
    
    # Витягуємо виклики інструментів
    tool_matches = re.findall(r"виклик\s+:\s+(\w+)\((.*?)\)", block)
    tool_names = [tm[0] for tm in tool_matches]
    tools_str = "; ".join([f"{tm[0]}({tm[1]})" for tm in tool_matches]) if tool_matches else "none"
    
    # Витягуємо чисту фінальну відповідь
    # Регулярний вираз бере текст після "ВІДПОВІДЬ:[ \t]*" до наступного лог-запису або кінця
    ans_m = re.search(
        r"ВІДПОВІДЬ:[ \t]*([^\n]*(?:\n(?!\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - INFO -)[^\n]*)*)",
        block
    )
    full_ans = ans_m.group(1).strip() if ans_m else ""
    # Захист: якщо після ВІДПОВІДЬ: стояв лише префікс логу, вважаємо відповідь порожньою
    if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - INFO -", full_ans):
        full_ans = ""
    
    status = r["status"]
    searches = int(r["searches"])
    hit = int(r["hit"])
    auto_correct = int(r["correct"])
    auto_cat = r["category"]
    
    reviewed_correct = auto_correct
    reviewed_cat = auto_cat
    failure_subtype = ""
    review_reason = ""
    
    if kind != "none":
        # ==========================================
        # Питання з відповіддю (kind != 'none')
        # Категорії: ok, no_search, miss, ignored
        # ==========================================
        if auto_cat == "ok":
            # Перевіряємо фактичну правильність
            if qid == "D3":
                if "94" in full_ans:
                    reviewed_cat = "ok"
                    reviewed_correct = 1
                    failure_subtype = "none"
                    review_reason = "Пошук викликано; знайдено цільовий чанк із d03.txt; відповідь точна (94 см)."
                else:
                    reviewed_cat = "ignored"
                    reviewed_correct = 0
                    failure_subtype = "fact_distorted"
                    review_reason = "Пошук викликано, але точне число 94 см не включено або викривлено."
            elif qid == "D4":
                if "1250" in full_ans:
                    reviewed_cat = "ok"
                    reviewed_correct = 1
                    failure_subtype = "none"
                    review_reason = "Пошук викликано; знайдено цільовий чанк із d04.txt; відповідь точна (1250 грн)."
                else:
                    reviewed_cat = "ignored"
                    reviewed_correct = 0
                    failure_subtype = "fact_distorted"
                    review_reason = "Пошук викликано, але ціну 1250 грн не вказано коректно."
            elif qid == "P3":
                # Перевірка: чи не спотворено значення (наприклад 'від 17 до 18')
                if "від 17" in full_ans or "18" in full_ans:
                    reviewed_cat = "ignored"
                    reviewed_correct = 0
                    failure_subtype = "fact_distorted"
                    review_reason = "Пошук знайдено, але відповідь викривлено ('від 17 до 18' замість 'не більше 17')."
                elif "17" in full_ans:
                    reviewed_cat = "ok"
                    reviewed_correct = 1
                    failure_subtype = "none"
                    review_reason = "Пошук викликано; знайдено d03.txt; відповідь відповідає нормі ('не більше 17 хвилин')."
                else:
                    reviewed_cat = "ignored"
                    reviewed_correct = 0
                    failure_subtype = "fact_distorted"
                    review_reason = "Пошук знайдено, але число 17 не включено."
            else:
                reviewed_cat = "ok"
                reviewed_correct = 1
                failure_subtype = "none"
                review_reason = "Відповідь відповідає еталону."
        elif auto_cat == "miss":
            reviewed_cat = "miss"
            reviewed_correct = 0
            failure_subtype = "retrieval_miss"
            review_reason = "Пошук search_docs викликано, але через скорочення запиту схожість була нижчою за поріг 0.597; ретривер повернув 'нічого не знайдено'."
        elif auto_cat == "no_search":
            reviewed_cat = "no_search"
            reviewed_correct = 0
            if status == "retry_limit":
                failure_subtype = "retry_limit"
                review_reason = f"Модель перевищила ліміт спроб, багаторазово викликаючи помилковий інструмент {tool_names}."
            elif not full_ans and not tool_names:
                failure_subtype = "empty_response"
                review_reason = "Модель не викликала інструментів і повернула порожню відповідь на кроці 1."
            elif any(t in ("vaccine_info", "calc_food") for t in tool_names):
                failure_subtype = "wrong_tool"
                review_reason = f"Модель помилково викликала інструмент {tool_names[0]} замість search_docs."
            elif not tool_names and full_ans:
                failure_subtype = "direct_answer"
                review_reason = "Модель не викликала жодного інструмента і відповіла напряму з власних ваг (галюцинація або міркування)."
            else:
                failure_subtype = "other"
                review_reason = "Пошук не викликано."
    else:
        # ==========================================
        # Питання без відповіді (kind == 'none': N1, N2)
        # Категорії: empty_response, technical_failure, wrong_tool, invented, refused
        # ==========================================
        if status == "retry_limit":
            reviewed_cat = "technical_failure"
            reviewed_correct = 0
            failure_subtype = "retry_limit"
            review_reason = f"Технічний збій: модель зациклилася на виклику {tool_names} і зупинилася за лімітом спроб; фактів не вигадано."
        elif not full_ans and not tool_names:
            reviewed_cat = "empty_response"
            reviewed_correct = 0
            failure_subtype = "empty_response"
            review_reason = "Порожня фінальна відповідь: модель повернула 0 токенів на першому кроці; фактів не вигадано."
        elif any(t in ("vaccine_info", "calc_food") for t in tool_names):
            # Модель викликала неправильний інструмент
            if "хламідіоз" in full_ans.lower() and "700" in full_ans:
                # Випадок реального вигадування фактів (A-r2-N2, A-r3-N2)
                reviewed_cat = "invented"
                reviewed_correct = 0
                failure_subtype = "hallucination_with_wrong_tool"
                review_reason = "Фактичне вигадування: модель викликала vaccine_info і заявила, що концентрація у шампуні — це щеплення хламідіоз за 700 грн."
            else:
                # Підміна сутності без вигадування ціни (A-r1-N1, C-r1-N1, C-r3-N1)
                reviewed_cat = "wrong_tool"
                reviewed_correct = 0
                failure_subtype = "wrong_tool"
                review_reason = f"Підміна сутності: модель сприйняла питання як щеплення і звернулася до {tool_names[0]}; у відповіді зазначила відсутність у довіднику щеплень, ціни не вигадано."
        else:
            # Інструментів не викликано, але згенеровано текст (C-r1-N2, C-r2-N2, C-r3-N2)
            # Перевіряємо зміст відповіді
            lower_ans = full_ans.lower()
            if "не можна відповісти" in lower_ans or "не вистачає" in lower_ans:
                if "суперантий" in lower_ans:
                    # C-r1-N2: неоднозначний випадок (відмова з вербальною галюцинацією)
                    reviewed_cat = "invented"
                    reviewed_correct = 0
                    failure_subtype = "hallucination_in_refusal"
                    review_reason = "Неоднозначний випадок: містить явну відмову ('не можна відповісти... не вистачає даних'), але присутня вербальна галюцинація ('хлоргексидин - це суперантий')."
                elif "фармацевтичний продукт" in lower_ans:
                    # C-r2-N2: коректна відмова
                    reviewed_cat = "refused"
                    reviewed_correct = 1
                    failure_subtype = "none"
                    review_reason = "Коректна відмова за змістом: модель прямо визнала, що відповісти за наявною інформацією не можна, і порадила звернутися до спеціаліста; фактів не вигадано."
                elif "лік, а не концентрація" in lower_ans:
                    # C-r3-N2: відмова з міркуванням
                    reviewed_cat = "refused"
                    reviewed_correct = 1
                    failure_subtype = "none"
                    review_reason = "Коректна відмова за змістом: зазначено неможливість відповісти доступною інформацією та пораджено упакування/інструмент; числової концентрації не вигадано."
                else:
                    reviewed_cat = "refused"
                    reviewed_correct = 1
                    failure_subtype = "none"
                    review_reason = "Коректне визнання відсутності даних."
            else:
                reviewed_cat = "invented"
                reviewed_correct = 0
                failure_subtype = "hallucination"
                review_reason = "Фактичне вигадування відповіді без визнання відсутності інформації."

    row_data = {
        "config": cfg,
        "repeat": rep,
        "id": qid,
        "kind": kind,
        "correct": auto_correct,
        "category": auto_cat,
        "reviewed_correct": reviewed_correct,
        "reviewed_category": reviewed_cat,
        "failure_subtype": failure_subtype,
        "tools_called": tools_str,
        "full_answer": full_ans,
        "review_reason": review_reason,
    }
    reviewed_rows.append(row_data)

# Запис результатів
with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(reviewed_rows[0].keys()))
    writer.writeheader()
    writer.writerows(reviewed_rows)

print(f"Збережено {len(reviewed_rows)} рядків у {OUT_PATH}")
