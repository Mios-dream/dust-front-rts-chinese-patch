param(
    [Parameter(Mandatory = $true)]
    [string]$GamePath
)

$ErrorActionPreference = "Stop"
$resource = Join-Path $GamePath "Dust Front RTS_Data\resources.assets"
$directory = Split-Path -Parent $resource
$backups = @(Get-ChildItem -LiteralPath $directory -Filter "resources.assets.bak.*" -File | Sort-Object LastWriteTime -Descending)

if ($backups.Count -eq 0) {
    throw "No backup was found next to $resource"
}

Copy-Item -LiteralPath $backups[0].FullName -Destination $resource -Force
Write-Host "Restored: $($backups[0].FullName)"
