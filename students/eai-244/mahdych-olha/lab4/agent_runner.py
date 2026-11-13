"""П'ять коротких задач ЛР3 на налаштуваннях ЛР4; результати окремі."""
import os
import json
from pathlib import Path
from measure import run_one, run_id_for
if __name__=="__main__":
    os.chdir(Path(__file__).resolve().parent)
    target=Path("logs/run_lab3.log")
    if target.exists(): raise SystemExit("STOP: logs/run_lab3.log exists")
    tasks=json.loads(Path("tasks.json").read_text(encoding="utf-8"))
    for i in range(len(tasks)):
        code=run_one("none",1,"baseline",short=i)
        if code: raise SystemExit(code)
    target.write_text("\n".join((Path("logs")/(run_id_for("baseline","none",1,i)+".log")).read_text(encoding="utf-8") for i in range(len(tasks))),encoding="utf-8")
    print("SAVED:",target)
