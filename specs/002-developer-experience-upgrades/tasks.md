# Tasks: Developer Experience Upgrades

**Feature**: 002-developer-experience-upgrades
**Input**: Design documents from `/specs/002-developer-experience-upgrades/`
**Prerequisites**: plan.md ✅, research.md ✅, contracts/ ✅, quickstart.md ✅

---

## Execution Summary

**Total Tasks**: 28
**Parallel-Safe Tasks**: 15 (marked [P])
**Estimated Duration**: 2-3 weeks (incremental phases)
**Primary File**: `services/observatory/quick-start.ps1`

---

## Phase 3.1: Setup & Preparation

### T001: Add new parameters to param() block
**File**: `services/observatory/quick-start.ps1` (lines 10-30, param block)
**Description**: Add 6 new switch parameters: `-Clean`, `-Unit`, `-Contract`, `-Integration`, `-Validation`, `-Coverage` (Note: `-Detail` already exists, `-NewWindow` already exists)
**Contract**: `contracts/parameters.md`
**Test**: Verify PowerShell parses script without errors
**Dependencies**: None
**Parallel**: No (single file, foundational change)

```powershell
# Add to existing param() block:
[Parameter()]
[switch]$Detail,

[Parameter()]
[switch]$Clean,

[Parameter()]
[switch]$Unit,

[Parameter()]
[switch]$Contract,

[Parameter()]
[switch]$Integration,

[Parameter()]
[switch]$Validation,

[Parameter()]
[switch]$Coverage
```

---

