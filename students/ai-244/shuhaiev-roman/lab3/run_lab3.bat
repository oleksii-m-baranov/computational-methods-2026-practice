@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d %~dp0
if not exist .env (echo Nemaie fajlu .env z kliuchamy Langfuse & exit /b 1)
python test_checks.py || goto :err
if not exist results\baseline_stats.json (python agent_runner.py baseline || goto :err)
if not exist results\checks_stats.json (python agent_runner.py checks || goto :err)
if not exist results\structured_demo.json (python structured_demo.py || goto :err)
echo GOTOVO
goto :eof
:err
echo POMYLKA - nadishli tekst vyshche.
exit /b 1
