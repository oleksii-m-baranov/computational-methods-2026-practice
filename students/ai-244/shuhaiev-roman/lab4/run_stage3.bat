@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d %~dp0
rem Pri porozi 2150 stysnennia ne spratsovuie (div. probe_trim), tomu osnovne vymiriuvannia - z porohom 1100
set COMPRESS_AT=1100
echo === Krok 8: osnovne vymiriuvannia (9 progoniv, ~20 khv) ===
python measure.py none,trim,trim+state 3 main > results\measure_main.txt || goto :err
for %%c in (none trim trim+state) do for %%r in (1 2 3) do python analyze.py logs\main_%%c_r%%r.log > results\analyze_main_%%c_r%%r.txt
echo === Dodatkove: summary (3 progony) ===
python measure.py summary 3 extra > results\measure_extra_summary.txt || goto :err
for %%r in (1 2 3) do python analyze.py logs\extra_summary_r%%r.log > results\analyze_extra_summary_r%%r.txt
set COMPRESS_AT=
powershell -command "Get-Content results\measure_main.txt -Tail 6; Get-Content results\measure_extra_summary.txt -Tail 4"
echo GOTOVO
goto :eof
:err
echo POMYLKA - nadishli tekst vyshche.
exit /b 1
