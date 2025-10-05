# Action Signatures Contract

**Feature**: 002-developer-experience-upgrades
**File**: `services/observatory/quick-start.ps1`
**Type**: PowerShell Function Contracts

---

## Existing Actions (Enhanced)

### Invoke-Setup
```powershell
function Invoke-Setup {
    # No parameters (uses script-scoped $Detail)
}
```

**Contract**:
- **Purpose**: Create virtual environment and install dependencies
- **Preconditions**:
  - Python 3.11+ installed
  - uv package manager available
- **Behavior**:
  - Default: Minimal output, show only results
  - With `-Detail`: Show step-by-step progress and full tool output
- **Postconditions**:
  - `.venv/` directory exists with Python environment
  - All dependencies installed (from setup.py)
  - Dev dependencies installed (pytest, ruff, etc.)
- **Exit Code**: 0 on success, 1 on failure
- **Output**:
  - Default: `[OK]` messages for each major step
  - Detail: Full uv/pip output plus `→` progress messages

**Enhancements (FR-001, FR-002, FR-003)**:
- Suppress external tool output unless `-Detail` flag set
- Add venv existence check (prevent error on re-run)
- Success messages shown in default mode

---

### Invoke-Test
```powershell
function Invoke-Test {
    # No parameters (uses script-scoped $Detail, $Unit, $Contract, $Integration, $Coverage)
}
```

**Contract**:
- **Purpose**: Run test suite with optional filtering and coverage
- **Preconditions**:
  - Virtual environment exists
  - pytest installed
  - Test directories exist
- **Behavior**:
  - Default: Run all tests with quiet pytest output
  - With `-Detail`: Verbose pytest output with test names
  - With `-Unit`: Run only `tests/unit/`
  - With `-Contract`: Run only `tests/contract/`
  - With `-Integration`: Run only `tests/integration/`
  - With `-Coverage`: Add coverage analysis to selected tests
- **Test Path Selection**:
  ```powershell
  if (-not ($Unit -or $Contract -or $Integration)) {
      $paths = @("tests/unit/", "tests/contract/", "tests/integration/")
  } else {
      $paths = @()
      if ($Unit) { $paths += "tests/unit/" }
      if ($Contract) { $paths += "tests/contract/" }
      if ($Integration) { $paths += "tests/integration/" }
  }
  ```
- **Pytest Arguments**:
  ```powershell
  $args = if ($Detail) { @("-v", "--tb=short") } else { @("-q", "--tb=line") }
  if ($Coverage) { $args += @("--cov=app", "--cov-report=term-missing") }
  ```
- **Postconditions**: All tests pass (exit 0) or failures reported (exit 1)
- **Exit Code**: pytest's exit code (0 = success, 1+ = failures)
- **Output**:
  - Default: Summary line (e.g., "94 passed in 2.31s")
  - Detail: Full pytest session with test names

**Enhancements (FR-011 to FR-016)**:
- Test type filtering via flags
- Coverage report generation
- Verbosity control (quiet vs verbose pytest)

---

### Invoke-Server
```powershell
function Invoke-Server {
    # No parameters (uses script-scoped $Port, $NewWindow, $Clean)
}
```

**Contract**:
- **Purpose**: Start FastAPI development server
- **Preconditions**:
  - Virtual environment exists
  - uvicorn installed
  - app.main:app module available
- **Behavior**:
  - Default: Start uvicorn with ANSI colors
  - With `-Clean`: Use `run_clean_server.py` (no ANSI codes)
  - With `-NewWindow`: Start in new PowerShell window
  - With `-Reload`: Enable auto-reload (existing flag)
- **Server Command Selection**:
  ```powershell
  $pythonExe = ".venv\Scripts\python.exe"
  if ($Clean) {
      $cmd = "& $pythonExe run_clean_server.py $Port"
  } else {
      $cmd = "& $pythonExe -m uvicorn app.main:app --host 0.0.0.0 --port $Port"
  }
  ```
- **Postconditions**: Server running on specified port
- **Exit Code**: N/A (server runs until stopped)
- **Output**:
  - Always: Server URL and docs URL
  - Default: Uvicorn startup with colors
  - With `-Clean`: Timestamped logs without ANSI codes

**Enhancements (FR-006 to FR-010)**:
- Clean logging mode via `-Clean` flag
- Integration with existing `run_clean_server.py`
- Graceful fallback if clean logging unavailable

---

### Invoke-Validate
```powershell
function Invoke-Validate {
    # No parameters (uses script-scoped $Detail, $Clean)
}
```

**Contract**:
- **Purpose**: Run full validation (start server, run tests, stop server)
- **Preconditions**:
  - Setup complete
  - Tests exist
  - Port available
