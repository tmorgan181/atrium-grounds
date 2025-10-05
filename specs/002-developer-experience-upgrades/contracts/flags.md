# PowerShell Parameter Contracts

**Feature**: 002-developer-experience-upgrades
**File**: `services/observatory/quick-start.ps1`
**Type**: CLI Parameter Definitions

---

## Existing Parameters (Preserved)

### Action Parameter
```powershell
[Parameter(Position = 0)]
[ValidateSet('test', 'serve', 'demo', 'health', 'analyze', 'keys', 'setup', 'clean', 'validate', 'help')]
[string]$Action = 'help'
```

**Contract**:
- **Type**: String (positional parameter 0)
- **Default**: `'help'`
- **Valid Values**: Enum of 10 actions
- **Behavior**: Determines which function to execute
- **Backward Compatibility**: All existing values preserved

---

### Port Parameter
```powershell
[Parameter()]
[int]$Port = 8000
```

**Contract**:
- **Type**: Integer
- **Default**: `8000`
- **Valid Range**: 1-65535 (standard TCP port range)
- **Behavior**: Server listen port for `serve` and `validate` actions
- **Backward Compatibility**: Unchanged

---

### Detail Parameter (EXISTING - Enhanced)
```powershell
[Parameter()]
[switch]$Detail
```

**Contract**:
- **Type**: Switch (boolean flag)
- **Default**: `$false`
- **Current Behavior**: Already exists in script, minimally used
- **Enhanced Behavior**:
  - Controls all `Write-Step` output (23 instances)
  - Controls external tool output verbosity
  - Controls pytest verbosity (`-v` vs `-q`)
- **Backward Compatibility**: Existing usage preserved, scope expanded

---

### NewWindow Parameter
```powershell
[Parameter()]
[switch]$NewWindow
```

**Contract**:
- **Type**: Switch (boolean flag)
- **Default**: `$false`
- **Behavior**: Start server in new PowerShell window (serve action only)
- **Backward Compatibility**: Unchanged

---

## New Parameters (Added by Feature 002)

### Clean Parameter
```powershell
[Parameter()]
[switch]$Clean
```

**Contract**:
- **Type**: Switch (boolean flag)
- **Default**: `$false`
- **Purpose**: Enable clean logging (no ANSI escape codes)
- **Applicable Actions**: `serve`, `validate`
- **Behavior**:
  - When `$true`: Use `run_clean_server.py` instead of `uvicorn` directly
  - When `$false`: Standard uvicorn with ANSI colors
- **Integration**: Leverages existing Copilot clean logging implementation
- **Platform Notes**: Works on all platforms, primarily for Windows PowerShell compatibility

**Validation**:
- ✅ Valid with `serve` action
- ✅ Valid with `validate` action (affects background server)
- ⚠️ Ignored with other actions (info message shown)
- ✅ Combines with `-Detail` flag (both apply)
- ✅ Combines with `-NewWindow` flag

---

### Unit Parameter
```powershell
[Parameter()]
[switch]$Unit
```

**Contract**:
- **Type**: Switch (boolean flag)
- **Default**: `$false`
- **Purpose**: Run only unit tests
- **Applicable Actions**: `test`
- **Behavior**:
  - When `$true`: `pytest tests/unit/` only
  - When `$false` (and no other test type): Run all tests
- **Test Path**: `tests/unit/` (must exist)

**Validation**:
- ✅ Valid with `test` action
- ⚠️ Ignored with other actions
- ✅ Combines with `-Coverage` flag
- ✅ Combines with `-Detail` flag
- ✅ Combines with `-Contract` and/or `-Integration` (runs all specified types)

---

### Contract Parameter
```powershell
[Parameter()]
[switch]$Contract
```

**Contract**:
- **Type**: Switch (boolean flag)
- **Default**: `$false`
- **Purpose**: Run only contract tests
- **Applicable Actions**: `test`
- **Behavior**:
  - When `$true`: `pytest tests/contract/` only
  - When `$false` (and no other test type): Run all tests
- **Test Path**: `tests/contract/` (must exist)

**Validation**:
- ✅ Valid with `test` action
- ⚠️ Ignored with other actions
- ✅ Combines with `-Coverage` flag
- ✅ Combines with `-Detail` flag
- ✅ Combines with `-Unit` and/or `-Integration`

---

### Integration Parameter
```powershell
[Parameter()]
[switch]$Integration
```

**Contract**:
- **Type**: Switch (boolean flag)
- **Default**: `$false`
- **Purpose**: Run only integration tests
- **Applicable Actions**: `test`
- **Behavior**:
  - When `$true`: `pytest tests/integration/` only
  - When `$false` (and no other test type): Run all tests
- **Test Path**: `tests/integration/` (must exist)

**Validation**:
- ✅ Valid with `test` action
- ⚠️ Ignored with other actions
- ✅ Combines with `-Coverage` flag
- ✅ Combines with `-Detail` flag
- ✅ Combines with `-Unit` and/or `-Contract`

---

### Coverage Parameter
```powershell
[Parameter()]
[switch]$Coverage
```

**Contract**:
- **Type**: Switch (boolean flag)
- **Default**: `$false`
- **Purpose**: Generate coverage report
- **Applicable Actions**: `test`
- **Behavior**:
  - When `$true`: Add `--cov=app --cov-report=term-missing` to pytest
  - When `$false`: No coverage analysis
