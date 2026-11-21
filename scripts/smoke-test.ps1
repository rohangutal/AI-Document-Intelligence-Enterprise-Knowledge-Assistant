param(
    [string]$ApiUrl = 'http://localhost:8000',
    [string]$FrontendUrl = 'http://localhost:8080'
)

$ErrorActionPreference = 'Stop'

function Assert-HttpOk([string]$Url) {
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing
    if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 300) {
        throw "Expected a 2xx response from $Url, received $($response.StatusCode)."
    }
    Write-Output "PASS $Url [$($response.StatusCode)]"
}

Assert-HttpOk "$ApiUrl/api/v1/health"
Assert-HttpOk "$ApiUrl/docs"
Assert-HttpOk $FrontendUrl

try {
    $ready = Invoke-WebRequest -Uri "$ApiUrl/api/v1/health/ready" -UseBasicParsing
    if ($ready.StatusCode -ne 200) { throw "Readiness returned $($ready.StatusCode)." }
    Write-Output "PASS $ApiUrl/api/v1/health/ready [200]"
} catch {
    throw "Readiness check failed. Confirm PostgreSQL and Redis are running. $($_.Exception.Message)"
}

Write-Output 'Smoke test completed successfully.'
