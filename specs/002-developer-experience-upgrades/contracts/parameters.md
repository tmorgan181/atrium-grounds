# Parameter Contracts

**Feature**: Developer Experience Upgrades
**File**: `services/observatory/quick-start.ps1`
**Date**: 2025-10-04

---

## Global Parameters

These parameters are added to the script-level `param()` block and accessible to all functions.

### -Detail

**Type**: `[switch]`
**Default**: `$false`
**Scope**: All actions
**Purpose**: Enable verbose output showing step-by-step progress and full external tool output

**Contract**:
```powershell
[Parameter()]
[switch]$Detail
```

**Behavior**:
- When `$false` (default): Minimal output, suppress external command output
- When `$true`: Full diagnostic output, show all steps and external command output
- Affects: `Write-Step` visibility, pytest verbosity, external command output

**Usage Examples**:
```powershell
.\quick-start.ps1 setup           # Minimal output
.\quick-start.ps1 setup -Detail   # Verbose output
.\quick-start.ps1 test -Detail    # Verbose test output
```

**Test Cases**:
- TC-001: Default (no flag) produces minimal output
- TC-002: `-Detail` flag shows `Write-Step` messages
- TC-003: `-Detail` shows full pytest output (`-v`)
- TC-004: `-Detail` shows uv/pip installation output
- TC-005: Errors always shown regardless of `-Detail`

---

### -Clean

**Type**: `[switch]`
**Default**: `$false`
**Scope**: `serve` action only
**Purpose**: Use clean logging formatter without ANSI escape codes (Windows-friendly)

**Contract**:
```powershell
[Parameter()]
[switch]$Clean
```

**Behavior**:
- When `$false` (default): Standard uvicorn logging with ANSI codes
- When `$true`: Use `run_clean_server.py` for ANSI-free logging
- Validates `run_clean_server.py` exists before use
- Falls back to standard mode with warning if file missing

**Usage Examples**:
```powershell
.\quick-start.ps1 serve           # Standard ANSI logging
.\quick-start.ps1 serve -Clean    # Clean logging (no ANSI)
.\quick-start.ps1 serve -Clean -NewWindow  # Clean logs in new window
```

**Test Cases**:
- TC-006: Default uses standard uvicorn
- TC-007: `-Clean` uses `run_clean_server.py`
- TC-008: `-Clean` falls back gracefully if file missing
- TC-009: `-Clean` works with `-NewWindow`
- TC-010: `-Clean` with non-serve action shows info message

---

### -Unit

**Type**: `[switch]`
**Default**: `$false`
**Scope**: `test` action only
**Purpose**: Run only unit tests

**Contract**:
```powershell
[Parameter()]
[switch]$Unit
```

**Behavior**:
- When `$true`: Run `pytest tests/unit/` only
- When `$false`: Run all tests (if no other test flags provided)
- Can combine with `-Coverage` flag

**Usage Examples**:
```powershell
.\quick-start.ps1 test -Unit              # Unit tests only
.\quick-start.ps1 test -Unit -Detail      # Unit tests, verbose
.\quick-start.ps1 test -Unit -Coverage    # Unit tests with coverage
```

**Test Cases**:
- TC-011: `-Unit` runs only tests/unit/ directory
- TC-012: `-Unit` exit code reflects test results
- TC-013: `-Unit -Coverage` generates coverage report
- TC-014: `-Unit -Detail` shows verbose pytest output

---

### -Contract

**Type**: `[switch]`
**Default**: `$false`
**Scope**: `test` action only
**Purpose**: Run only contract tests

**Contract**:
```powershell
[Parameter()]
[switch]$Contract
```

**Behavior**:
- When `$true`: Run `pytest tests/contract/` only
- When `$false`: Run all tests (if no other test flags provided)
- Can combine with `-Coverage` flag

**Usage Examples**:
```powershell
.\quick-start.ps1 test -Contract           # Contract tests only
.\quick-start.ps1 test -Contract -Detail   # Contract tests, verbose
```

**Test Cases**:
- TC-015: `-Contract` runs only tests/contract/ directory
- TC-016: `-Contract` exit code reflects test results
- TC-017: `-Contract -Coverage` generates coverage report

---

### -Integration

**Type**: `[switch]`
**Default**: `$false`
**Scope**: `test` action only
**Purpose**: Run only integration tests

**Contract**:
```powershell
[Parameter()]
[switch]$Integration
```

**Behavior**:
- When `$true`: Run `pytest tests/integration/` only
- When `$false`: Run all tests (if no other test flags provided)
- Can combine with `-Coverage` flag

**Usage Examples**:
```powershell
.\quick-start.ps1 test -Integration        # Integration tests only
.\quick-start.ps1 test -Integration -Detail # Integration tests, verbose
```

**Test Cases**:
- TC-018: `-Integration` runs only tests/integration/ directory
- TC-019: `-Integration` exit code reflects test results
- TC-020: `-Integration -Coverage` generates coverage report