- **Behavior**:
  - Start server in background (with `-Clean` if specified)
  - Wait for health endpoint
  - Run full test suite
  - Stop server
- **Server Handling**:
  ```powershell
  if ($Clean) {
      $serverProc = Start-Process python -Args "run_clean_server.py $Port" -PassThru
  } else {
      $serverProc = Start-Process python -Args "-m uvicorn app.main:app --port $Port" -PassThru
  }
  # ... health check loop ...
  Stop-Process -Id $serverProc.Id
  ```
- **Postconditions**: Server stopped, validation results reported
- **Exit Code**: 0 if all tests pass, 1 otherwise
- **Output**:
  - Default: High-level progress, test results
  - Detail: Step-by-step server management, verbose tests

**Enhancements**:
- Respect `-Clean` flag for background server
- Respect `-Detail` flag for diagnostic output

---

## New Actions (Added by Feature 002)

### Invoke-Lint
```powershell
function Invoke-Lint {
    # No parameters (uses script-scoped $Detail)
}
```

**Contract**:
- **Purpose**: Check code quality without modifying files
- **Preconditions**:
  - Virtual environment exists
  - ruff installed
- **Command**:
  ```powershell
  & ".venv\Scripts\python.exe" -m ruff check .
  ```
- **Behavior**:
  - Read-only check (no file modifications)
  - Report violations with file paths and line numbers
  - Exit with ruff's exit code
- **Postconditions**: No files modified
- **Exit Code**:
  - 0 = No violations
  - 1+ = Violations found
- **Output**:
  - Default: Violation list
  - Detail: Same (ruff is already verbose)

**New Requirements (FR-017, FR-020)**:
- Safe read-only checking
- Clear violation reporting

---

### Invoke-Format
```powershell
function Invoke-Format {
    # No parameters (uses script-scoped $Detail)
}
```

**Contract**:
- **Purpose**: Auto-format code using project standards
- **Preconditions**:
  - Virtual environment exists
  - ruff installed
  - pyproject.toml configuration exists
- **Command**:
  ```powershell
  & ".venv\Scripts\python.exe" -m ruff format .
  ```
- **Behavior**:
  - Format all Python files in project
  - Preserve semantic meaning (formatting only)
  - Report modified files
- **Postconditions**: Code formatted according to ruff rules
- **Exit Code**: 0 on success
- **Output**:
  - Default: List of reformatted files
  - Detail: Same (ruff format is already informative)

**New Requirements (FR-018, FR-021)**:
- Explicit formatting action
- No semantic changes (formatting only)

---

### Invoke-Check
```powershell
function Invoke-Check {
    # No parameters (uses script-scoped $Detail)
}
```

**Contract**:
- **Purpose**: Run comprehensive quality checks (lint + type check)
- **Preconditions**:
  - Virtual environment exists
  - ruff and mypy installed
- **Commands**:
  ```powershell
  & ".venv\Scripts\python.exe" -m ruff check .
  if ($LASTEXITCODE -eq 0) {
      & ".venv\Scripts\python.exe" -m mypy app/
  }
  ```
- **Behavior**:
  - Run ruff linting
  - If lint passes, run mypy type checking
  - Short-circuit on first failure
- **Postconditions**: Code quality verified (or violations reported)
- **Exit Code**:
  - 0 = All checks pass
  - 1+ = Failures found
- **Output**:
  - Ruff violations (if any)
  - Mypy type errors (if any)

**New Requirements (FR-019)**:
- Combined lint + type check
- Appropriate exit codes for CI/CD

---

## Action Registration

### Updated ValidateSet
```powershell
[Parameter(Position = 0)]
[ValidateSet(
    'test',      # EXISTING
    'serve',     # EXISTING
    'demo',      # EXISTING
    'health',    # EXISTING
    'analyze',   # EXISTING
    'keys',      # EXISTING
    'setup',     # EXISTING
    'clean',     # EXISTING
    'validate',  # EXISTING
    'lint',      # NEW - FR-017
    'format',    # NEW - FR-018
    'check',     # NEW - FR-019
    'help'       # EXISTING
)]
[string]$Action = 'help'
```

---

## Main Switch Statement

```powershell
switch ($Action) {
    'setup'    { Invoke-Setup }
    'test'     { Invoke-Test }
    'serve'    { Invoke-Server }
    'validate' { Invoke-Validate }
    'lint'     { Invoke-Lint }      # NEW
    'format'   { Invoke-Format }    # NEW
    'check'    { Invoke-Check }     # NEW
    'demo'     { Invoke-Demo }
    'health'   { Invoke-Health }
    'analyze'  { Invoke-Analyze }
    'keys'     { Invoke-Keys }
    'clean'    { Invoke-Clean }
    'help'     { Show-Help }
}
```

---

## Error Handling Contracts

