$psb = "$PSScriptRoot\FreeMote\PsbDecompile.exe"
$src = "$PSScriptRoot\extracted"

if (!(Test-Path $src)) { Write-Error "Extracted directory not found"; exit 1 }

Get-ChildItem -Path $src -Filter "*.scn" | ForEach-Object {
    Write-Host "Decompiling $($_.Name)..."
    & $psb $_.FullName
}