---

### -Validation

**Type**: `[switch]`
**Default**: `$false`
**Scope**: `test` action only
**Purpose**: Run validation suite (PowerShell endpoint tests)

**Contract**:
```powershell
[Parameter()]
[switch]$Validation
```

**Behavior**:
- When `$true`: Run `scripts/validation.ps1` only
- When `$false`: Run all tests (if no other test flags provided)
- Validation suite includes 27 endpoint tests across 8 phases
- Auto-manages server startup/shutdown

**Usage Examples**:
```powershell
.\quick-start.ps1 test -Validation         # Validation suite only
.\quick-start.ps1 validate                 # Deprecated alias (still works)
```

**Test Cases**:
- TC-021: `-Validation` runs only validation.ps1
- TC-022: `-Validation` auto-starts/stops server
- TC-023: `validate` action is alias to `test -Validation`
- TC-024: Deprecation notice shown for `validate` action

---

### -Coverage

**Type**: `[switch]`
**Default**: `$false`
**Scope**: `test` action only
**Purpose**: Generate coverage report for pytest tests

**Contract**:
```powershell
[Parameter()]
[switch]$Coverage
```

**Behavior**:
- When `$true`: Add `--cov=app --cov-report=term-missing` to pytest
- Can combine with test type flags (`-Unit`, `-Contract`, `-Integration`)
- Generates terminal coverage report
- Does not apply to validation suite (PowerShell tests)

**Usage Examples**:
```powershell
.\quick-start.ps1 test -Coverage           # All pytest tests with coverage
.\quick-start.ps1 test -Unit -Coverage     # Unit tests with coverage
```

**Test Cases**:
- TC-025: `-Coverage` adds coverage flags to pytest
- TC-026: Coverage report displayed in output
- TC-027: `-Coverage` with `-Validation` skips coverage for validation
- TC-028: Exit code reflects test results, not coverage threshold

---

## Parameter Interaction Rules

### Mutual Exclusivity
**None** - All parameters can be combined as long as they apply to the current action

### Conflict Resolution
```powershell
# Test type flags without any flags = all tests
if (-not ($Unit -or $Contract -or $Integration -or $Validation)) {
    # Run all test types
}

# Multiple test type flags = run those types only
if ($Unit -and $Contract) {
    # Run unit tests then contract tests
}

# Clean flag on non-serve action
if ($Clean -and $Action -ne "serve") {
    Write-Info "-Clean flag only applies to 'serve' action (ignored)"
}
```

### Validation Rules
```powershell
# FR-026: Validate flag combinations
function Test-ParameterCombinations {
    # No conflicts currently defined
    # Future: Could add -Quiet flag that conflicts with -Detail
}
```

---

## Backward Compatibility

### Existing Commands (No Changes)
```powershell
.\quick-start.ps1 setup          # Still works, now with minimal output
.\quick-start.ps1 test           # Still runs all tests (NEW: includes validation)
.\quick-start.ps1 serve          # Still uses standard uvicorn
.\quick-start.ps1 clean          # No changes
.\quick-start.ps1 health         # No changes
.\quick-start.ps1 analyze        # No changes
```

### Deprecated Commands (Aliases)
```powershell
.\quick-start.ps1 validate       # Now alias to: .\quick-start.ps1 test -Validation
                                 # Shows deprecation notice, still functional
```

---

## Default Behavior Changes

### Breaking Changes (None - But Output Changes)
- **setup** action now shows minimal output by default (previously showed all steps)
  - Migration: Add `-Detail` flag to see old behavior
  - Rationale: NFR-001 requires scannable output
- **test** action now includes validation suite (previously separate)
  - Migration: Use `-Unit` to run only unit tests
  - Rationale: FR consolidation decision from research phase

### Non-Breaking Changes
- All new flags are optional
- New actions (`lint`, `format`, `check`) don't affect existing workflows
- Clean logging is opt-in via `-Clean` flag

---

## Implementation Notes

### Parameter Declaration
Add all new parameters to existing `param()` block at top of script:

```powershell
param(
    # ... existing parameters ...

    [Parameter()]
    [switch]$Detail,     # NEW

    [Parameter()]
    [switch]$Clean,      # NEW

    [Parameter()]
    [switch]$Unit,       # NEW

    [Parameter()]
    [switch]$Contract,   # NEW

    [Parameter()]
    [switch]$Integration,  # NEW

    [Parameter()]
    [switch]$Validation,   # NEW

    [Parameter()]
    [switch]$Coverage     # NEW
)
```

### Access Pattern
All functions can access these parameters directly via script scope:

```powershell
function Invoke-Test {
    # No parameter passing needed
    if ($Detail) {
        # Use verbose mode
    }

    if ($Coverage) {
        # Add coverage flags
    }
}
```

---

**Contract Status**: ✅ Defined and testable
