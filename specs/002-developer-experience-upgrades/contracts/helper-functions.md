# Helper Function Contracts

**Feature**: 002-developer-experience-upgrades
**File**: `services/observatory/quick-start.ps1`
**Type**: Internal Utility Function Contracts

---

## Existing Helper Functions (Enhanced)

### Write-Step (MODIFIED)
```powershell
function Write-Step {
    param([string]$Message)
    if ($Detail) {
        Write-Host "→ $Message" -ForegroundColor Magenta
    }
}
```

**Contract**:
- **Purpose**: Display step-by-step progress messages
- **Parameters**:
  - `$Message` (string, required): Progress message to display
- **Behavior**:
  - **Default mode** (`$Detail = $false`): Silent (no output)
  - **Detail mode** (`$Detail = $true`): Display message with arrow prefix
- **Output Format**: `→ {Message}` in magenta color
- **Used By**: All action functions (23 call sites in current implementation)
- **Breaking Change**: Yes (was always shown before, now conditional)
- **Mitigation**: Success messages added for default mode to maintain feedback

**Examples**:
```powershell
# Default mode (no Detail flag)
Write-Step "Installing dependencies..."  # Output: (nothing)

# Detail mode (-Detail flag)
Write-Step "Installing dependencies..."  # Output: → Installing dependencies...
```

---

### Write-Success (UNCHANGED)
```powershell
function Write-Success {
    param([string]$Text)
    Write-Host "[OK] " -ForegroundColor Green -NoNewline
    Write-Host $Text -ForegroundColor White
}
```

**Contract**:
- **Purpose**: Display success messages
- **Parameters**: `$Text` (string, required)
- **Behavior**: Always shown (verbosity-independent)
- **Output Format**: `[OK] {Text}` (green + white)
- **Enhancement**: Use more frequently in default mode to replace hidden Write-Step calls

---

### Write-Error (UNCHANGED - Renamed to Write-Failure to avoid conflict)
```powershell
function Write-Failure {
    param([string]$Text)
    Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
    Write-Host $Text -ForegroundColor White
}
```

**Contract**:
- **Purpose**: Display error messages
- **Parameters**: `$Text` (string, required)
- **Behavior**: Always shown (verbosity-independent)
- **Output Format**: `[FAIL] {Text}` (red + white)
- **Note**: Renamed from `Write-Error` to avoid PowerShell built-in conflict

---

### Write-Info (UNCHANGED)
```powershell
function Write-Info {
    param([string]$Text)
    Write-Host "[INFO] " -ForegroundColor Cyan -NoNewline
    Write-Host $Text -ForegroundColor White
}
```

**Contract**:
- **Purpose**: Display informational messages
- **Parameters**: `$Text` (string, required)
- **Behavior**: Always shown (verbosity-independent)
- **Output Format**: `[INFO] {Text}` (cyan + white)

---

### Write-Warning (UNCHANGED)
```powershell
function Write-Warning {
    param([string]$Text)
    Write-Host "[WARN] " -ForegroundColor Yellow -NoNewline
    Write-Host $Text -ForegroundColor White
}
```

**Contract**:
- **Purpose**: Display warning messages
- **Parameters**: `$Text` (string, required)
- **Behavior**: Always shown (verbosity-independent)
- **Output Format**: `[WARN] {Text}` (yellow + white)

---

## New Helper Functions (Added by Feature 002)

### Invoke-CommandWithVerbosity (NEW)
```powershell
function Invoke-CommandWithVerbosity {
    <#
    .SYNOPSIS
        Execute external command with output controlled by $Detail flag
    .PARAMETER Command
        ScriptBlock containing the command to execute
    .PARAMETER SuccessMessage
        Message to display on success (default mode only)
    .PARAMETER ErrorMessage
        Message prefix for errors
    .EXAMPLE
        Invoke-CommandWithVerbosity -Command { uv venv } -SuccessMessage "Virtual environment created"
    #>
    param(
        [Parameter(Mandatory=$true)]
        [scriptblock]$Command,

        [Parameter()]
        [string]$SuccessMessage = "",

        [Parameter()]
        [string]$ErrorMessage = "Command failed"
    )

    try {
        if ($Detail) {
            # Show all output (stdout and stderr)
            & $Command
        } else {
            # Suppress output, capture for error reporting
            $output = & $Command 2>&1
            if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
                # Error occurred - show captured output
                Write-Host $output -ForegroundColor Red
                throw "$ErrorMessage (exit code: $LASTEXITCODE)"
            }
        }

        # Show success message in default mode
        if ($SuccessMessage -and -not $Detail) {
            Write-Success $SuccessMessage
        }
    }
    catch {
        Write-Failure "$ErrorMessage: $_"
        throw
    }
}
```

