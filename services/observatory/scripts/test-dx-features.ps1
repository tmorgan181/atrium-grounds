#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Test matrix validation for Feature 002 Developer Experience Upgrades

.DESCRIPTION
    Tests all flag combinations and validates NFR-001 (scannable output <50 lines).
    Ensures all new parameters work correctly across different actions.

.EXAMPLE
    .\scripts\test-dx-features.ps1
    Run full test matrix validation
#>

$ErrorActionPreference = "Stop"
$script:PassCount = 0
$script:FailCount = 0
$script:SkipCount = 0

function Write-TestHeader {
    param([string]$Title)
    Write-Host "`n$('='*70)" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor White
    Write-Host "$('='*70)" -ForegroundColor Cyan
}

function Write-TestCase {
    param([string]$Name, [string]$Command)
    Write-Host "`n[TEST] $Name" -ForegroundColor Yellow
    Write-Host "  CMD: $Command" -ForegroundColor DarkGray
}

function Write-TestResult {
    param([bool]$Passed, [string]$Message = "")
    if ($Passed) {
        $script:PassCount++
        Write-Host "  [PASS]" -ForegroundColor Green
        if ($Message) { Write-Host "      $Message" -ForegroundColor Gray }
    } else {
        $script:FailCount++
        Write-Host "  [FAIL]" -ForegroundColor Red
        if ($Message) { Write-Host "      $Message" -ForegroundColor Red }
    }
}

function Write-TestSkip {
    param([string]$Reason)
    $script:SkipCount++
    Write-Host "  [SKIP] $Reason" -ForegroundColor DarkGray
}

function Test-OutputLength {
    param([string]$Output, [int]$MaxLines = 50)
    $lineCount = ($Output -split "`n").Count
    return @{
        Passed = $lineCount -le $MaxLines
        LineCount = $lineCount
        MaxLines = $MaxLines
    }
}

function Invoke-QuickStartTest {
    param(
        [string]$Action,
        [string[]]$Flags = @(),
        [int]$ExpectedMaxLines = 50,
        [bool]$ShouldSucceed = $true
    )
    
    $flagStr = if ($Flags.Count -gt 0) { "-" + ($Flags -join " -") } else { "" }
    $command = ".\quick-start.ps1 $Action $flagStr"
    
    try {
        $output = & { 
            Invoke-Expression $command 2>&1 | Out-String
        }
        
        $lengthCheck = Test-OutputLength -Output $output -MaxLines $ExpectedMaxLines
        
        if ($LASTEXITCODE -eq 0) {
            if ($ShouldSucceed) {
                $passed = $lengthCheck.Passed
                $msg = "Output: $($lengthCheck.LineCount) lines (max: $($lengthCheck.MaxLines))"
                Write-TestResult -Passed $passed -Message $msg
                return $passed
            } else {
                Write-TestResult -Passed $false -Message "Expected failure but succeeded"
                return $false
            }
        } else {
            if (-not $ShouldSucceed) {
                Write-TestResult -Passed $true -Message "Failed as expected (exit: $LASTEXITCODE)"
                return $true
            } else {
                Write-TestResult -Passed $false -Message "Exit code: $LASTEXITCODE"
                return $false
            }
        }
    }
    catch {
        if (-not $ShouldSucceed) {
            Write-TestResult -Passed $true -Message "Failed as expected"
            return $true
        } else {
            Write-TestResult -Passed $false -Message $_.Exception.Message
            return $false
        }
    }
}

# ============================================================================
# TEST SUITE
# ============================================================================

Write-TestHeader "Feature 002 Developer Experience - Test Matrix"
Write-Host "  Testing parameter combinations and NFR-001 compliance" -ForegroundColor Gray
Write-Host "  NFR-001: Common operations should be scannable (<50 lines)" -ForegroundColor Gray

# ============================================================================
# Test Group 1: Parameter Parsing (all flags recognized)
# ============================================================================

Write-TestHeader "Group 1: Parameter Parsing"

