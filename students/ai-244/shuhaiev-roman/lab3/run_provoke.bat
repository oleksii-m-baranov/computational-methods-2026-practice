@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d %~dp0
python agent_runner.py provoke provoke_tasks.json