### Dependency Check Pattern
```powershell
# Before executing action
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Error "Virtual environment not found. Run: .\quick-start.ps1 setup"
    exit 1
}

# For specific tools
if (-not (Test-Path ".venv\Scripts\ruff.exe") -and $Action -in @('lint', 'format', 'check')) {
    Write-Error "ruff not installed. Run: .\quick-start.ps1 setup"
    exit 1
}
```

### Tool Availability Check
```powershell
# For clean logging
if ($Clean -and -not (Test-Path "run_clean_server.py")) {
    Write-Warning "Clean logging script not found, using standard uvicorn"
    $Clean = $false
}
```

### Exit Code Propagation
```powershell
# Always preserve tool exit codes
& python -m pytest tests/
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-Error "Tests failed with exit code $exitCode"
    exit $exitCode
}
```

---

## Backward Compatibility Guarantees

### Unchanged Behavior
- ✅ `.\quick-start.ps1 setup` → Same as before (now with cleaner output)
- ✅ `.\quick-start.ps1 test` → Run all tests (now with quiet mode)
- ✅ `.\quick-start.ps1 serve` → Start server (now with optional clean logging)
- ✅ `.\quick-start.ps1 validate` → Full validation (now auto-managed)

### Enhanced Behavior (Opt-in)
- 🆕 `.\quick-start.ps1 setup -Detail` → Diagnostic mode
- 🆕 `.\quick-start.ps1 test -Unit` → Test filtering
- 🆕 `.\quick-start.ps1 serve -Clean` → Clean logging
- 🆕 `.\quick-start.ps1 lint` → New action
- 🆕 `.\quick-start.ps1 format` → New action
- 🆕 `.\quick-start.ps1 check` → New action

---

## Help Text Enhancement

### Updated Show-Help Function
```powershell
function Show-Help {
    Write-Header "Observatory Quick Start - Help"

    Write-Section "ACTIONS"
    Write-Info "setup     - Install dependencies and prepare environment"
    Write-Info "test      - Run test suite (optional: -Unit, -Contract, -Integration, -Coverage)"
    Write-Info "serve     - Start development server (optional: -Clean, -NewWindow)"
    Write-Info "validate  - Run full validation suite"
    Write-Info "lint      - Check code quality (read-only)"
    Write-Info "format    - Auto-format code"
    Write-Info "check     - Run lint + type checking"
    Write-Info "demo      - Run interactive demo"
    Write-Info "health    - Check server health"
    Write-Info "analyze   - Test analysis endpoint"
    Write-Info "keys      - Generate API keys"
    Write-Info "clean     - Clean generated files"

    Write-Section "FLAGS"
    Write-Info "-Detail       - Show detailed diagnostic output (all actions)"
    Write-Info "-Clean        - Use clean logging without ANSI codes (serve, validate)"
    Write-Info "-Unit         - Run only unit tests (test action)"
    Write-Info "-Contract     - Run only contract tests (test action)"
    Write-Info "-Integration  - Run only integration tests (test action)"
    Write-Info "-Coverage     - Generate coverage report (test action)"
    Write-Info "-NewWindow    - Start server in new window (serve action)"
    Write-Info "-Port <num>   - Specify port number (default: 8000)"

    Write-Section "EXAMPLES"
    Write-Host "  .\quick-start.ps1 setup -Detail" -ForegroundColor Yellow
    Write-Host "  .\quick-start.ps1 test -Unit -Coverage" -ForegroundColor Yellow
    Write-Host "  .\quick-start.ps1 serve -Clean -NewWindow" -ForegroundColor Yellow
    Write-Host "  .\quick-start.ps1 lint" -ForegroundColor Yellow
    Write-Host "  .\quick-start.ps1 format" -ForegroundColor Yellow
    Write-Host "  .\quick-start.ps1 check" -ForegroundColor Yellow
}
```

---

## Implementation Checklist

### Existing Action Enhancements
- [ ] Modify `Invoke-Setup` for verbosity control
- [ ] Modify `Invoke-Test` for filtering and coverage
- [ ] Modify `Invoke-Server` for clean logging
- [ ] Modify `Invoke-Validate` for detail/clean flags

### New Action Implementation
- [ ] Implement `Invoke-Lint` function
- [ ] Implement `Invoke-Format` function
- [ ] Implement `Invoke-Check` function

### Integration
- [ ] Add new actions to ValidateSet
- [ ] Add new actions to switch statement
- [ ] Update Show-Help with new actions and flags
- [ ] Add error handling for missing dependencies

### Testing
- [ ] Test all existing actions (backward compatibility)
- [ ] Test new actions (lint, format, check)
- [ ] Test all flag combinations
- [ ] Verify exit codes

---

**Contract Status**: ✅ DEFINED - Ready for implementation
