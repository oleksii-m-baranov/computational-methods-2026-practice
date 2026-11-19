"""Одна точка запуску: python run.py check|probe|trim|state|baseline|cache1|cache2|main|collect."""
import os
import subprocess
import sys
from pathlib import Path
os.chdir(Path(__file__).resolve().parent)
COMMANDS={
 "check":["preflight.py"],"selfcheck":["self_check.py"],"tracing":["check_tracing.py"],
 "probe":["measure.py","none","1","probe"],
 "trim":["measure.py","trim","1","probe"],
 "state":["measure.py","trim+state","1","probe"],
 "baseline":["agent_runner.py"],
 "cache1":["measure.py","none","1","cache1"],
 "cache2":["measure.py","none","1","cache2"],
 "main":["measure.py","all","3","main"],
 "collect":["collect_results.py"],
}
if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in COMMANDS: raise SystemExit(__doc__)
    action=sys.argv[1]
    if action=="cache1" and Path("cache").exists() and any(Path("cache").iterdir()):
        raise SystemExit("STOP: cache is not empty. Preserve/rename it before the cold-cache run.")
    if action=="cache2" and (not Path("cache").exists() or not any(Path("cache").iterdir())):
        raise SystemExit("STOP: cache is empty. Complete cache1 first.")
    try:
        timeout=45 if action=="tracing" else None
        code=subprocess.run([sys.executable,"-u",*COMMANDS[action]],timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        print("TIMEOUT: tracing check exceeded 45 seconds");code=2
    raise SystemExit(code)
