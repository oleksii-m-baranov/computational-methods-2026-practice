"""Offline audit: preserves primary files and includes failed attempts."""
import csv, hashlib, json, statistics
from pathlib import Path
from logparse import parse_log
ROOT=Path(__file__).resolve().parent

def main():
    data=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'results').glob('main_*_r[123].json'))]
    assert len(data)==9
    signatures=set(); rows=[]
    for d in data:
        signatures.add(json.dumps({k:d[k] for k in ('model','num_ctx','temperature','compress_at','keep_last','state_result_chars','request_timeout','task_sha256','source_sha256')},sort_keys=True))
        assert not d['use_cache']
        for name,digest in d['source_sha256'].items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
        assert hashlib.sha256((ROOT/'long_task.json').read_bytes()).hexdigest()==d['task_sha256']
        steps=parse_log((ROOT/'logs'/f"{d['run_id']}.log").read_text(encoding='utf-8'))[0]['steps']
        known=[s for s in steps if s['tokens'] is not None]; m=d['metrics']
        assert (len(known),sum(s['tokens'] for s in known),sum(s['completion'] for s in known),sum(len(s['calls']) for s in steps))==(m['steps'],m['prompt_tokens'],m['completion_tokens'],d['tool_calls']),d['run_id']
        rows.append([d['run_id'],d['status'],len(steps),len(known),d['tool_calls'],m['prompt_tokens'],m['completion_tokens'],len(known)==len(steps),d['seconds']])
    assert len(signatures)==1
    dest=ROOT/'exports'/'review';dest.mkdir(exist_ok=True,parents=True)
    with (dest/'all_main_attempts.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['run_id','status','attempts','steps_with_usage','tool_calls','known_input','known_output','usage_complete','seconds']);w.writerows(rows)
    med=[]
    for mode in ('none','trim','trim+state'):
        part=[d for d in data if d['configuration']==mode]
        complete=all(d['status']=='final' for d in part)
        med.append({'mode':mode,'attempted_runs':len(part),'final_answers':sum(d['status']=='final' for d in part),'median_seconds':statistics.median(d['seconds'] for d in part),'median_full_input':statistics.median(d['metrics']['prompt_tokens'] for d in part) if complete else None,'median_full_output':statistics.median(d['metrics']['completion_tokens'] for d in part) if complete else None})
    (dest/'medians.json').write_text(json.dumps(med,ensure_ascii=False,indent=2),encoding='utf-8')
    print('VERIFIED: 9 attempts; matching source/task hashes and log metrics; incomplete usage marked null.')
    print('EXPORTED: exports/review/all_main_attempts.csv and medians.json')
if __name__=='__main__':main()