- **Output**: Terminal coverage report with missing line numbers

**Validation**:
- ✅ Valid with `test` action
- ⚠️ Ignored with other actions
- ✅ Combines with any test type filter (`-Unit`, `-Contract`, `-Integration`)
- ✅ Combines with `-Detail` flag

---

## Parameter Combination Rules

### Test Type Filters (`-Unit`, `-Contract`, `-Integration`)
```powershell
# Logic:
if (-not ($Unit -or $Contract -or $Integration)) {
    # No filters = run all tests
    $testPaths = @("tests/unit/", "tests/contract/", "tests/integration/")
} else {
    # Build array of specified test types
    $testPaths = @()
    if ($Unit) { $testPaths += "tests/unit/" }
    if ($Contract) { $testPaths += "tests/contract/" }
    if ($Integration) { $testPaths += "tests/integration/" }
}
```

**Examples**:
- `.\quick-start.ps1 test` → All tests
- `.\quick-start.ps1 test -Unit` → Unit tests only
- `.\quick-start.ps1 test -Unit -Contract` → Unit + Contract tests
- `.\quick-start.ps1 test -Unit -Contract -Integration` → All tests (explicit)

---

### Verbosity Control (`-Detail`)
```powershell
# Affects:
# 1. Write-Step output (shown only if $Detail)
# 2. External tool output (suppressed unless $Detail)
# 3. Pytest verbosity
$pytestArgs = if ($Detail) { @("-v", "--tb=short") } else { @("-q", "--tb=line") }
```

**Examples**:
- `.\quick-start.ps1 setup` → Minimal output
- `.\quick-start.ps1 setup -Detail` → Full diagnostic output
- `.\quick-start.ps1 test -Unit -Detail` → Verbose unit test output

---

### Clean Logging (`-Clean`)
```powershell
# Affects serve command:
if ($Clean) {
    # Use clean logging script
    $serverCmd = "run_clean_server.py"
} else {
    # Use standard uvicorn
    $serverCmd = "uvicorn app.main:app"
}
```

**Examples**:
- `.\quick-start.ps1 serve` → Standard uvicorn with colors
- `.\quick-start.ps1 serve -Clean` → Clean logging (no ANSI codes)
- `.\quick-start.ps1 serve -Clean -NewWindow` → Clean logs in new window

---

### Coverage + Test Types
```powershell
# Coverage applies to selected test types
if ($Coverage) {
    $pytestArgs += @("--cov=app", "--cov-report=term-missing")
}

# Examples:
# -Unit -Coverage          → Coverage for unit tests only
# -Integration -Coverage   → Coverage for integration tests only
# -Coverage (no filters)   → Coverage for all tests
```

---

## Validation & Error Handling

### Action-Specific Parameter Validation
```powershell
# Clean flag only meaningful for serve/validate
if ($Clean -and $Action -notin @('serve', 'validate')) {
    Write-Info "-Clean flag only applies to 'serve' and 'validate' actions (ignored)"
}

# Test filters only for test action
if (($Unit -or $Contract -or $Integration -or $Coverage) -and $Action -ne 'test') {
    Write-Info "Test-related flags only apply to 'test' action (ignored)"
}
```

### Missing Prerequisites
```powershell
# If -Clean used but run_clean_server.py missing
if ($Clean -and -not (Test-Path "run_clean_server.py")) {
    Write-Warning "Clean logging script not found, using standard uvicorn"
    $Clean = $false
}
```

### Flag Conflict Resolution
```powershell
# Currently no conflicting flags, but pattern for future:
# if ($Detail -and $Quiet) {  # If -Quiet added later
#     Write-Warning "Both -Detail and -Quiet specified. Using -Detail (most verbose wins)"
#     $Quiet = $false
# }
```

---

## Help Text Updates

### New Usage Examples
```powershell
.EXAMPLE
    .\quick-start.ps1 test -Unit -Coverage
    Run unit tests with coverage report

.EXAMPLE
    .\quick-start.ps1 serve -Clean -NewWindow
    Start server with clean logging in new window

.EXAMPLE
    .\quick-start.ps1 setup -Detail
    Run setup with detailed diagnostic output

.EXAMPLE
    .\quick-start.ps1 test -Contract -Integration -Detail
    Run contract and integration tests with verbose output
```

---

## Implementation Checklist

### Phase 1: Parameter Definitions
- [ ] Add `-Clean` switch parameter
- [ ] Add `-Unit` switch parameter
- [ ] Add `-Contract` switch parameter
- [ ] Add `-Integration` switch parameter
- [ ] Add `-Coverage` switch parameter
- [ ] Update help text with new examples

### Phase 2: Validation Logic
- [ ] Add action-specific parameter validation
- [ ] Add prerequisite checks (file existence)
- [ ] Add informative warnings for ignored flags
- [ ] Test all parameter combinations

### Phase 3: Backward Compatibility
- [ ] Verify existing commands work unchanged
- [ ] Verify `-Detail` enhancement doesn't break existing usage
- [ ] Test with PowerShell 5.1 and 7+

---

**Contract Status**: ✅ DEFINED - Ready for implementation
