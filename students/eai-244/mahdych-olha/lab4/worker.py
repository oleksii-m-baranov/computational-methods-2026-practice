"""Один реальний прогін; запускається measure.py в окремому процесі."""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone


def main():
    os.chdir(Path(__file__).resolve().parent)
    p = argparse.ArgumentParser()
    p.add_argument("name", choices=["none","trim","trim+state"])
    p.add_argument("repeat", type=int)
    p.add_argument("series")
    p.add_argument("--short", type=int)
    a = p.parse_args()
    import config
    from measure import CONFIGS, is_correct, run_id_for
    run_id = run_id_for(a.series,a.name,a.repeat,a.short)
    for directory in ["logs","state","results"]:
        Path(directory).mkdir(exist_ok=True)
    metadata = Path("results") / (run_id+".json")
    if (Path("logs")/(run_id+".log")).exists() or (Path("state")/(run_id+".json")).exists():
        raise SystemExit("STOP: existing run files: " + run_id)
    record = dict(run_id=run_id,configuration=a.name,series=a.series,status="running",
                  started_at=datetime.now(timezone.utc).isoformat(),answer=None)
    with metadata.open("x",encoding="utf-8") as f:
        json.dump(record,f,ensure_ascii=False,indent=2)
    def save():
        temporary = metadata.with_suffix(".tmp")
        temporary.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
        temporary.replace(metadata)
    started=time.perf_counter()
    client=None
    failed=False
    try:
        for key,value in CONFIGS[a.name].items(): setattr(config,key,value)
        config.USE_CACHE=a.series.startswith("cache")
        from langfuse import get_client, propagate_attributes
        from agent import run_agent
        from logparse import parse_log
        from metrics import describe
        client=get_client()
        task_file=Path("long_task.json") if a.short is None else Path("tasks.json")
        task=json.loads(task_file.read_text(encoding="utf-8"))
        if a.short is not None: task=task[a.short]
        record.update(model=config.MODEL,num_ctx=config.NUM_CTX,temperature=config.TEMPERATURE,
                      compress_at=config.COMPRESS_AT,keep_last=config.KEEP_LAST,
                      state_result_chars=config.STATE_RESULT_CHARS,use_cache=config.USE_CACHE,
                      request_timeout=config.REQUEST_TIMEOUT,cache_namespace=config.CACHE_NAMESPACE,
                      task_sha256=hashlib.sha256(task_file.read_bytes()).hexdigest(),
                      source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in sorted(Path('.').glob('*.py'))})
        from importlib.metadata import version
        record["python_version"]=sys.version
        record["packages"]={name:version(name) for name in ["openai","pydantic","langfuse","python-dotenv"]}
        save()
        with propagate_attributes(trace_name="long-"+run_id,tags=[a.series,a.name]):
            answer=run_agent(task["question"],max_steps=config.MAX_STEPS_LONG if a.short is None else config.MAX_STEPS,
                             logfile_name=run_id,task_id=run_id,log_overwrite=False)
        record["seconds"]=round(time.perf_counter()-started,3)
        record["answer"]=answer
        runs=parse_log((Path("logs")/(run_id+".log")).read_text(encoding="utf-8"))
        if not runs: raise ValueError("No parseable run in log")
        metrics=describe(runs[-1])
        record["status"]=metrics["status"]
        record["metrics"]=metrics
        record["tool_calls"]=sum(len(s["calls"]) for s in runs[-1]["steps"])
        record["min_calls"]=task.get("min_calls")
        record["expected"]=task.get("expected")
        record["expected_number_present"]=is_correct(answer,task.get("expected","")) if a.short is None else None
        record["manual_correct"]=None
        failed=record["status"]=="server_error"
    except BaseException as error:
        record.update(status="interrupted" if isinstance(error,KeyboardInterrupt) else "execution_error",
                      error=type(error).__name__,seconds=round(time.perf_counter()-started,3))
        failed=True
        print("RUN ERROR:",type(error).__name__,flush=True)
    finally:
        save()
        if client is not None:
            client.flush()
    print("RUN SAVED:",run_id,record["status"],flush=True)
    return 2 if failed else 0

if __name__=="__main__":
    raise SystemExit(main())
