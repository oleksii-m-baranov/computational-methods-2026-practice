"""Контрольовані прогони: python measure.py none 1 probe; all 3 main."""
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

CONFIGS={
    "none":{"COMPRESS":"none","USE_STATE":False},
    "trim":{"COMPRESS":"trim","USE_STATE":False},
    "trim+state":{"COMPRESS":"trim","USE_STATE":True},
}

def is_correct(answer,expected):
    # Це лише перевірка наявності числа; остаточна оцінка — вручну.
    if not answer or expected=="": return False
    pattern=r"(?<![\d.])"+re.escape(str(expected))+r"(?![\d.])"
    return bool(re.search(pattern,answer.replace(",",".")))

def run_id_for(series,name,repeat,short=None):
    if not re.fullmatch(r"[A-Za-z0-9_-]+",series):
        raise ValueError("Series must contain only ASCII letters, digits, _ or -")
    suffix=f"_short{short+1}" if short is not None else ""
    return f"{series}_{name}_r{repeat}{suffix}"

def run_one(name,repeat,series,short=None):
    import config
    run_id=run_id_for(series,name,repeat,short)
    metadata=Path("results")/(run_id+".json")
    for file in [metadata,Path("logs")/(run_id+".log"),Path("state")/(run_id+".json")]:
        if file.exists():
            print("STOP: result already exists:",file)
            return 3
    cmd=[sys.executable,"-u","worker.py",name,str(repeat),series]
    if short is not None: cmd += ["--short",str(short)]
    print(f"START {run_id}; hard limit {config.RUN_TIMEOUT} seconds",flush=True)
    started=time.perf_counter()
    process=subprocess.Popen(cmd)
    status=None
    try:
        return process.wait(timeout=config.RUN_TIMEOUT)
    except subprocess.TimeoutExpired:
        status="wall_timeout"
    except KeyboardInterrupt:
        status="interrupted"
    finally:
        if status:
            process.kill()
            process.wait()
            record=json.loads(metadata.read_text(encoding="utf-8")) if metadata.exists() else {"run_id":run_id}
            record["status_before_stop"]=record.get("status")
            record.update(status=status,seconds_total=round(time.perf_counter()-started,3))
            metadata.parent.mkdir(exist_ok=True)
            metadata.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
            print("STOP:",status,". Partial files preserved; do not treat as a completed run.")
    return 2

def main():
    import os
    os.chdir(Path(__file__).resolve().parent)
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("which",choices=[*CONFIGS,"all"])
    p.add_argument("repeats",type=int)
    p.add_argument("series")
    a=p.parse_args()
    if not 1<=a.repeats<=3: p.error("repeats must be 1..3")
    run_id_for(a.series,"none",1)
    names=list(CONFIGS) if a.which=="all" else [a.which]
    if a.series.startswith("cache") and (a.which!="none" or a.repeats!=1):
        p.error("Use none 1 cache1, then none 1 cache2")
    # Precheck every output before starting a multi-run series.
    for repeat in range(1,a.repeats+1):
        for name in names:
            rid=run_id_for(a.series,name,repeat)
            if any((Path(d)/(rid+ext)).exists() for d,ext in [("results",".json"),("logs",".log"),("state",".json")]):
                p.error("Existing run: "+rid+". Choose a NEW series; no files overwritten.")
    for repeat in range(1,a.repeats+1):
        for name in names:
            code=run_one(name,repeat,a.series)
            if code: return code
    print("SERIES FINISHED. Run: python collect_results.py")
    return 0
if __name__=="__main__": raise SystemExit(main())
