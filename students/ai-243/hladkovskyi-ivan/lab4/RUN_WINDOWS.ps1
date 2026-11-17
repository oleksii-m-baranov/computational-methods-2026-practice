# Лабораторна робота №4, варіант 7 — запуски на власному ПК (Windows PowerShell).
# Усі виміряні значення беруться лише з локального Ollama.
# Перед запуском: інсталюйте Ollama, завантажте qwen2.5:3b та задайте Langfuse ключі у .env.
param([switch]$WithSummary)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force -Path 'logs' | Out-Null

function Do-Python([string[]]$Arguments) {
    Write-Host ('>>> python ' + ($Arguments -join ' ')) -ForegroundColor Cyan
    & python @Arguments
    if ($LASTEXITCODE -ne 0) { throw ('Python завершився з кодом ' + $LASTEXITCODE) }
}

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    throw 'Команда ollama не знайдена. Інсталюйте Ollama з офіційного сайту та перезапустіть PowerShell.'
}
Do-Python -Arguments @('-m','pip','install','-r','requirements.txt')
Do-Python -Arguments @('make_task.py')
Do-Python -Arguments @('verify_local.py')
& ollama list
& ollama create qwen25-4k -f Modelfile
if ($LASTEXITCODE -ne 0) { throw 'Не вдалося створити модель qwen25-4k' }
& ollama show qwen2.5:3b | Tee-Object -FilePath 'logs/ollama_original.txt'
& ollama show qwen25-4k | Tee-Object -FilePath 'logs/ollama_4k.txt'
Write-Host 'Крок 3–4: перевірка без захисту' -ForegroundColor Green
Do-Python -Arguments @('measure.py','none','1','probe')
Do-Python -Arguments @('analyze.py','logs/probe_none_r1.log','steps')
Write-Host 'ВАЖЛИВО: Перевірте випадок A/B/C/D. Для C за методичкою потрібно зменшити num_ctx до 3072.' -ForegroundColor Yellow
$answer = Read-Host 'Випадок C? Зупинити зараз для переходу на 3072? [y/N]'
if ($answer -match '^[yYтТ]$') {
    Write-Host 'Змініть Modelfile на 3072, створіть qwen25-3k, config.MODEL/NUM_CTX/COMPRESS_AT = qwen25-3k/3072/2150; потім повторіть.' -ForegroundColor Yellow
    exit 0
}
Write-Host 'Крок 5–6: trim і trim+state' -ForegroundColor Green
Do-Python -Arguments @('measure.py','trim','1','probe')
Do-Python -Arguments @('measure.py','trim+state','1','probe')
Do-Python -Arguments @('analyze.py','logs/probe_trim_r1.log')
Do-Python -Arguments @('analyze.py','logs/probe_trim+state_r1.log')
Write-Host 'Крок 7: два запуски з кешем' -ForegroundColor Green
if (Test-Path 'cache') { Remove-Item 'cache' -Recurse -Force }
Do-Python -Arguments @('measure.py','none','1','cache1')
Do-Python -Arguments @('measure.py','none','1','cache2')
Write-Host 'Крок 8: дев’ять вимірювань без кешу' -ForegroundColor Green
Do-Python -Arguments @('measure.py','all','3','main')
if ($WithSummary) {
    Write-Host 'Додаткове завдання: summary (три прогони)' -ForegroundColor Green
    Do-Python -Arguments @('measure.py','summary','3','extra')
}
Do-Python -Arguments @('build_results.py')
Write-Host 'Готово. Див. results_from_logs.md, logs/results_*.json і траси Langfuse.' -ForegroundColor Green
