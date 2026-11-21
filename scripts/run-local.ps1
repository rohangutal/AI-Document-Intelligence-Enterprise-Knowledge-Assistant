$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root 'backend'
$frontend = Join-Path $root 'frontend'
$compose = Join-Path $root 'infra\docker-compose.yml'

Set-Location -LiteralPath $root

if (-not (Test-Path (Join-Path $backend '.env'))) {
    Copy-Item (Join-Path $backend '.env.example') (Join-Path $backend '.env')
    Write-Output 'Created backend/.env from backend/.env.example. Set JWT_SECRET before using authentication.'
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker Desktop is required. Install and start Docker Desktop, then run this script again.'
}

docker compose -f $compose up -d
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL and Redis could not be started.' }

Set-Location -LiteralPath $backend
if (-not (Get-Command alembic -ErrorAction SilentlyContinue)) {
    Write-Output 'Alembic is not installed in the active Python environment. Run: pip install -e ".[dev]"'
    throw 'Backend dependencies are missing.'
}
alembic upgrade head

if (-not (Test-Path (Join-Path $frontend 'node_modules'))) {
    Set-Location -LiteralPath $frontend
    npm install
    if ($LASTEXITCODE -ne 0) { throw 'Frontend dependencies could not be installed.' }
    Set-Location -LiteralPath $backend
}

$backendCommand = "Set-Location -LiteralPath '$backend'; `$env:CORS_ORIGINS='http://localhost:5173'; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
$frontendCommand = "Set-Location -LiteralPath '$frontend'; node '.\node_modules\vite\bin\vite.js' --host 0.0.0.0"
Start-Process powershell.exe -ArgumentList '-NoExit', '-Command', $backendCommand
Start-Process powershell.exe -ArgumentList '-NoExit', '-Command', $frontendCommand

Start-Sleep -Seconds 3
Start-Process 'http://localhost:5173'
Write-Output 'Local project started: http://localhost:5173'
