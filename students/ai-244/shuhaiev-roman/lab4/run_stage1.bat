@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d %~dp0
if not exist .env copy ..\lab3\.env .env
if not exist results mkdir results
echo === Krok 1: model z vuzkym viknom ===
ollama create qwen25-4k -f Modelfile || goto :err
ollama show qwen25-4k > results\ollama_show_qwen25-4k.txt
ollama show qwen2.5:3b > results\ollama_show_qwen2.5-3b.txt
type results\ollama_show_qwen25-4k.txt
echo === Krok 2: dovga zadacha ===
python make_task.py || goto :err
echo === Krok 3: perevirka agenta ===
python agent.py || goto :err
python agent_runner.py || goto :err
echo === Krok 3: prohin bez zakhystu ===
python measure.py none 1 probe > results\measure_probe_none.txt || goto :err
type results\measure_probe_none.txt
echo === Krok 4: rozbir ===
python analyze.py logs\probe_none_r1.log steps > results\analyze_probe_none.txt || goto :err
type results\analyze_probe_none.txt
echo GOTOVO
goto :eof
:err
echo POMYLKA - nadishli tekst vyshche.
exit /b 1
