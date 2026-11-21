$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dockerDesktop = "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop.exe"

if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker info *> $null
}

if ($LASTEXITCODE -ne 0) {
    if (Test-Path $dockerDesktop) {
        Start-Process $dockerDesktop
    }

    $deadline = (Get-Date).AddSeconds(180)
    do {
        docker info *> $null
        if ($LASTEXITCODE -eq 0) {
            break
        }
        Start-Sleep -Seconds 5
    } while ((Get-Date) -lt $deadline)
}

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker is not running. Start Docker Desktop and run this script again."
}

Set-Location $root
docker compose -f "infra/docker-compose.yml" up -d
docker compose -f "infra/docker-compose.yml" ps

Set-Location (Join-Path $root "backend")
alembic upgrade head

$backendCommand = "Set-Location '$root\backend'; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
$frontendCommand = "Set-Location '$root\frontend'; node '$root\frontend\node_modules\vite\bin\vite.js' --host 0.0.0.0"

Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $backendCommand
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $frontendCommand

Start-Sleep -Seconds 5
Start-Process "http://localhost:5173"
