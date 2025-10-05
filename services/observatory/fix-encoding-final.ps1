# Final encoding fix for PowerShell scripts
# Replaces Unicode characters with ASCII equivalents for Windows PowerShell 5.1 compatibility

Write-Host "`n=== Encoding Fix Script ===" -ForegroundColor Cyan
Write-Host "Fixing Unicode characters in PowerShell scripts for Windows PowerShell 5.1 compatibility`n" -ForegroundColor Gray

$files = @(
    "quick-start.ps1",
    "scripts\validation.ps1"
)

foreach ($filePath in $files) {
    if (-not (Test-Path $filePath)) {
        Write-Host "[SKIP] $filePath - File not found" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "Processing: $filePath" -ForegroundColor Cyan
    
    # Read file as bytes then decode as UTF-8
    $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $filePath).Path)
    
    # Remove BOM if present
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        Write-Host "  - Removing UTF-8 BOM" -ForegroundColor Gray
        $bytes = $bytes[3..($bytes.Length-1)]
    }
    
    $content = [System.Text.Encoding]::UTF8.GetString($bytes)
    $originalLength = $content.Length
    
    # Count Unicode characters before replacement
    $unicodeCount = 0
    $replacements = @{
        "═" = "="     # U+2550 Box Drawings Double Horizontal
        "─" = "-"     # U+2500 Box Drawings Light Horizontal
        "│" = "|"     # U+2502 Box Drawings Light Vertical
        "┌" = "+"     # U+250C Box Drawings Light Down And Right
        "┐" = "+"     # U+2510 Box Drawings Light Down And Left
        "└" = "+"     # U+2514 Box Drawings Light Up And Right
        "┘" = "+"     # U+2518 Box Drawings Light Up And Left
        "├" = "+"     # U+251C Box Drawings Light Vertical And Right
        "┤" = "+"     # U+2524 Box Drawings Light Vertical And Left
        "┬" = "+"     # U+252C Box Drawings Light Down And Horizontal
        "┴" = "+"     # U+2534 Box Drawings Light Up And Horizontal
        "┼" = "+"     # U+253C Box Drawings Light Vertical And Horizontal
        "║" = "|"     # U+2551 Box Drawings Double Vertical
        "╔" = "+"     # U+2554 Box Drawings Double Down And Right
        "╗" = "+"     # U+2557 Box Drawings Double Down And Left
        "╚" = "+"     # U+255A Box Drawings Double Up And Right
        "╝" = "+"     # U+255D Box Drawings Double Up And Left
        "╠" = "+"     # U+2560 Box Drawings Double Vertical And Right
        "╣" = "+"     # U+2563 Box Drawings Double Vertical And Left
        "╦" = "+"     # U+2566 Box Drawings Double Down And Horizontal
        "╩" = "+"     # U+2569 Box Drawings Double Up And Horizontal
        "╬" = "+"     # U+256C Box Drawings Double Vertical And Horizontal
        "•" = "*"     # U+2022 Bullet
        "→" = "->"    # U+2192 Rightwards Arrow
        "✓" = "[OK]"  # U+2713 Check Mark
        "✗" = "[FAIL]" # U+2717 Ballot X
        "⚠" = "[WARN]" # U+26A0 Warning Sign
        "ℹ" = "[INFO]" # U+2139 Information Source
    }
    
    # Apply replacements
    $modified = $content
    foreach ($unicode in $replacements.Keys) {
        $count = ([regex]::Matches($modified, [regex]::Escape($unicode))).Count
        if ($count -gt 0) {
            $modified = $modified -replace [regex]::Escape($unicode), $replacements[$unicode]
            $unicodeCount += $count
            Write-Host "  - Replaced $count × '$unicode' -> '$($replacements[$unicode])'" -ForegroundColor Gray
        }
    }
    
    if ($modified -ne $content) {
        # Save as UTF-8 WITH BOM (required for Windows PowerShell 5.1 to detect UTF-8)
        $utf8WithBOM = New-Object System.Text.UTF8Encoding $true
        $outputBytes = $utf8WithBOM.GetBytes($modified)
        [System.IO.File]::WriteAllBytes((Resolve-Path $filePath).Path, $outputBytes)
        
        $savings = $originalLength - $modified.Length
        Write-Host "  [OK] Saved with UTF-8 BOM ($unicodeCount chars replaced, $savings byte reduction)" -ForegroundColor Green
    } else {
        Write-Host "  [SKIP] No Unicode characters found" -ForegroundColor Gray
    }
}

Write-Host "`n=== Validation ===" -ForegroundColor Cyan

# Verify changes
foreach ($filePath in $files) {
    if (Test-Path $filePath) {
        $check = Get-Content $filePath -Raw -Encoding UTF8
        $hasUnicode = $check -match "[─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬✓✗⚠ℹ→•]"
        
        if ($hasUnicode) {
            Write-Host "[FAIL] $filePath still contains Unicode" -ForegroundColor Red
        } else {
            Write-Host "[PASS] $filePath is ASCII-safe" -ForegroundColor Green
        }
    }
}

Write-Host "`nFiles should now work in both Windows PowerShell 5.1 and PowerShell Core 7+`n" -ForegroundColor Cyan