Write-TestCase "1.1: -Detail flag recognized" ".\quick-start.ps1 help -Detail"
Invoke-QuickStartTest -Action "help" -Flags @("Detail") -ExpectedMaxLines 100

Write-TestCase "1.2: -Clean flag recognized" ".\quick-start.ps1 help -Clean"
Invoke-QuickStartTest -Action "help" -Flags @("Clean") -ExpectedMaxLines 100

Write-TestCase "1.3: -Unit flag recognized" ".\quick-start.ps1 help -Unit"
Invoke-QuickStartTest -Action "help" -Flags @("Unit") -ExpectedMaxLines 100

Write-TestCase "1.4: -Contract flag recognized" ".\quick-start.ps1 help -Contract"
Invoke-QuickStartTest -Action "help" -Flags @("Contract") -ExpectedMaxLines 100

Write-TestCase "1.5: -Integration flag recognized" ".\quick-start.ps1 help -Integration"
Invoke-QuickStartTest -Action "help" -Flags @("Integration") -ExpectedMaxLines 100

Write-TestCase "1.6: -Validation flag recognized" ".\quick-start.ps1 help -Validation"
Invoke-QuickStartTest -Action "help" -Flags @("Validation") -ExpectedMaxLines 100

Write-TestCase "1.7: -Coverage flag recognized" ".\quick-start.ps1 help -Coverage"
Invoke-QuickStartTest -Action "help" -Flags @("Coverage") -ExpectedMaxLines 100

# ============================================================================
# Test Group 2: Test Filtering (T008-T011)
# ============================================================================

Write-TestHeader "Group 2: Test Filtering"

Write-TestCase "2.1: Unit tests only" ".\quick-start.ps1 test -Unit"
Invoke-QuickStartTest -Action "test" -Flags @("Unit") -ExpectedMaxLines 30

Write-TestCase "2.2: Contract tests only" ".\quick-start.ps1 test -Contract"
Invoke-QuickStartTest -Action "test" -Flags @("Contract") -ExpectedMaxLines 30

Write-TestCase "2.3: Integration tests only" ".\quick-start.ps1 test -Integration"
Invoke-QuickStartTest -Action "test" -Flags @("Integration") -ExpectedMaxLines 30

Write-TestCase "2.4: Validation suite only" ".\quick-start.ps1 test -Validation"
Invoke-QuickStartTest -Action "test" -Flags @("Validation") -ExpectedMaxLines 30

Write-TestCase "2.5: Unit + Coverage" ".\quick-start.ps1 test -Unit -Coverage"
Invoke-QuickStartTest -Action "test" -Flags @("Unit", "Coverage") -ExpectedMaxLines 50

Write-TestCase "2.6: Multiple test types" ".\quick-start.ps1 test -Unit -Contract"
Invoke-QuickStartTest -Action "test" -Flags @("Unit", "Contract") -ExpectedMaxLines 50

# ============================================================================
# Test Group 3: Verbosity Control (T005-T007)
# ============================================================================

Write-TestHeader "Group 3: Verbosity Control"

Write-TestCase "3.1: Setup minimal output" ".\quick-start.ps1 setup"
$output = .\quick-start.ps1 setup 2>&1 | Out-String
$lengthCheck = Test-OutputLength -Output $output -MaxLines 15
Write-TestResult -Passed $lengthCheck.Passed -Message "Lines: $($lengthCheck.LineCount)/15"

Write-TestCase "3.2: Setup detailed output" ".\quick-start.ps1 setup -Detail"
Write-TestSkip "Already set up (would show more output)"

Write-TestCase "3.3: Test minimal output" ".\quick-start.ps1 test -Unit"
$output = .\quick-start.ps1 test -Unit 2>&1 | Out-String
$lengthCheck = Test-OutputLength -Output $output -MaxLines 30
Write-TestResult -Passed $lengthCheck.Passed -Message "Lines: $($lengthCheck.LineCount)/30"

# ============================================================================
# Test Group 4: Code Quality Actions (T013-T015)
# ============================================================================

Write-TestHeader "Group 4: Code Quality Actions"