**Contract**:
- **Purpose**: Execute external commands with verbosity-aware output control
- **Parameters**:
  - `$Command` (scriptblock, required): Command to execute
  - `$SuccessMessage` (string, optional): Success message for default mode
  - `$ErrorMessage` (string, optional): Error prefix (default: "Command failed")
- **Behavior**:
  - **Detail mode**: Show all command output (stdout/stderr)
  - **Default mode**: Suppress output, show success message if provided
  - **Error handling**: Always show errors with captured output
- **Exit Code Handling**: Preserves `$LASTEXITCODE` from command
- **Output Streams**: Merges stderr to stdout (`2>&1`) for consistent capture

**Usage Examples**:
```powershell
# Setup - uv venv
Invoke-CommandWithVerbosity -Command { & "$uvPath" venv } -SuccessMessage "Virtual environment created"

# Setup - pip install
Invoke-CommandWithVerbosity -Command {
    & "$venvPath\pip.exe" install -e . --quiet
} -SuccessMessage "Dependencies installed" -ErrorMessage "Failed to install dependencies"

# Test - pytest
Invoke-CommandWithVerbosity -Command {
    & "$venvPath\python.exe" -m pytest tests/unit/ -q
} -ErrorMessage "Unit tests failed"
```

**Error Scenarios**:
```powershell
# Scenario 1: Command succeeds (default mode)
Invoke-CommandWithVerbosity { uv venv } -SuccessMessage "Done"
# Output: [OK] Done

# Scenario 2: Command succeeds (detail mode)
$Detail = $true
Invoke-CommandWithVerbosity { uv venv } -SuccessMessage "Done"
# Output: [full uv venv output]

# Scenario 3: Command fails (always show error)
Invoke-CommandWithVerbosity { uv invalid-cmd } -ErrorMessage "UV failed"
# Output: [error output] + [FAIL] UV failed: ...
```

---

### Get-PytestArguments (NEW)
```powershell
function Get-PytestArguments {
    <#
    .SYNOPSIS
        Build pytest argument array based on flags
    .OUTPUTS
        String array of pytest arguments
    #>
    [OutputType([string[]])]
    param()

    $args = @()

    # Verbosity
    if ($Detail) {
        $args += @("-v", "--tb=short")
    } else {
        $args += @("-q", "--tb=line")
    }

    # Coverage
    if ($Coverage) {
        $args += @("--cov=app", "--cov-report=term-missing")
    }

    return $args
}
```

**Contract**:
- **Purpose**: Generate pytest arguments based on script flags
- **Parameters**: None (uses script-scoped variables)
- **Returns**: String array of pytest arguments
- **Behavior**:
  - Default: `@("-q", "--tb=line")` - quiet mode, one-line tracebacks
  - With `-Detail`: `@("-v", "--tb=short")` - verbose, short tracebacks
  - With `-Coverage`: Add `--cov=app --cov-report=term-missing`
- **Used By**: `Invoke-Test` function

**Examples**:
```powershell
# Default
Get-PytestArguments  # Returns: @("-q", "--tb=line")

# With Detail
$Detail = $true
Get-PytestArguments  # Returns: @("-v", "--tb=short")

# With Coverage
$Coverage = $true
Get-PytestArguments  # Returns: @("-q", "--tb=line", "--cov=app", "--cov-report=term-missing")

# With Detail + Coverage
$Detail = $true
$Coverage = $true
Get-PytestArguments  # Returns: @("-v", "--tb=short", "--cov=app", "--cov-report=term-missing")
```

