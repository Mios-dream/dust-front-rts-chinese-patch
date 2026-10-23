param(
    [Parameter(Mandatory = $true)]
    [string]$GamePath,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$resource = Join-Path $GamePath "Dust Front RTS_Data\resources.assets"
$replacement = Join-Path $PSScriptRoot "Dust Front RTS_Data\resources.assets"
$manifestPath = Join-Path $PSScriptRoot "manifest.json"

if (-not (Test-Path -LiteralPath $resource -PathType Leaf)) {
    throw "Game resource not found: $resource"
}
if (-not (Test-Path -LiteralPath $replacement -PathType Leaf)) {
    throw "Patch resource not found: $replacement"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$currentHash = (Get-FileHash -LiteralPath $resource -Algorithm SHA256).Hash.ToLowerInvariant()
$expectedHash = $manifest.source_sha256.ToLowerInvariant()
if (-not $Force -and $currentHash -ne $expectedHash) {
    throw "The Steam resource version does not match this patch. Use -Force only after making a backup."
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = "$resource.bak.$stamp"
Copy-Item -LiteralPath $resource -Destination $backup
Copy-Item -LiteralPath $replacement -Destination $resource -Force

$patchedHash = (Get-FileHash -LiteralPath $resource -Algorithm SHA256).Hash.ToLowerInvariant()
if ($patchedHash -ne $manifest.patched_sha256.ToLowerInvariant()) {
    Copy-Item -LiteralPath $backup -Destination $resource -Force
    throw "Patched resource checksum verification failed; the original file was restored."
}

Write-Host "Chinese translation patch installed."
Write-Host "Backup: $backup"
