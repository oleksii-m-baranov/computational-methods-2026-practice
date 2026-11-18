@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d %~dp0
rem Kroky, dlia yakykh rezultat uzhe ye, propuskaiutsia.
if not exist results\task1_reasoning.json (python reasoning.py || goto :err)
if not exist results\task2_system.json (python hello.py || goto :err)
if not exist results\task3_compare.json (python compare.py || goto :err)
if not exist results.csv (python benchmark.py || goto :err)
if not exist results\task4_cold_warm.json (python benchmark.py --cold || goto :err)
if not exist speed.png (python plot.py || goto :err)
if not exist quality.json (python quality.py || goto :err)
python check_json.py || goto :err
if not exist results\task6_sampling.json (python sampling.py || goto :err)
echo.
echo GOTOVO
goto :eof
:err
echo POMYLKA na poperednomu kroci - nadishli tekst vyshche.
exit /b 1