### T002: [P] Add mypy to dev dependencies
**File**: `services/observatory/pyproject.toml` (dev dependencies section)
**Description**: Add `mypy` to development dependencies for type checking (implements research.md decision #5: "Use MyPy for type checking")
**Rationale**: Required for `check` action
**Test**: Run `uv pip install -e ".[dev]"` succeeds
**Dependencies**: None
**Parallel**: Yes (different file from T001)

```toml
[project.optional-dependencies]
dev = [
    # ... existing ...
    "mypy>=1.0",
]
```

---

## Phase 3.2: Helper Functions (Core Verbosity Control)

### T003: Create Invoke-CommandWithVerbosity helper
**File**: `services/observatory/quick-start.ps1` (after existing Write-* functions)
**Description**: Implement core helper function for conditional output redirection (implements NFR-005 <100ms overhead and NFR-006 efficient streaming via 2>&1 redirection)
**Contract**: `contracts/helper-functions.md`
**Test**: Call with test scriptblock, verify output suppression works
**Dependencies**: T001 (needs `-Detail` parameter)
**Parallel**: No (same file as T001)

```powershell
function Invoke-CommandWithVerbosity {
    <#
    .SYNOPSIS
        Execute command with output controlled by $Detail flag
    #>
    param(
        [scriptblock]$Command,
        [string]$SuccessMessage = ""
    )

    try {
        if ($Detail) {
            & $Command
        } else {
            $output = & $Command 2>&1
            if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
                Write-Host $output -ForegroundColor Red
                throw "Command failed"
            }
        }

        if ($SuccessMessage -and -not $Detail) {
            Write-Success $SuccessMessage
        }
    } catch {
        Write-Failure "$_"
        throw
    }
}
```

---

### T004: Modify Write-Step to respect -Detail flag
**File**: `services/observatory/quick-start.ps1` (Write-Step function)
**Description**: Update Write-Step to only output when $Detail is true
**Contract**: `contracts/helper-functions.md`
**Test**: Call Write-Step with/without -Detail, verify behavior
**Dependencies**: T001 (needs `-Detail` parameter)
**Parallel**: No (same file)

```powershell
# Before:
function Write-Step {
    param([string]$Message)
    Write-Host "→ $Message" -ForegroundColor Cyan
}

# After:
function Write-Step {
    param([string]$Message)
    if ($Detail) {
        Write-Host "→ $Message" -ForegroundColor Cyan
    }
}
```

---

## Phase 3.3: Apply Verbosity Control to Existing Actions

### T005: Apply verbosity to setup action (uv venv)
**File**: `services/observatory/quick-start.ps1` (Invoke-Setup function)
**Description**: Add venv existence check and conditional output for `uv venv` command
**Contract**: Based on research.md decision #8
**Test**: Run `.\quick-start.ps1 setup` (minimal), `.\quick-start.ps1 setup -Detail` (verbose)
**Dependencies**: T003 (needs helper function)
**Parallel**: No (same file)

```powershell
# In Invoke-Setup:
if (-not (Test-Path ".venv")) {
    Write-Step "Creating virtual environment..."
    if ($Detail) {
        & "$uvPath" venv
    } else {
        & "$uvPath" venv 2>&1 | Out-Null
    }
    # ... error checking ...
    Write-Success "Virtual environment created!"
} else {
    if ($Detail) {
        Write-Info "Virtual environment already exists (skipping creation)"
    }
}
```

---

### T006: Apply verbosity to setup action (dependencies)
**File**: `services/observatory/quick-start.ps1` (Invoke-Setup function)
**Description**: Suppress pip install output using `--quiet` flag when not in Detail mode
**Test**: Run setup, verify no pip output in default mode
**Dependencies**: T003 (needs helper function)
**Parallel**: No (same file)

```powershell
Write-Step "Installing dependencies..."
if ($Detail) {
    & "$venvPath\pip.exe" install -e .
} else {
    & "$venvPath\pip.exe" install -e . --quiet 2>&1 | Out-Null
}
# ... error checking ...
if (-not $Detail) {
    Write-Success "Dependencies installed!"
}
```

---

### T007: Apply verbosity to setup action (dev dependencies)
**File**: `services/observatory/quick-start.ps1` (Invoke-Setup function)
**Description**: Suppress dev dependency installation output
**Test**: Run setup -Detail, verify all output visible
**Dependencies**: T003 (needs helper function)
**Parallel**: No (same file)

```powershell
Write-Step "Installing development dependencies..."
if ($Detail) {
    & "$venvPath\pip.exe" install pytest pytest-asyncio pytest-cov ruff mypy
} else {
    & "$venvPath\pip.exe" install pytest pytest-asyncio pytest-cov ruff mypy --quiet 2>&1 | Out-Null
}
# ... error checking ...
if (-not $Detail) {
    Write-Success "Dev dependencies installed!"
}
```

---

## Phase 3.4: Test Action Enhancement

### T008: Implement test filtering logic
**File**: `services/observatory/quick-start.ps1` (Invoke-Test function)
**Description**: Add logic to handle `-Unit`, `-Contract`, `-Integration`, `-Validation` flags
**Contract**: `contracts/actions.md`, `contracts/parameters.md`
**Test**: Run each flag combination, verify correct tests execute
**Dependencies**: T001 (needs test filter parameters)
**Parallel**: No (same file)

```powershell
function Invoke-Test {
    # Determine which tests to run
    $runAll = -not ($Unit -or $Contract -or $Integration -or $Validation)

    if ($Unit -or $runAll) {
        Write-Info "Running unit tests..."
        # ... pytest unit tests ...
    }

    if ($Contract -or $runAll) {
        Write-Info "Running contract tests..."
        # ... pytest contract tests ...
    }

    if ($Integration -or $runAll) {
        Write-Info "Running integration tests..."
        # ... pytest integration tests ...
    }

    if ($Validation -or $runAll) {
        Write-Info "Running validation suite..."
        # ... validation.ps1 ...
    }
}
```

---

### T009: Implement pytest verbosity control
**File**: `services/observatory/quick-start.ps1` (Invoke-Test function)
**Description**: Use `-q` (quiet) by default, `-v` (verbose) with -Detail flag
**Contract**: Based on research.md decision #3
**Test**: Run tests with/without -Detail, verify output levels
**Dependencies**: T001, T008
**Parallel**: No (same file)

```powershell
# Define pytest arguments based on verbosity
$pytestArgs = if ($Detail) {
    @("-v", "--tb=short")
} else {
    @("-q", "--tb=line")
}

# Use in pytest invocations
& "$venvPath\python.exe" -m pytest tests/unit/ @pytestArgs
```

---

### T010: Implement coverage flag support
**File**: `services/observatory/quick-start.ps1` (Invoke-Test function)
**Description**: Add `--cov=app --cov-report=term-missing` when -Coverage flag is set
**Contract**: `contracts/parameters.md` (Coverage parameter)
**Test**: Run `test -Unit -Coverage`, verify coverage report appears
**Dependencies**: T008 (test filtering must exist first)
**Parallel**: No (same file)

```powershell
$pytestArgs = if ($Detail) { @("-v") } else { @("-q") }

if ($Coverage) {
    $pytestArgs += @("--cov=app", "--cov-report=term-missing")
}
```

---

### T011: Add deprecation warning to validate action
**File**: `services/observatory/quick-start.ps1` (Invoke-Validate function)
**Description**: Show deprecation warning and delegate to validation suite (NOT duplicating T008 - T008 adds `-Validation` flag to test action, T011 adds deprecation to standalone `validate` action for backward compatibility)
**Contract**: Based on research.md decision #2 (test/validation consolidation)
**Test**: Run `.\quick-start.ps1 validate`, verify warning shown and validation runs
**Dependencies**: T008 (test action must support -Validation)
**Parallel**: No (same file)

```powershell
function Invoke-Validate {
    Write-Warning "DEPRECATED: 'validate' action is deprecated. Use '.\quick-start.ps1 test -Validation' instead."
    Write-Info "Running validation suite..."

    # Call validation script (same as test -Validation)
    & "$PWD\scripts\validation.ps1" -BaseUrl $Script:Config.BaseUrl
}
```

---

## Phase 3.5: Clean Logging Integration

### T012: Implement -Clean flag for serve action
**File**: `services/observatory/quick-start.ps1` (Invoke-Server function)
**Description**: Use `run_clean_server.py` when -Clean flag is set
**Contract**: `contracts/parameters.md` (Clean parameter), based on research.md decision #4
**Test**: Run `serve -Clean`, verify ANSI-free output
**Dependencies**: T001 (needs -Clean parameter)
**Parallel**: No (same file)

```powershell
function Invoke-Server {
    $pythonExe = "$($Script:Config.VenvPath)\python.exe"

    # Check if clean logging files exist
    if ($Clean -and -not (Test-Path "run_clean_server.py")) {
        Write-Warning "Clean logging files not found (run_clean_server.py missing). Using standard mode."
        $Clean = $false
    }

    if ($NewWindow) {
        if ($Clean) {
            $serverScript = "cd '$PWD'; & '$pythonExe' run_clean_server.py $Port $(if($Reload){'--reload'})"
            Write-Info "Starting server with clean logging (no ANSI codes)"
        } else {
            $serverScript = "cd '$PWD'; & '$pythonExe' -m uvicorn app.main:app --host 0.0.0.0 --port $Port $(if($Reload){'--reload'})"
        }

        Start-Process $pwsh -ArgumentList "-NoExit", "-Command", $serverScript
        Write-Success "Server starting in new $pwsh window"
    } else {
        # Foreground mode
        if ($Clean) {
            Write-Info "Using clean logging (no ANSI escape codes)"
            & $pythonExe run_clean_server.py $Port $(if($Reload){'--reload'})
        } else {
            & $pythonExe -m uvicorn app.main:app --host 0.0.0.0 --port $Port $(if($Reload){'--reload'})
        }
    }

    Write-Info "Server running at http://127.0.0.1:$Port"
}
```

---

## Phase 3.6: Code Quality Actions

### T013: [P] Implement lint action
**File**: `services/observatory/quick-start.ps1` (new Invoke-Lint function + action routing)
**Description**: Create new `lint` action that runs `ruff check .`
**Contract**: `contracts/actions.md` (lint action)
**Test**: Run `.\quick-start.ps1 lint`, verify linter executes
**Dependencies**: T002 (ruff must be installed)
**Parallel**: Yes (new function, doesn't modify existing code paths)

```powershell
function Invoke-Lint {
    Write-Info "Running code linter (ruff)..."

    $pythonExe = "$($Script:Config.VenvPath)\python.exe"

    if ($Detail) {
        & $pythonExe -m ruff check .
    } else {
        & $pythonExe -m ruff check . 2>&1 | Tee-Object -Variable ruffOutput | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host $ruffOutput
            Write-Failure "Linting found issues"
            exit 1
        }
    }

    Write-Success "No linting issues found"
}

# Add to action switch:
"lint" { Invoke-Lint }
```

---

### T014: [P] Implement format action
**File**: `services/observatory/quick-start.ps1` (new Invoke-Format function + action routing)
**Description**: Create new `format` action that runs `ruff format .`
**Contract**: `contracts/actions.md` (format action)
**Test**: Run `.\quick-start.ps1 format`, verify files are formatted
**Dependencies**: T002 (ruff must be installed)
**Parallel**: Yes (new function, independent of T013)

```powershell
function Invoke-Format {
    Write-Info "Formatting code with ruff..."

    $pythonExe = "$($Script:Config.VenvPath)\python.exe"

    if ($Detail) {
        & $pythonExe -m ruff format .
    } else {
        $output = & $pythonExe -m ruff format . 2>&1
        # Extract summary line (e.g., "12 files reformatted, 45 files left unchanged")
        $summary = $output | Select-String "files?" | Select-Object -Last 1
        if ($summary) {
            Write-Success $summary
        } else {
            Write-Success "Code formatted"
        }
    }
}

# Add to action switch:
"format" { Invoke-Format }
```

---

### T015: [P] Implement check action
**File**: `services/observatory/quick-start.ps1` (new Invoke-Check function + action routing)
**Description**: Create new `check` action that runs lint + type check
**Contract**: `contracts/actions.md` (check action)
**Test**: Run `.\quick-start.ps1 check`, verify both lint and mypy execute
**Dependencies**: T002 (mypy required), T013 (can reuse lint logic)
**Parallel**: Yes (new function, can be implemented alongside T013/T014)

```powershell
function Invoke-Check {
    Write-Info "Running code quality checks..."

    $pythonExe = "$($Script:Config.VenvPath)\python.exe"
    $allPassed = $true

    # Run linter
    Write-Info "Running linter..."
    & $pythonExe -m ruff check .
    if ($LASTEXITCODE -ne 0) {
        Write-Failure "Linting failed"
        $allPassed = $false
    } else {
        Write-Success "Linting passed"
    }

    # Run type checker
    Write-Info "Running type checker..."
    & $pythonExe -m mypy app/
    if ($LASTEXITCODE -ne 0) {
        Write-Failure "Type checking failed"
        $allPassed = $false
    } else {
        Write-Success "Type checking passed"
    }

    if ($allPassed) {
        Write-Success "All quality checks passed"
        exit 0
    } else {
        Write-Failure "Some quality checks failed"
        exit 1
    }
}

# Add to action switch:
"check" { Invoke-Check }
```

---

## Phase 3.7: Documentation & Help

### T016: Update help text with new flags
**File**: `services/observatory/quick-start.ps1` (Invoke-Help function or help text section)
**Description**: Document all new parameters and actions in help output
**Test**: Run `.\quick-start.ps1 help`, verify new flags documented
**Dependencies**: All previous tasks (all features should exist)
**Parallel**: No (depends on feature completion)

```powershell
function Show-Help {
    Write-Host @"
Observatory Quick-Start Script

USAGE:
    .\quick-start.ps1 <action> [flags]

ACTIONS:
    setup       Install dependencies and configure environment
    test        Run test suite (unit, contract, integration, validation)
    serve       Start development server
    lint        Check code quality (read-only)
    format      Auto-format code
    check       Run linting + type checking
    clean       Remove generated files
    health      Test health endpoint
    analyze     Test analysis endpoint
    keys        Generate API keys
    help        Show this help message

FLAGS:
    -Detail             Show verbose output with full diagnostics
    -Clean              Use clean logging without ANSI codes (serve only)
    -Unit               Run unit tests only (test action)
    -Contract           Run contract tests only (test action)
    -Integration        Run integration tests only (test action)
    -Validation         Run validation suite only (test action)
    -Coverage           Generate coverage report (test action)
    -NewWindow          Start server in new window (serve action)
    -Reload             Enable auto-reload (serve action)
    -Port <number>      Custom port (default: 8000)

EXAMPLES:
    .\quick-start.ps1 setup
    .\quick-start.ps1 setup -Detail
    .\quick-start.ps1 test -Unit -Coverage
    .\quick-start.ps1 serve -Clean -NewWindow
    .\quick-start.ps1 lint
    .\quick-start.ps1 check
"@
}
```

---

### T017: [P] Update WORKFLOW.md with new features
**File**: `services/observatory/WORKFLOW.md`
**Description**: Add examples of new flags and workflows
**Test**: Read file, verify examples are clear
**Dependencies**: None (documentation)
**Parallel**: Yes (different file)

Add sections:
- "Using Verbosity Control"
- "Test Filtering"
- "Code Quality Checks"
- "Clean Logging on Windows"

---

### T018: [P] Update README.md with quick examples
**File**: `services/observatory/README.md` (Quick Start section)
**Description**: Add brief examples of new capabilities
**Test**: Read file, verify examples work
**Dependencies**: None (documentation)
**Parallel**: Yes (different file from T017)

---

## Phase 3.8: Testing & Validation

### T019: Create test matrix validation script
**File**: `services/observatory/scripts/test-dx-features.ps1` (NEW FILE)
**Description**: Create PowerShell script that tests all flag combinations AND validates NFR-001 (scannable in <5 seconds = <50 lines of output for common operations)
**Test**: Run script, verify all combinations work
**Dependencies**: All implementation tasks complete
**Parallel**: No (validation task)

```powershell
# Test matrix from spec:
# - 7 parameters × 3-5 test cases each = ~30 tests
# - 5 actions × 2-3 parameter combinations = ~12 tests
# - Total: ~42 test cases

# NFR-001 Measurement: "Scannable in <5 seconds" = <50 lines of output (typical reading speed)
$maxLinesForScannable = 50

$tests = @(
    @{ Action = "setup"; Flags = @(); Expected = "Minimal output"; MaxLines = $maxLinesForScannable },
    @{ Action = "setup"; Flags = @("-Detail"); Expected = "Verbose output"; MaxLines = $null },  # No limit for Detail
    @{ Action = "test"; Flags = @("-Unit"); Expected = "Unit tests only"; MaxLines = $maxLinesForScannable },
    @{ Action = "test"; Flags = @("-Unit", "-Coverage"); Expected = "Unit with coverage"; MaxLines = $null },  # Coverage adds lines
    # ... etc
)

foreach ($test in $tests) {
    # Run test and validate output
    $output = & .\quick-start.ps1 $test.Action @($test.Flags) 2>&1
    $lineCount = ($output | Measure-Object -Line).Lines

    if ($test.MaxLines -and $lineCount -gt $test.MaxLines) {
        Write-Warning "Action '$($test.Action)' output too long: $lineCount lines (max: $($test.MaxLines))"
    }
}
```

---

### T020: Verify backward compatibility
**File**: Manual testing checklist
**Description**: Run all Feature 001 commands without flags, verify they still work
**Test Cases**:
- `.\quick-start.ps1 setup` (should work, now with minimal output)
- `.\quick-start.ps1 test` (should run all tests including validation)
- `.\quick-start.ps1 serve` (should use standard uvicorn)
- `.\quick-start.ps1 validate` (should show deprecation warning but work)
**Dependencies**: All implementation complete
**Parallel**: No (validation)

---

### T021: Test on Windows PowerShell 5.1
**File**: Manual testing
**Description**: Run test matrix on Windows PowerShell 5.1 (not just PowerShell Core)
**Rationale**: Spec targets PS 5.1+ (common in corporate environments)
**Test**: Verify output redirection, parameters, all actions work
**Dependencies**: T019, T020
**Parallel**: No (validation)

---

### T022: Performance validation (<100ms overhead)
**File**: Benchmark script or manual measurement
**Description**: Measure overhead of verbosity control
**Test**: Use `Measure-Command` to compare before/after
**Expected**: <100ms overhead per action
**Dependencies**: All implementation complete
**Parallel**: No (validation)

```powershell
# Baseline (before changes)
$before = Measure-Command { .\quick-start.ps1 test -Unit }

# After changes (minimal mode)
$after = Measure-Command { .\quick-start.ps1 test -Unit }

# Overhead
$overhead = $after - $before
# Should be < 100ms
```

---

## Phase 3.9: Polish & Finalization

### T023: Review and remove code duplication
**File**: `services/observatory/quick-start.ps1`
**Description**: Identify repeated patterns and consolidate into helper functions
**Test**: Run all actions, verify behavior unchanged
**Dependencies**: All implementation complete
**Parallel**: No (refactoring)

---

### T024: Add parameter validation (flag conflicts)
**File**: `services/observatory/quick-start.ps1` (near start of script, after param block)
**Description**: Implement FR-026 (validate flag combinations and warn about conflicts)
**Test**: Try conflicting flags, verify warnings appear
**Dependencies**: T001 (parameters must exist)
**Parallel**: No (same file)

```powershell
# Comprehensive flag conflict validation:

# Rule 1: -Clean only applies to serve action
if ($Clean -and $Action -ne "serve") {
    Write-Warning "-Clean flag only applies to 'serve' action (ignored)"
    $Clean = $false
}

# Rule 2: Test filters only apply to test action
if (($Unit -or $Contract -or $Integration -or $Validation -or $Coverage) -and $Action -ne "test") {
    Write-Warning "Test filtering flags (-Unit, -Contract, -Integration, -Validation, -Coverage) only apply to 'test' action (ignored)"
    $Unit = $false; $Contract = $false; $Integration = $false; $Validation = $false; $Coverage = $false
}

# Rule 3: Multiple test filters selected = run all selected types (not a conflict, just info)
$testFilterCount = @($Unit, $Contract, $Integration, $Validation).Where({$_}).Count
if ($testFilterCount -gt 1) {
    Write-Info "Multiple test types selected - running: $(if($Unit){'Unit '})$(if($Contract){'Contract '})$(if($Integration){'Integration '})$(if($Validation){'Validation'})"
}

# Rule 4: -NewWindow only applies to serve action
if ($NewWindow -and $Action -ne "serve") {
    Write-Warning "-NewWindow flag only applies to 'serve' action (ignored)"
    $NewWindow = $false
}

# Rule 5: -Coverage without test action
if ($Coverage -and $Action -ne "test") {
    Write-Warning "-Coverage flag only applies to 'test' action (ignored)"
    $Coverage = $false
}
```

---

### T025: [P] Update CLEAN-LOGGING.md
**File**: `services/observatory/docs/CLEAN-LOGGING.md`
**Description**: Add section about `-Clean` flag integration
**Test**: Read file, verify instructions are clear
**Dependencies**: T012 (clean logging implementation)
**Parallel**: Yes (documentation)

---

### T026: [P] Create migration guide
**File**: `services/observatory/docs/MIGRATION-002.md` (NEW FILE)
**Description**: Document changes from Feature 001 to Feature 002
**Content**:
- What changed (default output, test action behavior)
- How to get old behavior (-Detail flag)
- Deprecation notices (validate action)
**Test**: Read guide, follow instructions
**Dependencies**: None (documentation)
**Parallel**: Yes (new file)

---

### T027: Run quickstart.md validation checklist
**File**: `specs/002-developer-experience-upgrades/quickstart.md` (Validation Checklist section)
**Description**: Execute all checklist items and verify they pass
**Test**: Check off each item in quickstart.md
**Dependencies**: All implementation complete
**Parallel**: No (final validation)

---

### T028: Update Progress Tracking in plan.md
**File**: `specs/002-developer-experience-upgrades/plan.md`
**Description**: Mark Phase 4 complete, update artifact list
**Test**: Read plan.md, verify status accurate
**Dependencies**: All tasks complete
**Parallel**: No (documentation)

```markdown
- [x] Phase 4: Implementation complete ✅
- [ ] Phase 5: Validation passed (next step)

**Artifacts Generated**:
- [x] Updated quick-start.ps1 with verbosity control
- [x] New actions: lint, format, check
- [x] Updated documentation
```

---

## Dependencies

### Critical Path
```
T001 (parameters)
  → T003 (helper function)
    → T004 (Write-Step)
      → T005-T007 (apply to setup)
  → T008 (test filtering)
    → T009 (pytest verbosity)
      → T010 (coverage)
        → T011 (deprecation)
  → T012 (clean logging)
  → T013-T015 (code quality actions, can be parallel)
    → T016 (help text)
      → T019-T028 (validation & polish)
```

### Blocking Relationships
- **T001** blocks almost everything (foundational)
- **T003** blocks T005-T007 (needs helper function)
- **T008** blocks T009-T011 (test filtering must exist first)
- **All implementation** blocks validation tasks (T019-T022)
- **All features** block documentation updates (T017-T018, T025-T026)

---

## Parallel Execution Opportunities

### Phase 3.1 Setup (Parallel Group 1)
```powershell
# Can run after T001 completes:
# T002 is parallel (different file)
Task: "Add mypy to dev dependencies in pyproject.toml"
```

### Phase 3.6 Code Quality (Parallel Group 2)
```powershell
# After T002 completes, all three can run in parallel:
Task: "Implement lint action in quick-start.ps1"
Task: "Implement format action in quick-start.ps1"
Task: "Implement check action in quick-start.ps1"
```

### Phase 3.7 Documentation (Parallel Group 3)
```powershell
# Can run anytime (independent):
Task: "Update WORKFLOW.md with new features"
Task: "Update README.md with quick examples"
```

### Phase 3.9 Final Documentation (Parallel Group 4)
```powershell
# After implementation complete:
Task: "Update CLEAN-LOGGING.md with -Clean flag"
Task: "Create migration guide MIGRATION-002.md"
```

---

## Validation Checklist

### Pre-Implementation Gates
- [x] All contracts have corresponding implementation tasks
- [x] All parameters have usage in at least one task
- [x] Test verbosity control comes before applying to actions
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task

### Implementation Verification
- [ ] T001-T028 all completed
- [ ] All actions tested manually
- [ ] Test matrix executed (T019)
- [ ] Backward compatibility verified (T020)
- [ ] Windows PS 5.1 tested (T021)
- [ ] Performance overhead measured (T022)
- [ ] Documentation updated (T017-T018, T025-T026)

---

## Notes for Implementation

### Best Practices
- **Commit after each task** (especially T001-T012)
- **Test incrementally** (don't wait until T028)
- **Use `-Detail` flag** during development for debugging
- **Verify error handling** (errors should always be visible)

### Common Pitfalls
- ❌ Don't suppress error output in minimal mode
- ❌ Don't forget `$LASTEXITCODE` checks
- ❌ Don't use `-Detail` in automated scripts (use default)
- ❌ Don't skip Windows PS 5.1 testing

### Testing Strategy
- Unit test equivalent: Individual task verification
- Integration test equivalent: Test matrix (T019)
- E2E test equivalent: Backward compatibility check (T020)

---

## Estimated Effort

| Phase | Tasks | Effort | Can Parallelize? |
|-------|-------|--------|------------------|
| 3.1 Setup | T001-T002 | 1 hour | Partially (T002) |
| 3.2 Helpers | T003-T004 | 2 hours | No (same file) |
| 3.3 Apply Verbosity | T005-T007 | 3 hours | No (same file) |
| 3.4 Test Enhancement | T008-T011 | 4 hours | No (sequential) |
| 3.5 Clean Logging | T012 | 1 hour | No |
| 3.6 Code Quality | T013-T015 | 3 hours | Yes (all parallel) |
| 3.7 Help/Docs | T016-T018 | 2 hours | Partially (T017-T018) |
| 3.8 Testing | T019-T022 | 4 hours | No (validation) |
| 3.9 Polish | T023-T028 | 3 hours | Partially (docs) |
| **Total** | **28 tasks** | **23 hours** | **~30% parallelizable** |

**Realistic Timeline**: 2-3 weeks with incremental development

---

**Tasks Status**: ✅ Generated and ready for execution
**Next Step**: Begin implementation with T001 (add parameters)
