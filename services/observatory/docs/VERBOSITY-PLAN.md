# Verbosity Implementation Plan

## Overview

Add comprehensive verbosity controls to `quick-start.ps1` to provide clean, user-friendly output by default while preserving detailed diagnostics when needed. Integrates with Copilot CLI's clean logging solution.

---

## Verbosity Levels

### Level 1: Minimal (Default)
- **Purpose**: Clean, distraction-free output for routine operations
- **Shows**: Action results, success/failure status, critical errors only
- **Hides**: Step-by-step progress, external tool output, debug information

### Level 2: Detailed (`-Detail` flag)
- **Purpose**: Full diagnostic output for troubleshooting
- **Shows**: Everything from Level 1 + step-by-step progress, external tool output, detailed test results
- **Hides**: Nothing

---

## Output Classification

### Always Show (Both Levels)

**Action Results**:
- `[OK]` - Successful completion
- `[FAIL]` - Operation failed
- `[WARN]` - Non-critical issues
- `[INFO]` - Important status updates

**Critical Information**:
- Server URLs and ports
- API key status (exists/generated/not found)
- Test pass/fail summaries
- Error messages

### Show Only with `-Detail`

**Process Steps** (23 instances):
- "Installing dependencies..."
- "Checking for development API keys..."
- "Waiting for server to be ready..."
- "Running unit tests..."
- All `Write-Step` calls

**External Tool Output**:
- uv installation logs
- pip dependency resolution
- pytest verbose test output
- git status details
- Process startup/shutdown messages

---

## Code Changes Required

### 1. Helper Function for External Commands

**Add to quick-start.ps1** (after existing helper functions):

```powershell
function Invoke-CommandWithVerbosity {
    <#
    .SYNOPSIS
        Execute command with output controlled by $Detail flag
    #>
    param(
        [scriptblock]$Command,
        [string]$SuccessMessage = "",
        [string]$ErrorMessage = "Command failed"
    )

    try {
        if ($Detail) {
            # Show all output
            & $Command
        } else {
            # Suppress output, capture errors only
            $output = & $Command 2>&1
            if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
                Write-Host $output -ForegroundColor Red
                throw $ErrorMessage
            }
        }

        if ($SuccessMessage -and -not $Detail) {
            Write-Success $SuccessMessage
        }
    } catch {
        Write-Failure "$ErrorMessage`: $_"
        throw
    }
}
```

### 2. Modify Write-Step to Respect Detail Flag

**Current**:
```powershell
function Write-Step {
    param([string]$Message)
    Write-Host "→ $Message" -ForegroundColor Cyan
}
```

**Updated**:
```powershell
function Write-Step {
    param([string]$Message)
    if ($Detail) {
        Write-Host "→ $Message" -ForegroundColor Cyan
    }
}
```

### 3. Suppress External Command Output

#### Setup Action - uv venv

**Before** (Line 194):
```powershell
& "$uvPath" venv
if ($LASTEXITCODE -ne 0) {
    Write-Failure "Failed to create virtual environment"
    exit 1
}
Write-Success "Virtual environment created!"
```

**After**:
```powershell
# Check if venv already exists
if (Test-Path ".venv") {
    if ($Detail) {
        Write-Info "Virtual environment already exists"
    }
} else {
    Write-Step "Creating virtual environment..."
    if ($Detail) {
        & "$uvPath" venv
    } else {
        & "$uvPath" venv 2>&1 | Out-Null
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Failure "Failed to create virtual environment"
        exit 1
    }
    Write-Success "Virtual environment created!"
}
```

#### Setup Action - Dependency Installation

**Before** (Line 212-219):
```powershell
Write-Step "Installing dependencies..."
& "$($Script:Config.VenvPath)\pip.exe" install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Failure "Failed to install dependencies"
    exit 1
}
```

**After**:
```powershell
Write-Step "Installing dependencies..."
if ($Detail) {
    & "$($Script:Config.VenvPath)\pip.exe" install -e .
} else {
    & "$($Script:Config.VenvPath)\pip.exe" install -e . --quiet 2>&1 | Out-Null
}

if ($LASTEXITCODE -ne 0) {
    Write-Failure "Failed to install dependencies"
    exit 1
}

if (-not $Detail) {
    Write-Success "Dependencies installed!"
}
```

#### Setup Action - Dev Dependencies

**Before** (Line 221-228):
```powershell
Write-Step "Installing dev dependencies..."
& "$($Script:Config.VenvPath)\pip.exe" install pytest pytest-asyncio pytest-cov ruff
if ($LASTEXITCODE -ne 0) {
    Write-Failure "Failed to install dev dependencies"
    exit 1
}
```

**After**:
```powershell
Write-Step "Installing dev dependencies..."
if ($Detail) {
    & "$($Script:Config.VenvPath)\pip.exe" install pytest pytest-asyncio pytest-cov ruff
} else {
    & "$($Script:Config.VenvPath)\pip.exe" install pytest pytest-asyncio pytest-cov ruff --quiet 2>&1 | Out-Null
}

