"""Виконує всі кроки лабораторної № 5 підряд і зберігає виведення кожного кроку в outputs/.

Запуск (з каталогу lab5, Ollama запущений, .env з ключами Langfuse поруч):
    python run_all.py

Якщо прогін перервався, просто запустіть ще раз: кроки, для яких уже є файл в outputs/,
пропускаються. Щоб повторити крок, видаліть його файл з outputs/.
"""
import json
import os
import re
import shutil
import subprocess
import sys

from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
load_dotenv()
OUT = "outputs"
os.makedirs(OUT, exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("results", exist_ok=True)
ENV = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")


def run(cmd, outfile, check=True):
    """Запускає команду, друкує й зберігає виведення. Пропускає, якщо файл уже є."""
    path = os.path.join(OUT, outfile)
    if os.path.exists(path):
        print(f"[пропускаю] {outfile} уже є")
        return open(path, encoding="utf-8").read()
    print(f"\n>>> {' '.join(cmd)}")
    proc = subprocess.run(cmd, env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace")
    text = f"$ {' '.join(cmd)}\n{proc.stdout}{proc.stderr}"
    print(proc.stdout[-3000:], proc.stderr[-2000:])
    if check and proc.returncode != 0:
        sys.exit(f"Команда завершилась з помилкою ({proc.returncode}). Деталі вище.")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def py(*args):
    return [sys.executable, *args]


def set_config(**values):
    """Змінює значення в config.py (рядки виду NAME = ...)."""
    with open("config.py", encoding="utf-8") as f:
        text = f.read()
    for name, value in values.items():
        literal = json.dumps(value, ensure_ascii=False) if isinstance(value, str) else repr(value)
        text, n = re.subn(rf"^{name} = [^#\n]*", f"{name} = {literal}  ", text, flags=re.M)
        assert n == 1, name
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(text)


def choose_chunking(table_text):
    """Найвищий hit@3, за рівності - менший розмір результату (токенів для k=3)."""
    params = {
        "fixed-200-0": ("fixed", 200, 0, False), "fixed-500-0": ("fixed", 500, 0, False),
        "fixed-500-100": ("fixed", 500, 100, False), "fixed-1500-0": ("fixed", 1500, 0, False),
        "paragraphs-800": ("paragraphs", 800, 0, False), "paragraphs-800+title": ("paragraphs", 800, 0, True),
    }
    rows = []
    for line in table_text.splitlines():
        parts = line.split()
        if parts and parts[0] in params and len(parts) == 9:
            rows.append({"name": parts[0], "hit3": float(parts[4]), "tokens": float(parts[8])})
    best = sorted(rows, key=lambda r: (-r["hit3"], r["tokens"]))[0]
    return best, params[best["name"]]


def choose_threshold(scores_text):
    low_good = float(re.search(r"Найнижча схожість серед питань з відповіддю: ([\d.]+)", scores_text).group(1))
    high_bad = float(re.search(r"Найвища схожість серед питань без відповіді: ([\d.]+)", scores_text).group(1))
    if high_bad < low_good:
        value, why = round((high_bad + low_good) / 2, 3), "межі не перекриваються: середина між ними"
    else:
        # пріоритет - не пропустити відповідь; від вигаданих відповідей захищає опис B
        value, why = round(low_good - 0.005, 3), "межі перекриваються: поріг трохи нижче найнижчої схожості питань з відповіддю"
    return {"low_good": low_good, "high_bad": high_bad, "MIN_SCORE": value, "why": why}


def main():
    if not os.environ.get("LANGFUSE_PUBLIC_KEY"):
        print("УВАГА: не знайдено LANGFUSE_PUBLIC_KEY. Покладіть .env з ключами Langfuse у lab5 "
              "(або в корінь репозиторію), інакше траси для скріншотів не запишуться.")
        try:
            if input("Продовжити без Langfuse? [y/N] ").strip().lower() != "y":
                return
        except EOFError:                 # немає інтерактивного вводу (Colab "!python"): продовжуємо
            print("Продовжую без Langfuse.")

    # Крок 1. Моделі та база для порівняння
    run(["ollama", "pull", "bge-m3"], "01a_pull_bge-m3.txt")
    run(["ollama", "create", "qwen25-4k", "-f", "Modelfile"], "01b_create_qwen25-4k.txt")
    lab4_log = os.path.join("..", "lab4", "logs", "lab4.log")
    if os.path.exists(lab4_log) and not os.path.exists("logs/run_lab4.log"):
        shutil.copy(lab4_log, "logs/run_lab4.log")

    # Крок 2. Перевірка питань і «чи вгадує модель без документів»
    run(py("check_cases.py"), "02a_check_cases.txt")
    run(py("guess_check.py", "D1", "D2", "P1"), "02b_guess_check.txt")

    # Крок 3. Нарізання одного документа
    run(py("show_chunks.py", "data/docs/d01.txt", "fixed", "200", "0"), "03a_chunks_fixed200.txt")
    run(py("show_chunks.py", "data/docs/d01.txt", "fixed", "500", "100"), "03b_chunks_fixed500_100.txt")
    run(py("show_chunks.py", "data/docs/d01.txt", "paragraphs", "800"), "03c_chunks_paragraphs800.txt")

    # Крок 4. Ембединги та індекс
    run(py("embed_check.py"), "04a_embed_check.txt")
    run(py("build_index.py"), "04b_build_index_initial.txt")

    # Крок 5. Пошук без агента: нарізання і поріг
    table = run(py("check_retrieval.py"), "05a_check_retrieval.txt")
    choice_file = os.path.join(OUT, "05c_choice.json")
    if not os.path.exists(choice_file):
        best, (method, size, overlap, title) = choose_chunking(table)
        set_config(CHUNK_METHOD=method, CHUNK_SIZE=size, CHUNK_OVERLAP=overlap, WITH_TITLE=title, MIN_SCORE=0.0)
        scores = run(py("check_retrieval.py", "scores"), "05b_scores.txt")
        threshold = choose_threshold(scores)
        set_config(MIN_SCORE=threshold["MIN_SCORE"])
        with open(choice_file, "w", encoding="utf-8") as f:
            json.dump({"chunking": best, "threshold": threshold}, f, ensure_ascii=False, indent=2)
    run(py("build_index.py"), "05d_build_index_final.txt")

    # Крок 6. Інструмент через диспетчер і перший запуск агента
    run(py("try_tool.py", "D1"), "06a_try_tool_D1.txt")
    run(py("try_tool.py", "N1"), "06b_try_tool_N1.txt")
    run(py("ask.py", "D1"), "06c_ask_D1.txt")

    # Крок 7. Три описи інструмента: пробний прогін, потім повний (90 запусків агента)
    run(py("measure_rag.py", "B", "1"), "07a_measure_B_trial.txt")
    run(py("measure_rag.py"), "07b_measure_all.txt")
    run(py("rag_report.py"), "07c_rag_report.txt")

    # Крок 9. Звичайні задачі після заміни пошуку (опис B)
    if not os.path.exists(os.path.join(OUT, "09_agent_runner.txt")):
        set_config(DOCS_DESCRIPTION="B")
        if os.path.exists("logs/lab5.log"):
            os.replace("logs/lab5.log", "logs/lab5_ask.log")      # там прогони ask.py
        run(py("agent_runner.py"), "09_agent_runner.txt")
        os.replace("logs/lab5.log", "logs/run_rag.log")

    # Додаткове завдання: Chroma
    run(py("chroma_test.py"), "10_chroma_test.txt")

    print("\nГОТОВО. Виведення кожного кроку - у outputs/, логи - у logs/, результати - у results/rag.csv.")
    print("Залишилось зробити скріншоти трас у Langfuse.")


if __name__ == "__main__":
    main()