---

### Get-TestPaths (NEW)
```powershell
function Get-TestPaths {
    <#
    .SYNOPSIS
        Determine which test paths to run based on filter flags
    .OUTPUTS
        String array of test directory paths
    #>
    [OutputType([string[]])]
    param()

    # If no filters specified, run all tests
    if (-not ($Unit -or $Contract -or $Integration)) {
        return @("tests/unit/", "tests/contract/", "tests/integration/")
    }

    # Build array of selected test types
    $paths = @()
    if ($Unit) { $paths += "tests/unit/" }
    if ($Contract) { $paths += "tests/contract/" }
    if ($Integration) { $paths += "tests/integration/" }

    return $paths
}
```

**Contract**:
- **Purpose**: Determine test directories based on filter flags
- **Parameters**: None (uses script-scoped variables)
- **Returns**: String array of test directory paths
- **Behavior**:
  - No filters: Return all test directories
  - Filters specified: Return only selected directories
  - Validation: Paths always end with `/` for pytest compatibility
- **Used By**: `Invoke-Test` function

**Examples**:
```powershell
# No filters (run all)
Get-TestPaths  # Returns: @("tests/unit/", "tests/contract/", "tests/integration/")

# Unit only
$Unit = $true
Get-TestPaths  # Returns: @("tests/unit/")

# Unit + Contract
$Unit = $true
$Contract = $true
Get-TestPaths  # Returns: @("tests/unit/", "tests/contract/")

# All filters (explicit all)
$Unit = $true
$Contract = $true
$Integration = $true
Get-TestPaths  # Returns: @("tests/unit/", "tests/contract/", "tests/integration/")
```

---

### Get-ServerCommand (NEW)
```powershell
function Get-ServerCommand {
    <#
    .SYNOPSIS
        Build server start command based on flags
    .OUTPUTS
        String containing complete server command
    #>
    [OutputType([string])]
    param()

    $pythonExe = ".venv\Scripts\python.exe"

    if ($Clean) {
        # Check if clean logging script exists
        if (-not (Test-Path "run_clean_server.py")) {
            Write-Warning "Clean logging script not found, using standard uvicorn"
            return "& $pythonExe -m uvicorn app.main:app --host 0.0.0.0 --port $Port $(if($Reload){'--reload'})"
        }
        return "& $pythonExe run_clean_server.py $Port $(if($Reload){'--reload'})"
    } else {
        return "& $pythonExe -m uvicorn app.main:app --host 0.0.0.0 --port $Port $(if($Reload){'--reload'})"
    }
}
```

**Contract**:
- **Purpose**: Generate server start command based on flags
- **Parameters**: None (uses script-scoped variables)
- **Returns**: String containing complete command
- **Behavior**:
  - Default: Standard uvicorn command
  - With `-Clean`: Use `run_clean_server.py` if available
  - Graceful degradation: Fallback to uvicorn if clean script missing
  - Preserves `-Reload` flag if specified
- **Used By**: `Invoke-Server`, `Invoke-Validate` functions

**Examples**:
```powershell
# Default
Get-ServerCommand
# Returns: "& .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

# With Clean flag
$Clean = $true
Get-ServerCommand
# Returns: "& .venv\Scripts\python.exe run_clean_server.py 8000"

# With Reload
$Reload = $true
Get-ServerCommand
# Returns: "& .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# Clean + Reload
$Clean = $true
$Reload = $true
Get-ServerCommand
# Returns: "& .venv\Scripts\python.exe run_clean_server.py 8000 --reload"
```

---