if ($LASTEXITCODE -ne 0) {
    Write-Failure "Failed to install dev dependencies"
    exit 1
}

if (-not $Detail) {
    Write-Success "Dev dependencies installed!"
}
```

#### Test Action - Pytest Verbosity

**Before** (Lines 308, 318, 328):
```powershell
& "$($Script:Config.VenvPath)\python.exe" -m pytest tests/unit/ -v
& "$($Script:Config.VenvPath)\python.exe" -m pytest tests/contract/ -v
& "$($Script:Config.VenvPath)\python.exe" -m pytest tests/integration/ -v
```

**After**:
```powershell
# Define pytest arguments based on verbosity
$pytestArgs = if ($Detail) {
    @("-v", "--tb=short")
} else {
    @("-q", "--tb=line")
}

# Unit tests
& "$($Script:Config.VenvPath)\python.exe" -m pytest tests/unit/ @pytestArgs

# Contract tests
& "$($Script:Config.VenvPath)\python.exe" -m pytest tests/contract/ @pytestArgs

# Integration tests
& "$($Script:Config.VenvPath)\python.exe" -m pytest tests/integration/ @pytestArgs
```

#### Serve Action - Server Startup

**Before** (Line 355):
```powershell
if ($NewWindow) {
    $serverScript = "cd '$PWD'; & '$($Script:Config.VenvPath)\python.exe' -m uvicorn app.main:app --host 0.0.0.0 --port $Port $(if($Reload){'--reload'})"
    Start-Process $pwsh -ArgumentList "-NoExit", "-Command", $serverScript
    Write-Success "Server starting in new $pwsh window"
}
```

**After** (with Clean flag integration):
```powershell
if ($NewWindow) {
    # Determine server command based on Clean flag
    if ($Clean) {
        $serverScript = "cd '$PWD'; & '$($Script:Config.VenvPath)\python.exe' run_clean_server.py $Port $(if($Reload){'--reload'})"
        Write-Info "Starting server with clean logging (no ANSI codes)"
    } else {
        $serverScript = "cd '$PWD'; & '$($Script:Config.VenvPath)\python.exe' -m uvicorn app.main:app --host 0.0.0.0 --port $Port $(if($Reload){'--reload'})"
    }

    Start-Process $pwsh -ArgumentList "-NoExit", "-Command", $serverScript
    Write-Success "Server starting in new $pwsh window"
}
```

### 4. Add -Clean Parameter

**Before** (Line 10):
```powershell
param(
    [Parameter()]
    [ValidateSet("setup", "test", "serve", "validate", "clean", "health", "analyze", "keys")]
    [string]$Action = "serve",

    # ... other parameters ...
)
```

**After**:
```powershell
param(
    [Parameter()]
    [ValidateSet("setup", "test", "serve", "validate", "clean", "health", "analyze", "keys")]
    [string]$Action = "serve",

    # ... existing parameters ...

    [Parameter()]
    [switch]$Clean  # Use clean logging (no ANSI codes)
)
```

### 5. Update Serve Action for Clean Logging

**Add to Invoke-Server function** (Line 351):

```powershell
function Invoke-Server {
    Write-Info "Starting Observatory server..."

    # Determine which server command to use
    $pythonExe = "$($Script:Config.VenvPath)\python.exe"

    if ($NewWindow) {
        # Build server command based on Clean flag
        if ($Clean) {
            $serverScript = "cd '$PWD'; & '$pythonExe' run_clean_server.py $Port $(if($Reload){'--reload'})"
            Write-Info "Using clean logging (no ANSI escape codes)"
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
    Write-Info "Documentation at http://127.0.0.1:$Port/docs"
}
```

### 6. Fix Output Inconsistencies

#### Issue 1: Duplicate "OK" (Line 644)

**Before**:
```powershell
Write-Success "[OK] OK"
```

**After**:
```powershell
Write-Success "Validation passed!"
```

#### Issue 2: Venv "Already Exists" Error

**Before** (Line 194):
```powershell
& "$uvPath" venv
```

**After**:
```powershell
if (-not (Test-Path ".venv")) {
    Write-Step "Creating virtual environment..."
    & "$uvPath" venv
    if ($LASTEXITCODE -ne 0) {
        Write-Failure "Failed to create virtual environment"
        exit 1
    }
    Write-Success "Virtual environment created!"
} else {
    if ($Detail) {
        Write-Info "Virtual environment already exists (skipping creation)"
    }
}
```

---

## Integration with Copilot's Clean Logging

### Files Created by Copilot (No Conflicts)
- ✅ `app/core/log_config.py` - Custom logging formatters
- ✅ `run_clean_server.py` - Clean server launcher
- ✅ `docs/CLEAN-LOGGING.md` - Documentation

### Integration Points

**1. Add `-Clean` flag to quick-start.ps1** (see section 4)

**2. Update serve action** to use `run_clean_server.py` when `-Clean` is provided

**3. Update demo action** (if it exists) to support `-Clean`:

```powershell
function Invoke-Demo {
    param([switch]$Clean)

    # Start server in background with clean logging if requested
    if ($Clean) {
        $serverProcess = Start-Process -FilePath "$($Script:Config.VenvPath)\python.exe" `
            -ArgumentList "run_clean_server.py", $Port `
            -PassThru -NoNewWindow -RedirectStandardOutput "nul" -RedirectStandardError "nul"
    } else {
        $serverProcess = Start-Process -FilePath "$($Script:Config.VenvPath)\python.exe" `
            -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", $Port `
            -PassThru -NoNewWindow -RedirectStandardOutput "nul" -RedirectStandardError "nul"
    }

    # ... rest of demo logic ...
}
```

---

## Before/After Examples

### Example 1: Setup (Default)

**Before**:
```
→ Creating virtual environment...
[OK] Virtual environment created!
→ Installing dependencies...
Collecting fastapi
  Using cached fastapi-0.109.0-py3-none-any.whl (92 kB)
Collecting uvicorn[standard]
  Using cached uvicorn-0.27.0-py3-none-any.whl (60 kB)
... [50+ lines of pip output] ...
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 ...
→ Installing dev dependencies...
... [30+ lines more] ...
[OK] Setup complete!
```

**After (Default)**:
```
[OK] Virtual environment created!
[OK] Dependencies installed!
[OK] Dev dependencies installed!
[OK] API keys generated!
[OK] Setup complete!
```

**After (With -Detail)**:
```
→ Creating virtual environment...
[Runs: uv venv]
[OK] Virtual environment created!
→ Installing dependencies...
Collecting fastapi
  Using cached fastapi-0.109.0-py3-none-any.whl (92 kB)
... [all pip output] ...
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 ...
→ Installing dev dependencies...
... [all pip output] ...
→ Checking for development API keys...
→ Generating development API keys...
[OK] API keys generated!
[OK] Setup complete!
```

### Example 2: Tests (Default)

**Before**:
```
→ Running unit tests...
==================== test session starts ====================
platform win32 -- Python 3.12.0, pytest-7.4.4, pluggy-1.3.0 -- python.exe
cachedir: .pytest_cache
rootdir: C:\...\observatory
configfile: pytest.ini
plugins: asyncio-0.23.3, cov-4.1.0
collected 94 items

tests/unit/test_analyzer.py::test_conversation_parsing PASSED  [  1%]
tests/unit/test_analyzer.py::test_turn_extraction PASSED        [  2%]
... [90+ more lines] ...
==================== 94 passed in 2.31s ====================
```

**After (Default)**:
```
[OK] Unit tests: 94 passed in 2.31s
[OK] Contract tests: 12 passed in 0.89s
[OK] Integration tests: 8 passed in 1.24s
[OK] All tests passed!
```

**After (With -Detail)**:
```
→ Running unit tests...
==================== test session starts ====================
... [full pytest output] ...
==================== 94 passed in 2.31s ====================
→ Running contract tests...
... [full pytest output] ...
[OK] All tests passed!
```

### Example 3: Serve with Clean Logging

**Command**:
```powershell
.\quick-start.ps1 serve -Clean -NewWindow
```

**Output**:
```
[INFO] Starting Observatory server...
[INFO] Using clean logging (no ANSI escape codes)
[OK] Server starting in new pwsh window

# In server window:
[2025-01-04 20:30:15] INFO     Started server process [12345]
[2025-01-04 20:30:15] INFO     Waiting for application startup
[2025-01-04 20:30:15] INFO     Application startup complete
[2025-01-04 20:30:15] INFO     Uvicorn running on http://0.0.0.0:8000
[2025-01-04 20:30:20] INFO     127.0.0.1:12345 - "GET /health HTTP/1.1" 200
```

---

## Usage Examples

### Standard Operations (Clean Output)
```powershell
# Setup everything (minimal output)
.\quick-start.ps1 setup

# Run tests (summary only)
.\quick-start.ps1 test

# Validate (auto-managed server, clean output)
.\quick-start.ps1 validate

# Serve with clean Windows logs
.\quick-start.ps1 serve -Clean -NewWindow
```

### Troubleshooting (Detailed Output)
```powershell
# Setup with full diagnostics
.\quick-start.ps1 setup -Detail

# Tests with verbose output
.\quick-start.ps1 test -Detail

# Validation with step-by-step progress
.\quick-start.ps1 validate -Detail

# Serve in foreground with clean logs
.\quick-start.ps1 serve -Clean
```

### Combined Flags
```powershell
# Detailed validation with clean server logs
.\quick-start.ps1 validate -Detail -Clean

# New window server with clean logs and reload
.\quick-start.ps1 serve -NewWindow -Clean -Reload
```

---

## Implementation Checklist

### Phase 1: Core Verbosity (Priority: High)
- [ ] Add `Invoke-CommandWithVerbosity` helper function
- [ ] Update `Write-Step` to respect `$Detail` flag
- [ ] Add venv existence check (prevent error on re-run)
- [ ] Suppress uv venv output when not in Detail mode

### Phase 2: External Commands (Priority: High)
- [ ] Suppress pip install output (use `--quiet` + Out-Null)
- [ ] Add pytest verbosity control (`-v` vs `-q`)
- [ ] Fix duplicate "[OK] OK" message
- [ ] Add success messages when not in Detail mode

### Phase 3: Clean Logging Integration (Priority: Medium)
- [ ] Add `-Clean` parameter to quick-start.ps1
- [ ] Update `Invoke-Server` to use `run_clean_server.py` when Clean flag is set
- [ ] Update demo action (if exists) to support Clean flag
- [ ] Document Clean flag usage in help text

### Phase 4: Testing & Documentation (Priority: Medium)
- [ ] Test all combinations: setup/test/validate/serve × Detail/Clean flags
- [ ] Verify no conflicts between Detail and Clean flags
- [ ] Update WORKFLOW.md with verbosity examples
- [ ] Add Before/After examples to README

### Phase 5: Edge Cases (Priority: Low)
- [ ] Handle graceful degradation if run_clean_server.py missing
- [ ] Validate Clean flag only affects serve/validate actions
- [ ] Ensure error messages always show (regardless of Detail flag)
- [ ] Test with different PowerShell versions (Core vs Windows)

---

## Testing Strategy

### Test Matrix

| Action | Flag Combo | Expected Behavior |
|--------|------------|-------------------|
| `setup` | (none) | Minimal output, show only results |
| `setup` | `-Detail` | Show all steps + external tool output |
| `test` | (none) | Pytest quiet mode, show summary |
| `test` | `-Detail` | Pytest verbose, show all test names |
| `validate` | (none) | Clean validation output, auto-manage server |
| `validate` | `-Detail` | Show server start/stop, step-by-step progress |
| `validate` | `-Clean` | Use clean server logs (no ANSI) |
| `validate` | `-Detail -Clean` | Verbose validation + clean server logs |
| `serve` | `-Clean` | Use run_clean_server.py |
| `serve` | `-NewWindow -Clean` | New window with clean logs |

### Validation Commands

```powershell
# Test 1: Setup twice (should not error)
.\quick-start.ps1 setup
.\quick-start.ps1 setup  # Should skip venv creation

# Test 2: Verbosity comparison
.\quick-start.ps1 test > test-minimal.log 2>&1
.\quick-start.ps1 test -Detail > test-detailed.log 2>&1
Compare-Object (Get-Content test-minimal.log) (Get-Content test-detailed.log)

# Test 3: Clean logging (check for ANSI codes)
.\quick-start.ps1 serve -Clean > server-clean.log 2>&1
# server-clean.log should have NO ←[XXm sequences

# Test 4: Combined flags
.\quick-start.ps1 validate -Detail -Clean
```

---

## Rollback Plan

If issues arise during implementation:

1. **Revert Write-Step changes**:
   ```powershell
   git checkout services/observatory/quick-start.ps1 -- Write-Step
   ```

2. **Keep external command suppression** (high value, low risk)

3. **Document issues** in `docs/VERBOSITY-ISSUES.md`

4. **Implement incrementally**:
   - Phase 1 first (core verbosity)
   - Test thoroughly before Phase 2
   - Clean logging (Phase 3) is independent, can be done separately

---

## Summary

This plan provides:

✅ **Clean default output** - Minimal, focused on results
✅ **Full diagnostics on demand** - `-Detail` flag for troubleshooting
✅ **Windows compatibility** - `-Clean` flag for ANSI-free logs
✅ **No breaking changes** - All existing commands work unchanged
✅ **Incremental rollout** - Can implement in phases
✅ **No conflicts** - Integrates cleanly with Copilot's work

**Next Steps**: Review plan → Implement Phase 1 → Test → Iterate
