# PowerShell Script Encoding Guide

**Issue**: Unicode characters in PowerShell scripts cause parse errors in Windows PowerShell 5.1

**Solution**: Use ASCII-safe alternatives and UTF-8 with BOM encoding

---

## The Problem

### Error Symptoms

```powershell
PS> .\quick-start.ps1
Unexpected token 'req/min' in expression or statement.
Missing closing ')' in expression.
Unexpected token 'â"â"â"...' in expression or statement.
```

### Root Cause

- **Windows PowerShell 5.1** defaults to Windows-1252 (ANSI) encoding
- **PowerShell Core 7+** defaults to UTF-8 encoding
- UTF-8 files WITHOUT BOM are misinterpreted by Windows PowerShell 5.1
- Unicode box-drawing characters (═, ─, │, etc.) get mangled as multi-byte sequences

### Why It Happens

1. Claude/AI tools write files with UTF-8 encoding (no BOM)
2. VSCode/Git preserve UTF-8 without BOM (standard practice)
3. Windows PowerShell 5.1 reads as ANSI, misinterpreting Unicode
4. Characters like `═` (U+2550) become `â"` or other mojibake

---

## The Solution

### Option 1: ASCII-Safe Characters (RECOMMENDED)

Replace Unicode with ASCII equivalents that work everywhere:

```powershell
# ❌ Unicode (breaks Windows PowerShell 5.1)
Write-Host "═══════════════════════" -ForegroundColor Cyan
Write-Host "─────────────────────────" -ForegroundColor Gray
Write-Host "✓ Success" -ForegroundColor Green
Write-Host "✗ Failed" -ForegroundColor Red

# ✅ ASCII-safe (works everywhere)
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "-------------------------" -ForegroundColor Gray
Write-Host "[OK] Success" -ForegroundColor Green
Write-Host "[FAIL] Failed" -ForegroundColor Red
```

### Option 2: UTF-8 with BOM

If you MUST use Unicode characters:

```powershell
# Save file with UTF-8 BOM
$content = Get-Content "script.ps1" -Raw -Encoding UTF8
$utf8BOM = New-Object System.Text.UTF8Encoding $true
$bytes = $utf8BOM.GetBytes($content)
[System.IO.File]::WriteAllBytes("script.ps1", $bytes)
```

**Downsides**:
- BOM is considered bad practice
- Can break bash/sh scripts
- Causes issues with some Git tools
- File size increases by 3 bytes

---

## Character Mapping Reference

### Box Drawing

| Unicode | Char | ASCII | Use Case |
|---------|------|-------|----------|
| U+2550  | ═    | =     | Double horizontal line |
| U+2500  | ─    | -     | Light horizontal line |
| U+2502  | │    | \|    | Vertical line |
| U+250C  | ┌    | +     | Top-left corner |
| U+2510  | ┐    | +     | Top-right corner |
| U+2514  | └    | +     | Bottom-left corner |
| U+2518  | ┘    | +     | Bottom-right corner |

### Symbols

| Unicode | Char | ASCII | Use Case |
|---------|------|-------|----------|
| U+2713  | ✓    | [OK]  | Success indicator |
| U+2717  | ✗    | [FAIL]| Failure indicator |
| U+26A0  | ⚠    | [WARN]| Warning |
| U+2139  | ℹ    | [INFO]| Information |
| U+2192  | →    | ->    | Arrow |
| U+2022  | •    | *     | Bullet point |

---

## Automated Fix

Run the provided fix script:

```powershell
cd services/observatory
.\fix-encoding-final.ps1
```

**What it does**:
1. Scans PowerShell scripts for Unicode characters
2. Replaces with ASCII equivalents
3. Saves with UTF-8 BOM for Windows PowerShell 5.1 compatibility
4. Validates all Unicode is removed

---

## Prevention Guidelines

### For AI Agents/Humans Writing PowerShell

1. **Avoid Unicode decorations** - Use `=`, `-`, `|`, `+` instead of box-drawing
2. **Use text labels** - `[OK]` instead of `✓`
3. **Test in Windows PowerShell 5.1** - Not just PowerShell Core
4. **Use ASCII art** - If you need visuals, use ASCII

### Good Patterns

```powershell
# Headers
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Script Title" -ForegroundColor White
Write-Host "=============================================" -ForegroundColor Cyan

# Sections
Write-Host "---------------------------------------------" -ForegroundColor Gray

# Status indicators
Write-Host "[OK]   Test passed" -ForegroundColor Green
Write-Host "[FAIL] Test failed" -ForegroundColor Red
Write-Host "[WARN] Check configuration" -ForegroundColor Yellow
Write-Host "[INFO] Starting process..." -ForegroundColor Cyan

# Lists
Write-Host "* Item 1" -ForegroundColor White
Write-Host "* Item 2" -ForegroundColor White

# Progress
Write-Host "Step 1 -> Step 2 -> Step 3" -ForegroundColor Cyan
```

