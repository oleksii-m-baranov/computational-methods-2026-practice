"""Виконує всі кроки лабораторної № 4 підряд і зберігає виведення кожного кроку в outputs/.

Запуск (з каталогу lab4, Ollama запущений, .env з ключами Langfuse поруч):
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
ENV = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
BASE_MODEL = "qwen2.5:3b"


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
        text, n = re.subn(rf"^{name} = [^#\n]*", f"{name} = {value!r}".replace("'", '"') + "  ", text, flags=re.M)
        assert n == 1, name
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(text)


def describe_log(path):
    """Показники прогону (metrics.py) з актуальним config.py."""
    proc = subprocess.run(py("-c", (
        "import json,config;from logparse import parse_log;from metrics import describe;"
        f"d=describe(parse_log(open({path!r},encoding='utf-8').read())[0]);"
        "d.pop('squeezes');print(json.dumps(d))")), env=ENV, capture_output=True, text=True, encoding="utf-8")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def read_config(name):
    proc = subprocess.run(py("-c", f"import config;print(config.{name})"), env=ENV,
                          capture_output=True, text=True, encoding="utf-8")
    return proc.stdout.strip()


def which_case(d, num_ctx):
    if d["status"] == "server_error":
        return "A"
    if d["stall"]:
        return "B"
    if d["max_tokens"] < 0.95 * num_ctx and d["status"] == "final":
        return "C"
    return "D"


def main():
    if not os.environ.get("LANGFUSE_PUBLIC_KEY"):
        print("УВАГА: не знайдено LANGFUSE_PUBLIC_KEY. Покладіть .env з ключами Langfuse у lab4 "
              "(або в корінь репозиторію), інакше траси для скріншотів не запишуться.")
        try:
            if input("Продовжити без Langfuse? [y/N] ").strip().lower() != "y":
                return
        except EOFError:                 # немає інтерактивного вводу (Colab "!python"): продовжуємо
            print("Продовжую без Langfuse.")

    # Крок 1. Модель з вікном 4096
    run(["ollama", "pull", BASE_MODEL], "00_pull.txt")
    run(["ollama", "create", "qwen25-4k", "-f", "Modelfile"], "01a_create_4k.txt")
    run(["ollama", "show", "qwen25-4k"], "01b_show_qwen25-4k.txt")
    run(["ollama", "show", BASE_MODEL], "01c_show_base.txt")

    # Крок 2. Довга задача. У першій спробі (attempt1/) модель викликала 12 інструментів за один крок
    # і відповіла на другому кроці, тому пробуємо формулювання з вимогою працювати по черзі
    choice_file = os.path.join(OUT, "02a_question_choice.json")
    if not os.path.exists(choice_file):
        tried = {}
        for variant in ("v2", "v3"):
            run(py("make_task.py", variant), f"02a_make_task_{variant}.txt")
            run(py("measure.py", "none", "1", f"q{variant}"), f"02a_qprobe_{variant}.txt")
            tried[variant] = describe_log(f"logs/q{variant}_none_r1.log")
            if tried[variant]["steps"] >= 10:            # ланцюжок вийшов довгим - беремо це формулювання
                break
        best = max(tried, key=lambda v: tried[v]["steps"])
        with open("long_task_variant.txt", "w", encoding="utf-8") as f:
            f.write(best)
        with open(choice_file, "w", encoding="utf-8") as f:
            json.dump({"chosen": best, "tried": tried}, f, ensure_ascii=False, indent=2)
        print(f"Вибрано формулювання {best}: кроків {tried[best]['steps']}")
    run(py("make_task.py"), "02_make_task.txt")

    # Крок 3. Перевірка агента і пробний прогін без захисту
    run(py("agent.py"), "03a_agent_check.txt")
    run(py("measure.py", "none", "1", "probe"), "03b_probe_none.txt")

    # Крок 4. Розбір і випадок A-D
    run(py("analyze.py", "logs/probe_none_r1.log", "steps"), "04a_analyze_probe_none.txt")
    case_file = os.path.join(OUT, "04b_case.json")
    if not os.path.exists(case_file):
        d = describe_log("logs/probe_none_r1.log")
        case = which_case(d, int(read_config("NUM_CTX")))
        info = {"window_4096": {"case": case, **d}}
        if case == "C":                          # задача закоротка: вікно 3072
            print("\nВипадок C: зменшую вікно до 3072 і повторюю пробний прогін")
            shutil.copy("logs/probe_none_r1.log", "logs/probe_none_r1_4k.log")
            with open("Modelfile", "w", encoding="utf-8") as f:
                f.write(f"FROM {BASE_MODEL}\nPARAMETER num_ctx 3072\n")
            run(["ollama", "create", "qwen25-3k", "-f", "Modelfile"], "04c_create_3k.txt")
            run(["ollama", "show", "qwen25-3k"], "04d_show_qwen25-3k.txt")
            set_config(MODEL="qwen25-3k", NUM_CTX=3072, COMPRESS_AT=2150)
            run(py("measure.py", "none", "1", "probe"), "04e_probe_none_3k.txt")
            run(py("analyze.py", "logs/probe_none_r1.log", "steps"), "04f_analyze_probe_none_3k.txt")
            d = describe_log("logs/probe_none_r1.log")
            info["window_3072"] = {"case": which_case(d, 3072), **d}
        # якщо вхід у прогоні без захисту так і не перевищив поріг, обрізання не спрацює жодного разу
        at = int(read_config("COMPRESS_AT"))
        if d["max_tokens"] <= at:
            new_at = int(round(0.7 * d["max_tokens"], -2))
            set_config(COMPRESS_AT=new_at)
            info["compress_at_changed"] = {"from": at, "to": new_at, "max_tokens_none": d["max_tokens"]}
        with open(case_file, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        print(json.dumps(info, ensure_ascii=False, indent=2))

    # Кроки 5-6. Обрізання і стан
    run(py("measure.py", "trim", "1", "probe"), "05a_probe_trim.txt")
    run(py("analyze.py", "logs/probe_trim_r1.log", "steps"), "05b_analyze_probe_trim.txt")
    run(py("measure.py", "trim+state", "1", "probe"), "06a_probe_trim+state.txt")
    run(py("analyze.py", "logs/probe_trim+state_r1.log", "steps"), "06b_analyze_probe_trim+state.txt")

    # Крок 7. Кеш: два однакові прогони, перед першим кеш очищується
    if not os.path.exists(os.path.join(OUT, "07a_cache1.txt")):
        shutil.rmtree("cache", ignore_errors=True)
    run(py("measure.py", "none", "1", "cache1"), "07a_cache1.txt")
    run(py("analyze.py", "logs/cache1_none_r1.log"), "07b_analyze_cache1.txt")
    run(py("measure.py", "none", "1", "cache2"), "07c_cache2.txt")
    run(py("analyze.py", "logs/cache2_none_r1.log"), "07d_analyze_cache2.txt")

    # Крок 8. Основне вимірювання: 3 конфігурації x 3 повтори
    run(py("measure.py", "all", "3", "main"), "08a_main.txt")
    for name in ["none", "trim", "trim+state"]:
        for r in (1, 2, 3):
            run(py("analyze.py", f"logs/main_{name}_r{r}.log"), f"08b_analyze_main_{name}_r{r}.txt")

    # Додаткове завдання: підсумовування
    run(py("measure.py", "summary", "3", "extra"), "09a_extra_summary.txt")
    for r in (1, 2, 3):
        run(py("analyze.py", f"logs/extra_summary_r{r}.log"), f"09b_analyze_extra_summary_r{r}.txt")

    # Звичайні задачі з tasks.json (лог logs/lab4.log знадобиться в лабораторній № 5)
    run(py("agent_runner.py"), "10_agent_runner.txt")

    print("\nГОТОВО. Виведення кожного кроку - у каталозі outputs/, логи - у logs/, стан - у state/.")
    print("Залишилось зробити скріншоти трас у Langfuse.")


if __name__ == "__main__":
    main()
