@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d %~dp0
echo === Zberihaiemo prohin na vikni 4096 ===
if exist logs\probe_none_r1.log if not exist logs\probe4k_none_r1.log move logs\probe_none_r1.log logs\probe4k_none_r1.log
if exist results\analyze_probe_none.txt if not exist results\analyze_probe4k_none.txt move results\analyze_probe_none.txt results\analyze_probe4k_none.txt
if exist results\measure_probe_none.txt if not exist results\measure_probe4k_none.txt move results\measure_probe_none.txt results\measure_probe4k_none.txt
echo === Vypadok C: vikno 3072 ===
ollama create qwen25-3k -f Modelfile || goto :err
ollama show qwen25-3k > results\ollama_show_qwen25-3k.txt
python measure.py none 1 probe > results\measure_probe_none.txt || goto :err
python analyze.py logs\probe_none_r1.log steps > results\analyze_probe_none.txt
type results\analyze_probe_none.txt
echo === Krok 5-6: trim i trim+state (COMPRESS_AT=2150) ===
python measure.py trim 1 probe > results\measure_probe_trim.txt || goto :err
python analyze.py logs\probe_trim_r1.log steps > results\analyze_probe_trim.txt
python measure.py trim+state 1 probe > results\measure_probe_trim+state.txt || goto :err
python analyze.py logs\probe_trim+state_r1.log steps > results\analyze_probe_trim+state.txt
echo === Te same z nyzhchym porohom COMPRESS_AT=1100 ===
set COMPRESS_AT=1100
python measure.py trim 1 probelow > results\measure_probelow_trim.txt || goto :err
python analyze.py logs\probelow_trim_r1.log steps > results\analyze_probelow_trim.txt
python measure.py trim+state 1 probelow > results\measure_probelow_trim+state.txt || goto :err
python analyze.py logs\probelow_trim+state_r1.log steps > results\analyze_probelow_trim+state.txt
set COMPRESS_AT=
echo === Krok 7: kesh ===
if exist cache rmdir /S /Q cache
python measure.py none 1 cache1 > results\measure_cache1.txt || goto :err
python analyze.py logs\cache1_none_r1.log > results\analyze_cache1.txt
python measure.py none 1 cache2 > results\measure_cache2.txt || goto :err
python analyze.py logs\cache2_none_r1.log > results\analyze_cache2.txt
type results\measure_cache1.txt results\measure_cache2.txt
echo GOTOVO
goto :eof
:err
echo POMYLKA - nadishli tekst vyshche.
exit /b 1