---

## Testing for Compatibility

### Quick Test Script

```powershell
# test-encoding.ps1
$script = "your-script.ps1"

Write-Host "Testing: $script" -ForegroundColor Cyan

# Check for Unicode
$content = Get-Content $script -Raw -Encoding UTF8
$pattern = "[─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬✓✗⚠ℹ→•]"
$hasUnicode = $content -match $pattern

if ($hasUnicode) {
    Write-Host "[WARN] Contains Unicode characters" -ForegroundColor Yellow
    Select-String -Path $script -Pattern $pattern | Select-Object -First 5
} else {
    Write-Host "[OK] ASCII-safe" -ForegroundColor Green
}

# Check BOM
$bytes = [System.IO.File]::ReadAllBytes($script) | Select-Object -First 3
if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    Write-Host "[OK] Has UTF-8 BOM (Windows PowerShell compatible)" -ForegroundColor Green
} else {
    Write-Host "[INFO] No BOM (PowerShell Core only)" -ForegroundColor Cyan
}
```

### Test in Both Environments

```powershell
# Test in PowerShell Core 7+
pwsh -Command ".\your-script.ps1 help"

# Test in Windows PowerShell 5.1 (if available)
powershell -Command ".\your-script.ps1 help"
```

---

## Python Script Encoding

Python 3 defaults to UTF-8, so no issues with Unicode. However:

### Best Practice

```python
# ✅ Always specify encoding explicitly for file operations
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# ✅ Add encoding declaration for special characters in source
# -*- coding: utf-8 -*-

# ✅ Or use Python 3.8+ format (PEP 263)
# coding: utf-8
```

### Windows Compatibility

```python
import sys
import locale

# Check system encoding
print(f"System encoding: {sys.getdefaultencoding()}")
print(f"Filesystem encoding: {sys.getfilesystemencoding()}")
print(f"Locale encoding: {locale.getpreferredencoding()}")

# Force UTF-8 for stdout (Windows PowerShell fix)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
```

---

## Git Configuration

### .gitattributes (Recommended)

Add to repository root to enforce consistent line endings and text handling:

```gitattributes
# Auto detect text files and normalize line endings
* text=auto

# PowerShell scripts
*.ps1 text eol=crlf

# Python scripts
*.py text eol=lf

# Markdown, configs
*.md text eol=lf
*.json text eol=lf
*.yml text eol=lf
*.yaml text eol=lf

# Binaries
*.db binary
*.sqlite binary
*.png binary
*.jpg binary
```

### .editorconfig

```editorconfig
root = true

[*]
charset = utf-8
insert_final_newline = true
trim_trailing_whitespace = true

[*.ps1]
end_of_line = crlf
indent_style = space
indent_size = 4

[*.py]
end_of_line = lf
indent_style = space
indent_size = 4

[*.{yml,yaml,json}]
end_of_line = lf
indent_style = space
indent_size = 2
```

---

## CI/CD Considerations

### GitHub Actions

```yaml
# Ensure Windows runners use PowerShell Core by default
- name: Run tests
  shell: pwsh  # Use PowerShell Core (cross-platform)
  run: |
    cd services/observatory
    .\quick-start.ps1 test

# Or test in Windows PowerShell 5.1 specifically
- name: Test compatibility
  shell: powershell  # Use Windows PowerShell 5.1
  run: |
    cd services/observatory
    .\quick-start.ps1 help
```

---

## Summary

✅ **Use ASCII-safe characters** (= instead of ═, - instead of ─)  
✅ **Save PowerShell scripts with UTF-8 BOM** if using Unicode  
✅ **Test in Windows PowerShell 5.1** before committing  
✅ **Add .gitattributes** for consistent encoding  
✅ **Use fix-encoding-final.ps1** to clean existing scripts  

❌ **Don't use fancy Unicode** without UTF-8 BOM  
❌ **Don't assume UTF-8 without BOM** works everywhere  
❌ **Don't test only in PowerShell Core** - validate Windows PowerShell 5.1  

---

## References

- [PowerShell Encoding Documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding)
- [UTF-8 BOM Debate](https://stackoverflow.com/questions/2223882/whats-the-difference-between-utf-8-and-utf-8-without-bom)
- [PowerShell Best Practices](https://github.com/PoshCode/PowerShellPracticeAndStyle)
- [PEP 263: Defining Python Source Code Encodings](https://peps.python.org/pep-0263/)

---

**Last Updated**: 2025-01-04  
**Status**: Resolved - All scripts ASCII-safe with UTF-8 BOM
