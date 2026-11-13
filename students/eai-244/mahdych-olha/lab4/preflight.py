"""Діагностика Ollama окремо від експериментів. Без сторонніх бібліотек."""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from datetime import datetime

ROOT=Path(__file__).resolve().parent

def request(path,payload=None):
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    data=None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request("http://127.0.0.1:11434"+path,data=data,headers={"Content-Type":"application/json"})
    with opener.open(req,timeout=65) as response: return json.load(response)

def child():
    import config
    started=time.perf_counter()
    version=request("/api/version")
    # Той самий OpenAI-compatible маршрут, який використовує агент.
    reply=request("/v1/chat/completions",dict(model=config.MODEL,
        messages=[dict(role="user",content="Reply only OK")],temperature=0,max_tokens=8))
    text=reply["choices"][0]["message"].get("content")
    if not text: raise RuntimeError("Empty reply")
    return dict(ok=True,version=version,model=config.MODEL,answer=text,
                seconds=round(time.perf_counter()-started,3),purpose="diagnostic_only")

if __name__=="__main__":
    os.chdir(ROOT)
    if "--worker" in sys.argv:
        try: print(json.dumps(child(),ensure_ascii=False))
        except Exception as e:
            print(json.dumps(dict(ok=False,error=type(e).__name__,purpose="diagnostic_only")))
            raise SystemExit(1)
    else:
        folder=Path("diagnostics");folder.mkdir(exist_ok=True)
        filename=folder/(datetime.now().strftime("preflight_%Y%m%d_%H%M%S_%f")+".txt")
        proc=subprocess.Popen([sys.executable,"-u",__file__,"--worker"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",errors="replace")
        try:
            output,_=proc.communicate(timeout=75)
            code=proc.returncode
        except subprocess.TimeoutExpired:
            proc.kill();output,_=proc.communicate()
            output += "\nHARD TIMEOUT: 75 seconds. Model/server requires diagnosis.\n"
            code=2
        filename.write_text(output,encoding="utf-8")
        print(output)
        print("Saved:",filename)
        print("READY FOR NEXT CHECK" if code==0 else "STOP. Do not start experiments. Send this diagnostic file.")
        raise SystemExit(code)
