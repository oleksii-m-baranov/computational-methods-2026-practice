@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d %~dp0
python check.py || goto :err
python agent_runner.py || goto :err
echo GOTOVO
goto :eof
:err
echo POMYLKA - nadishli tekst vyshche.
exit /b 1
