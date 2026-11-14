import json
import config
import schemas
from agent import run_agent


def run_variant(variant, cases):
    config.DOCS_DESCRIPTION = variant
    config.RUN_TAG = f"rag-desc-{variant}"
    schemas.SCHEMAS[:] = schemas.build_schemas()

    print(f"\n{'=' * 75}")
    print(f"ТЕСТУВАННЯ ОПИСУ search_docs = '{variant}'")
    print(f"{'=' * 75}")

    correct = 0
    for c in cases:
        ans = run_agent(c["question"], logfile_name=f"lab5_desc_{variant}", task_id=c["id"])
        ans_text = ans or "(None)"
        if c["kind"] != "none":
            ok = c["expected"] in ans_text
        else:
            refusal_markers = [
                "немає", "відсутн", "не знайдено", "не вказано",
                "не міст", "нема", "не доступн", "недоступн", "не можу"
            ]
            ok = any(m in ans_text.lower() for m in refusal_markers)
        if ok:
            correct += 1
        status = "OK" if ok else "FAIL"
        short_ans = ans_text.replace("\n", " ")[:95]
        print(f"[{status:<4}] {c['id']:<3} ({c['kind']:<10}) -> {short_ans}")

    print(f"--> Підсумок для опису '{variant}': {correct}/{len(cases)} ({correct / len(cases):.0%})")
    return correct


if __name__ == "__main__":
    with open("rag_cases.json", encoding="utf-8") as f:
        cases = json.load(f)

    summary = {}
    for v in ["A", "B", "C"]:
        summary[v] = run_variant(v, cases)

    print(f"\n{'=' * 75}")
    print("ЗВЕДЕНА ТАБЛИЦЯ ПОРІВНЯННЯ ОПИСІВ ІНСТРУМЕНТУ:")
    for v, score in summary.items():
        print(f"  Варіант {v}: {score}/{len(cases)} правильних відповідей")

    config.DOCS_DESCRIPTION = "C"
    config.RUN_TAG = "rag-mixed"
    schemas.SCHEMAS[:] = schemas.build_schemas()

    mixed_tasks = [
        "Знайди через пошук у документах, скільки мілілітрів системного інсектициду на 1 літр води використовують для поливу проти щитівки, і порахуй через калькулятор загальну кількість препарату для 3.5 літрів води.",
        "Перевір у довіднику дозу добрива на літр для рослини Монстера та обчисли загальну дозу для горщика об'ємом 4 літри.",
    ]
    print(f"\n{'=' * 75}")
    print("ПЕРЕВІРКА ЗМІШАНИХ ЗАДАЧ (ПОШУК + ОБЧИСЛЕННЯ):")
    for i, t in enumerate(mixed_tasks, 1):
        ans = run_agent(t, logfile_name="lab5_mixed", task_id=f"M{i}")
        print(f"\nЗадача M{i}: {t}\nВідповідь: {ans}")