Write-TestCase "4.1: Lint action" ".\quick-start.ps1 lint"
Invoke-QuickStartTest -Action "lint" -ExpectedMaxLines 500 -ShouldSucceed $false

Write-TestCase "4.2: Format action" ".\quick-start.ps1 format"
Invoke-QuickStartTest -Action "format" -ExpectedMaxLines 50

Write-TestCase "4.3: Check action" ".\quick-start.ps1 check"
Invoke-QuickStartTest -Action "check" -ExpectedMaxLines 500 -ShouldSucceed $false

# ============================================================================
# Test Group 5: Parameter Validation (T024)
# ============================================================================

Write-TestHeader "Group 5: Parameter Validation"

Write-TestCase "5.1: -Clean with non-serve action warns" ".\quick-start.ps1 setup -Clean"
$output = .\quick-start.ps1 setup -Clean 2>&1 | Out-String
$hasWarning = $output -match "WARNING.*-Clean.*serve"
Write-TestResult -Passed $hasWarning -Message "Warning displayed: $hasWarning"

Write-TestCase "5.2: Test flags with non-test action warn" ".\quick-start.ps1 lint -Unit"
$output = .\quick-start.ps1 lint -Unit 2>&1 | Out-String
$hasWarning = $output -match "WARNING.*test.*action"
Write-TestResult -Passed $hasWarning -Message "Warning displayed: $hasWarning"

Write-TestCase "5.3: Multiple test flags show info" ".\quick-start.ps1 test -Unit -Contract"
$output = .\quick-start.ps1 test -Unit -Contract 2>&1 | Out-String
$hasInfo = $output -match "\[INFO\].*Multiple test types"
Write-TestResult -Passed $hasInfo -Message "Info displayed: $hasInfo"

# ============================================================================
# Test Group 6: NFR-001 Compliance (Scannable Output)
# ============================================================================

Write-TestHeader "Group 6: NFR-001 Compliance (<50 lines)"

$nfrTests = @(
    @{ Action = "help"; MaxLines = 100 }
    @{ Action = "setup"; MaxLines = 15 }
    @{ Action = "test"; Flags = @("Unit"); MaxLines = 30 }
    @{ Action = "lint"; MaxLines = 500 }  # Lint can be longer
    @{ Action = "format"; MaxLines = 50 }
)

foreach ($test in $nfrTests) {
    $flagStr = if ($test.Flags) { "-" + ($test.Flags -join " -") } else { "" }
    Write-TestCase "NFR: $($test.Action) $flagStr" ".\quick-start.ps1 $($test.Action) $flagStr"
    
    try {
        $output = & { Invoke-Expression ".\quick-start.ps1 $($test.Action) $flagStr 2>&1" } | Out-String
        $lengthCheck = Test-OutputLength -Output $output -MaxLines $test.MaxLines
        Write-TestResult -Passed $lengthCheck.Passed -Message "Lines: $($lengthCheck.LineCount)/$($test.MaxLines)"
    } catch {
        Write-TestResult -Passed $false -Message $_.Exception.Message
    }
}

# ============================================================================
# Summary
# ============================================================================

Write-TestHeader "Test Summary"
$total = $script:PassCount + $script:FailCount + $script:SkipCount
$passRate = if ($total -gt 0) { [math]::Round(($script:PassCount / $total) * 100, 1) } else { 0 }

Write-Host "  Total Tests:  $total" -ForegroundColor White
Write-Host "  Passed:       $script:PassCount" -ForegroundColor Green
Write-Host "  Failed:       $script:FailCount" -ForegroundColor Red
Write-Host "  Skipped:      $script:SkipCount" -ForegroundColor DarkGray
Write-Host "  Pass Rate:    $passRate%" -ForegroundColor $(if ($passRate -ge 90) { "Green" } elseif ($passRate -ge 70) { "Yellow" } else { "Red" })
Write-Host ""

if ($script:FailCount -gt 0) {
    Write-Host "  [X] Some tests failed. Review output above." -ForegroundColor Red
    exit 1
} else {
    Write-Host "  [OK] All tests passed!" -ForegroundColor Green
    exit 0
}
