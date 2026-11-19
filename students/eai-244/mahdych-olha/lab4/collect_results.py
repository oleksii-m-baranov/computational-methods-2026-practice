"""Експорт лише наявних результатів; report.md не перезаписується."""
import csv
import json
import statistics
from pathlib import Path
from datetime import datetime
import os

if __name__=="__main__":
    os.chdir(Path(__file__).resolve().parent)
    rows=[]
    for p in sorted(Path("results").glob("*.json")):
        d=json.loads(p.read_text(encoding="utf-8"));m=d.get("metrics",{})
        rows.append(dict(run_id=d.get("run_id"),series=d.get("series"),configuration=d.get("configuration"),
                         status=d.get("status"),model=d.get("model"),num_ctx=d.get("num_ctx"),
                         seconds=d.get("seconds"),steps=m.get("steps"),tool_calls=d.get("tool_calls"),
                         prompt=m.get("prompt_tokens"),completion=m.get("completion_tokens"),
                         repeats=m.get("repeats"),squeezes=len(m.get("squeezes",[])),
                         cache_hits=m.get("cache_hits"),number_present=d.get("expected_number_present"),
                         manual_correct=d.get("manual_correct")))
    if not rows: raise SystemExit("NO RUN RESULTS. Nothing invented or exported.")
    folder=Path("exports")/datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    folder.mkdir(parents=True)
    with (folder/"runs.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    lines=["# Наявні результати", "", "Наявність числа у відповіді не доводить правильність. Потрібна ручна перевірка.", "",
           "| Прогін | Статус | Час, с | Кроків | Викликів інструментів | Вхід | Вихід | Кеш |",
           "|---|---|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        lines.append("| "+" | ".join(str(r[k]) if r[k] is not None else "—" for k in ["run_id","status","seconds","steps","tool_calls","prompt","completion","cache_hits"])+" |")
    lines += ["", "## Основна серія: медіани", "",
              "Лише завершені на рівні програми прогони main (final, retry_limit, step_limit). Транспортні збої виключено й залишено в переліку вище.", "",
              "| Режим | Прогонів | Правильно (ручна оцінка) | Кроків | Вхід | Вихід | Час, с | Стиснень | Повторів |",
              "|---|---:|---|---:|---:|---:|---:|---:|---:|"]
    all_records=[json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path("results").glob("main_*.json"))]
    comparable={(d.get("model"),d.get("num_ctx"),d.get("task_sha256"),
                 d.get("temperature"),d.get("compress_at"),d.get("keep_last"),
                 json.dumps(d.get("source_sha256",{}),sort_keys=True))
                for d in all_records if d.get("model")}
    if len(comparable)>1:
        lines += ["Параметри/джерела основних прогонів відрізняються. Медіани не об’єднано; перевірте JSON."]
    else:
        for name in ["none","trim","trim+state"]:
            part=[r for r in rows if r["series"]=="main" and r["configuration"]==name
                  and r["status"] in ["final","retry_limit","step_limit"]]
            if len(part)!=3:
                lines.append(f"| {name} | {len(part)} | Очікує 3 прогонів | — | — | — | — | — | — |")
                continue
            right=(str(sum(r["manual_correct"] is True for r in part))+" з 3"
                   if all(isinstance(r["manual_correct"],bool) for r in part) else "Потрібна ручна оцінка")
            values=[f"{statistics.median(r[k] for r in part):g}" for k in ["steps","prompt","completion","seconds","squeezes","repeats"]]
            lines.append("| "+" | ".join([name,"3",right,*values])+" |")
    (folder/"tables.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("EXPORTED:",folder)
