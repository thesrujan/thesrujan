$ErrorActionPreference = "Stop"
$uri = "http://127.0.0.1:5001/api/products/1001/availability?work_ms=20"

1..150 | ForEach-Object {
    Invoke-RestMethod -Uri $uri -Method Get -TimeoutSec 10 | Out-Null
}

Write-Host "Completed 150 product availability requests against $uri"
