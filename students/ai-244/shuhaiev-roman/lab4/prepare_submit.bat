@echo off
chcp 65001 >nul
cd /d %~dp0
echo === Prybyraiemo tymchasovi fajly ===
if exist cache rmdir /S /Q cache
if exist __pycache__ rmdir /S /Q __pycache__
echo === Perevirka: chy ye skrinshoty ===
if exist screenshots\main_none_r1.png (echo OK main_none_r1.png) else (echo NEMAIE screenshots\main_none_r1.png)
if exist screenshots\main_trim_state_r1.png (echo OK main_trim_state_r1.png) else (echo NEMAIE screenshots\main_trim_state_r1.png)
echo GOTOVO