### Test-ActionPrerequisites (NEW)
```powershell
function Test-ActionPrerequisites {
    <#
    .SYNOPSIS
        Validate prerequisites for specified action
    .PARAMETER Action
        Action name to validate
    .OUTPUTS
        Boolean - $true if prerequisites met
    #>
    [OutputType([bool])]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ActionName
    )

    $allGood = $true

    # Virtual environment check (most actions)
    if ($ActionName -notin @('setup', 'help', 'clean')) {
        if (-not (Test-Path ".venv\Scripts\python.exe")) {
            Write-Failure "Virtual environment not found. Run: .\quick-start.ps1 setup"
            $allGood = $false
        }
    }

    # Tool-specific checks
    switch ($ActionName) {
        { $_ -in @('lint', 'format', 'check') } {
            if (-not (Test-Path ".venv\Scripts\ruff.exe")) {
                Write-Failure "ruff not installed. Run: .\quick-start.ps1 setup"
                $allGood = $false
            }
        }
        'check' {
            # Note: mypy check would go here when added
            if (-not (Test-Path ".venv\Scripts\mypy.exe")) {
                Write-Warning "mypy not installed. Type checking will be skipped."
            }
        }
        'test' {
            if (-not (Test-Path "tests")) {
                Write-Failure "tests directory not found"
                $allGood = $false
            }
        }
    }

    return $allGood
}
```

**Contract**:
- **Purpose**: Validate action prerequisites before execution
- **Parameters**: `$ActionName` (string, required)
- **Returns**: Boolean indicating prerequisite status
- **Behavior**:
  - Check virtual environment (except for setup/help/clean)
  - Check tool availability (action-specific)
  - Display helpful error messages
  - Return `$true` only if all checks pass
- **Side Effects**: Displays error/warning messages
- **Used By**: Main action dispatcher (before invoking action function)

**Examples**:
```powershell
# Check before test action
if (Test-ActionPrerequisites -ActionName 'test') {
    Invoke-Test
} else {
    exit 1
}

# Check before lint action
if (Test-ActionPrerequisites -ActionName 'lint') {
    Invoke-Lint
} else {
    exit 1
}
```

---

## Helper Function Call Flow

### Setup Action
```
Main → Invoke-Setup
         ├→ Write-Step (suppressed unless -Detail)
         ├→ Invoke-CommandWithVerbosity (for uv venv)
         ├→ Invoke-CommandWithVerbosity (for pip install)
         └→ Write-Success (always shown)
```

### Test Action
```
Main → Test-ActionPrerequisites
       ├→ Invoke-Test
       │    ├→ Get-TestPaths
       │    ├→ Get-PytestArguments
       │    ├→ Write-Step (suppressed unless -Detail)
       │    └→ Invoke-CommandWithVerbosity (for pytest)
       └→ Write-Success / Write-Failure
```

### Serve Action
```
Main → Test-ActionPrerequisites
       ├→ Invoke-Server
       │    ├→ Get-ServerCommand
       │    ├→ Write-Info (server info)
       │    └→ Execute server command
       └→ Write-Info (URLs)
```

### Lint/Format/Check Actions
```
Main → Test-ActionPrerequisites
       ├→ Invoke-{Lint|Format|Check}
       │    ├→ Write-Step (suppressed unless -Detail)
       │    ├→ Invoke-CommandWithVerbosity (for ruff/mypy)
       │    └→ Write-Success / Write-Failure
       └→ Exit with tool's exit code
```

---

## Implementation Checklist

### Modify Existing Functions
- [ ] Update `Write-Step` to check `$Detail` flag
- [ ] Ensure all status functions (Success/Failure/Info/Warning) unchanged

### Implement New Functions
- [ ] Implement `Invoke-CommandWithVerbosity`
- [ ] Implement `Get-PytestArguments`
- [ ] Implement `Get-TestPaths`
- [ ] Implement `Get-ServerCommand`
- [ ] Implement `Test-ActionPrerequisites`

### Integration
- [ ] Replace direct external command calls with `Invoke-CommandWithVerbosity`
- [ ] Use helper functions in action implementations
- [ ] Add prerequisite checks to main action dispatcher

### Testing
- [ ] Test `Write-Step` with/without `-Detail`
- [ ] Test `Invoke-CommandWithVerbosity` error handling
- [ ] Test pytest argument generation for all flag combinations
- [ ] Test test path selection logic
- [ ] Test server command generation
- [ ] Test prerequisite validation

---

**Contract Status**: ✅ DEFINED - Ready for implementation
