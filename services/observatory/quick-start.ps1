#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Atrium Observatory Quick Start Script
    
.DESCRIPTION
    Professional developer tool for running tests, starting server, and testing API endpoints.
    Features colorful console output, detailed logging, and comprehensive help.
    
.PARAMETER Action
    The action to perform: test, serve, demo, health, analyze, setup, clean, help
    
.PARAMETER Port
    Port number for the server (default: 8000)
    
.PARAMETER Detail
    Enable detailed output with extra logging
    
.EXAMPLE
    .\quick-start.ps1 test
    Run the full test suite
    
.EXAMPLE
    .\quick-start.ps1 serve -Port 8001
    Start the development server on port 8001
    
.EXAMPLE
    .\quick-start.ps1 demo
    Run a full demo (tests, server, API calls)
    
.EXAMPLE
    .\quick-start.ps1 analyze
    Test the analysis endpoint with sample data
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet('test', 'serve', 'demo', 'health', 'analyze', 'keys', 'setup', 'clean', 'validate', 'lint', 'format', 'check', 'help')]
    [string]$Action = 'help',

    [Parameter()]
    [int]$Port = 8000,

    [Parameter()]
    [switch]$Detail,

    [Parameter()]
    [switch]$NewWindow,

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
)

# ============================================================================
# PARAMETER VALIDATION (Feature 002 - T024)
# ============================================================================

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

# Rule 3: Multiple test filters selected = run all selected types (informational)
$testFilterCount = @($Unit, $Contract, $Integration, $Validation).Where({$_}).Count
if ($testFilterCount -gt 1) {
    Write-Host "[INFO] Multiple test types selected - running: $(if($Unit){'Unit '})$(if($Contract){'Contract '})$(if($Integration){'Integration '})$(if($Validation){'Validation'})" -ForegroundColor Cyan
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

# ============================================================================
# CONFIGURATION
# ============================================================================

$Script:Config = @{
    ServiceName = "Atrium Observatory"
    Version     = "0.1.0"
    BaseUrl     = "http://127.0.0.1:$Port"  # Use 127.0.0.1 instead of localhost for Windows compatibility
    VenvPath    = ".venv\Scripts"
    DataPath    = "data"
}

# ============================================================================
# COLOR SCHEME
# ============================================================================

function Write-Header {
    param([string]$Text)
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor White
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host "[OK] " -ForegroundColor Green -NoNewline
    Write-Host $Text -ForegroundColor White
}

function Write-Error {
    param([string]$Text)
    Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
    Write-Host $Text -ForegroundColor White
}

function Write-Info {
    param([string]$Text)
    Write-Host "[INFO] " -ForegroundColor Cyan -NoNewline
    Write-Host $Text -ForegroundColor White
}

function Write-Warning {
    param([string]$Text)
    Write-Host "[WARN] " -ForegroundColor Yellow -NoNewline
    Write-Host $Text -ForegroundColor White
}

function Write-Step {
    param([string]$Text)
    if ($Detail) {
        Write-Host "-> " -ForegroundColor Magenta -NoNewline
        Write-Host $Text -ForegroundColor White
    }
}

function Write-Result {
    param(
        [string]$Label,
        [string]$Value,
        [string]$Color = "Cyan"
    )
    Write-Host "  $Label`: " -ForegroundColor Gray -NoNewline
    Write-Host $Value -ForegroundColor $Color
}

function Write-Section {
    param([string]$Text)
    Write-Host "-------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host $Text -ForegroundColor Yellow
    Write-Host "-------------------------------------------------------------" -ForegroundColor DarkGray
}

function Write-ApiCall {
    param(
        [string]$Method,
        [string]$Endpoint,
        [string]$Status
    )
    $MethodColor = switch ($Method) {
        "GET" { "Green" }
        "POST" { "Blue" }
        "DELETE" { "Red" }
        default { "White" }
    }
    
    Write-Host "  " -NoNewline
    Write-Host $Method -ForegroundColor $MethodColor -NoNewline
    Write-Host " $Endpoint " -ForegroundColor White -NoNewline
    
    if ($Status -match "^2\d\d") {
        Write-Host "-> $Status" -ForegroundColor Green
    } elseif ($Status -match "^4\d\d") {
        Write-Host "-> $Status" -ForegroundColor Yellow
    } else {
        Write-Host "-> $Status" -ForegroundColor Red
    }
}

# ============================================================================
# HELPER FUNCTIONS (Feature 002)
# ============================================================================

function Invoke-CommandWithVerbosity {
    <#
    .SYNOPSIS
        Execute external command with output controlled by $Detail flag
    .DESCRIPTION
        Implements NFR-005 (<100ms overhead) and NFR-006 (efficient streaming)
        via 2>&1 redirection for verbosity control
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

    if ($Detail) {
        # Detail mode: Show all output (stdout and stderr)
        & $Command
    } else {
        # Default mode: Suppress output, capture for error reporting
        $output = & $Command 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
            # Error occurred - show minimal summary instead of full output
            # Extract just the summary lines for pytest failures
            $lines = $output -split "`n"
            $summaryStarted = $false
            $relevantLines = @()
            
            foreach ($line in $lines) {
                # Show FAILED lines
                if ($line -match "^FAILED ") {
                    $relevantLines += $line
                }
                # Show the short test summary
                elseif ($line -match "^=+ (FAILURES|short test summary|failed|passed)") {
                    $summaryStarted = $true
                    $relevantLines += $line
                }
                # Show summary content
                elseif ($summaryStarted -and $line -match "(FAILED|passed|failed|warnings)") {
                    $relevantLines += $line
                }
            }
            
            # If we got relevant lines, show them; otherwise show count
            if ($relevantLines.Count -gt 0) {
                $relevantLines | Select-Object -First 10 | ForEach-Object {
                    if ($_ -match "FAILED") {
                        Write-Host $_ -ForegroundColor Red
                    } else {
                        Write-Host $_ -ForegroundColor Gray
                    }
                }
            }
            
            # Don't throw - let the calling function handle the failure
            # The LASTEXITCODE is still set and will be checked by caller
        }
    }

    # Show success message in default mode
    if ($SuccessMessage -and -not $Detail -and ($LASTEXITCODE -eq 0 -or $null -eq $LASTEXITCODE)) {
        Write-Success $SuccessMessage
    }
}

function Get-PythonExePath {
    <#
    .SYNOPSIS
        Get path to Python executable in virtual environment
    .DESCRIPTION
        Centralized function to return Python executable path.
        Reduces duplication across quality check functions.
    .EXAMPLE
        $pythonExe = Get-PythonExePath
    #>
    return "$($Script:Config.VenvPath)\python.exe"
}

function Start-TestServer {
    <#
    .SYNOPSIS
        Start server in background for integration/validation tests
    .DESCRIPTION
        Starts uvicorn server as background process for testing.
        Waits for server to be ready before returning.
    .OUTPUTS
        Process object for the server (to stop later)
    #>
    Write-Step "Starting test server in background..."
    
    $pythonExe = Get-PythonExePath
    $uvicornArgs = @(
        "-m", "uvicorn",
        "app.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--log-level", "warning"
    )
    
    $serverProcess = Start-Process -FilePath $pythonExe -ArgumentList $uvicornArgs -PassThru -WindowStyle Hidden
    
    # Wait for server to be ready (max 10 seconds)
    $maxWait = 10
    $waited = 0
    $ready = $false
    
    while ($waited -lt $maxWait -and -not $ready) {
        Start-Sleep -Milliseconds 500
        $waited += 0.5
        
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 1 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                $ready = $true
            }
        } catch {
            # Server not ready yet, continue waiting
        }
    }
    
    if ($ready) {
        Write-Success "Test server ready"
    } else {
        Write-Warning "Server may still be starting (waited ${waited}s)"
    }
    
    return $serverProcess
}

function Stop-TestServer {
    <#
    .SYNOPSIS
        Stop the test server process
    .PARAMETER ServerProcess
        Process object returned from Start-TestServer
    #>
    param(
        [Parameter(Mandatory=$true)]
        $ServerProcess
    )
    
    if ($ServerProcess -and -not $ServerProcess.HasExited) {
        Write-Step "Stopping test server..."
        try {
            Stop-Process -Id $ServerProcess.Id -Force -ErrorAction Stop
            Write-Success "Test server stopped"
        } catch {
            Write-Warning "Could not stop server process: $_"
        }
    }
}

function Invoke-TestSuite {
    <#
    .SYNOPSIS
        Run a specific test suite with consistent error handling
    .DESCRIPTION
        Reduces duplication in test execution logic.
        Handles pytest invocation, exit codes, and result tracking.
    .PARAMETER TestType
        Type of test (unit, contract, integration)
    .PARAMETER TestPath
        Path to test directory
    .PARAMETER PytestArgs
        Arguments to pass to pytest
    .EXAMPLE
        Invoke-TestSuite -TestType "unit" -TestPath "tests/unit/" -PytestArgs $pytestArgs
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$TestType,

        [Parameter(Mandatory=$true)]
        [string]$TestPath,

        [Parameter(Mandatory=$true)]
        [array]$PytestArgs
    )

    Write-Step "Running $TestType tests..."

    $pythonExe = Get-PythonExePath
    $command = { & $pythonExe -m pytest $TestPath @PytestArgs }

    Invoke-CommandWithVerbosity -Command $command -SuccessMessage "$($TestType.Substring(0,1).ToUpper())$($TestType.Substring(1)) tests passed"

    $exitCode = $LASTEXITCODE
    $passed = ($exitCode -eq 0)

    if (-not $Detail -and -not $passed) {
        if ($TestType -eq "integration") {
            Write-Warning "$($TestType.Substring(0,1).ToUpper())$($TestType.Substring(1)) tests failed (exit code: $exitCode)"
            Write-Info "Some integration tests may require the server running"
        } else {
            Write-Error "$($TestType.Substring(0,1).ToUpper())$($TestType.Substring(1)) tests failed (exit code: $exitCode)"
        }
    }

    Write-Host ""

    return @{
        ExitCode = $exitCode
        Passed = $passed
    }
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

function Test-Prerequisites {
    Write-Section "Checking Prerequisites"
    
    $allGood = $true
    
    # Check Python
    Write-Step "Checking Python installation..."
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    } catch {
        Write-Error "Python not found. Please install Python 3.11+"
        $allGood = $false
    }
    
    # Check uv
    Write-Step "Checking uv package manager..."
    try {
        $uvVersion = uv --version 2>&1
        Write-Success "uv found: $uvVersion"
    } catch {
        Write-Warning "uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        $allGood = $false
    }
    
    # Check virtual environment
    Write-Step "Checking virtual environment..."
    if (Test-Path $Script:Config.VenvPath) {
        Write-Success "Virtual environment found"
    } else {
        Write-Warning "Virtual environment not found. Run: .\quick-start.ps1 setup"
        $allGood = $false
    }
    
    Write-Host ""
    return $allGood
}

function Invoke-Setup {
    Write-Header "Setting Up Observatory Environment"

    # T005: Add venv existence check + verbosity control
    if (-not (Test-Path ".venv")) {
        Write-Step "Creating virtual environment with uv..."
        Invoke-CommandWithVerbosity -Command {
            uv venv
        } -SuccessMessage "Virtual environment created" -ErrorMessage "Failed to create virtual environment"
    } else {
        if ($Detail) {
            Write-Info "Virtual environment already exists (skipping creation)"
        }
    }

    # T006: Apply verbosity to dependency installation
    Write-Step "Installing dependencies..."
    Invoke-CommandWithVerbosity -Command {
        uv pip install -e .
    } -SuccessMessage "Dependencies installed" -ErrorMessage "Failed to install dependencies"

    # T007: Apply verbosity to dev dependencies
    Write-Step "Installing development dependencies..."
    Invoke-CommandWithVerbosity -Command {
        uv pip install -e ".[dev]"
    } -SuccessMessage "Development dependencies installed" -ErrorMessage "Failed to install development dependencies"

    # Auto-generate API keys if they don't exist
    Write-Host ""
    Write-Step "Checking for development API keys..."
    if (Test-Path "dev-api-keys.txt") {
        Write-Success "API keys already exist"
    } else {
        Write-Info "No API keys found. Generating now..."
        Write-Host ""
        Invoke-KeyManagement
    }

    Write-Host ""
    Write-Success "Setup complete!"
    Write-Info "Run '.\quick-start.ps1 test' to verify installation"
    Write-Info "Run '.\quick-start.ps1 validate' to test the service"
}

function Invoke-Clean {
    Write-Header "Cleaning Observatory Environment"
    
    $items = @(
        @{Path = ".venv"; Name = "Virtual environment"},
        @{Path = $Script:Config.DataPath; Name = "Data directory"},
        @{Path = "__pycache__"; Name = "Python cache"},
        @{Path = ".pytest_cache"; Name = "Pytest cache"},
        @{Path = "*.egg-info"; Name = "Egg info"},
        @{Path = "dev-api-keys.txt"; Name = "Development API keys"}
    )
    
    foreach ($item in $items) {
        if (Test-Path $item.Path) {
            Write-Step "Removing $($item.Name)..."
            Remove-Item $item.Path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Success "Removed $($item.Name)"
        }
    }
    
    Write-Success "Clean complete!"
}

# ============================================================================
# API KEY MANAGEMENT
# ============================================================================

function Invoke-KeyManagement {
    Write-Header "API Key Management"
    
    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites not met. Run: .\quick-start.ps1 setup"
        return
    }
    
    Write-Info "This will generate and register API keys for development"
    Write-Warning "Keys are in-memory only - they reset when the server restarts"
    Write-Host ""
    
    Write-Section "Generating API Keys"
    
    # Create Python script to generate keys
    $pythonScript = @"
from app.middleware.auth import generate_api_key, register_api_key
import json

# Generate keys
dev_key = generate_api_key()
partner_key = generate_api_key()

# Register them
register_api_key(dev_key, tier='api_key')
register_api_key(partner_key, tier='partner')

# Output as JSON for PowerShell to parse
result = {
    'dev_key': dev_key,
    'partner_key': partner_key
}
print(json.dumps(result))
"@
    
    # Run Python script
    $tempFile = [System.IO.Path]::GetTempFileName()
    $pythonScript | Out-File -FilePath $tempFile -Encoding UTF8
    
    try {
        Write-Step "Generating keys..."
        $output = & "$($Script:Config.VenvPath)\python.exe" $tempFile
        $keys = $output | ConvertFrom-Json
        
        Write-Host ""
        Write-Success "API keys generated successfully!"
        Write-Host ""
        
        # Display keys
        Write-Host "---------------------------------------------------------" -ForegroundColor Cyan
        Write-Host "  DEVELOPMENT API KEY (60 req/min)" -ForegroundColor Yellow
        Write-Host "---------------------------------------------------------" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  $($keys.dev_key)" -ForegroundColor Green
        Write-Host ""
        Write-Host "---------------------------------------------------------" -ForegroundColor Cyan
        Write-Host "  PARTNER API KEY (600 req/min)" -ForegroundColor Yellow
        Write-Host "---------------------------------------------------------" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  $($keys.partner_key)" -ForegroundColor Green
        Write-Host ""
        
        # Save to file
        $keyFile = "dev-api-keys.txt"
        @"
# Development API Keys
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# WARNING: These are for development only. In-memory storage, resets on server restart.

# API Key Tier (60 requests/minute)
DEV_KEY=$($keys.dev_key)

# Partner Tier (600 requests/minute)
PARTNER_KEY=$($keys.partner_key)

# Usage Example (PowerShell):
# `$headers = @{"Authorization" = "Bearer $($keys.dev_key)"}
# Invoke-WebRequest -Uri "http://localhost:8000/metrics" -Headers `$headers

# Usage Example (curl):
# curl -H "Authorization: Bearer $($keys.dev_key)" http://localhost:8000/metrics
"@ | Out-File -FilePath $keyFile -Encoding UTF8
        
        Write-Success "Keys saved to: $keyFile"
        Write-Host ""

        Write-Section "Auto-Registration Enabled!"
        Write-Host ""
        Write-Success "Keys will automatically load when server starts"
        Write-Info "The server checks for dev-api-keys.txt at startup"
        Write-Info "No manual configuration needed - just start the server!"
        Write-Host ""
        Write-Step "Next Steps:"
        Write-Host "  1. Start server: .\quick-start.ps1 serve" -ForegroundColor Gray
        Write-Host "  2. Keys auto-register on startup" -ForegroundColor Gray
        Write-Host "  3. Use keys from dev-api-keys.txt" -ForegroundColor Gray
        Write-Host ""

        Write-Section "Usage Instructions"
        Write-Host ""
        Write-Step "Quick Test (PowerShell):"
        Write-Host ""
        Write-Host "  `$key = `"$($keys.dev_key)`"" -ForegroundColor Gray
        Write-Host '  $headers = @{"Authorization" = "Bearer $key"}' -ForegroundColor Gray
        Write-Host '  Invoke-WebRequest -Uri "http://localhost:8000/metrics" -Headers $headers' -ForegroundColor Gray
        Write-Host ""
        
        
        Write-Step "Test with higher rate limits:"
        Write-Host ""
        Write-Host '  1..70 | ForEach-Object {' -ForegroundColor Gray
        Write-Host '      Invoke-WebRequest -Uri "http://localhost:8000/health" -Headers $headers' -ForegroundColor Gray
        Write-Host '  }' -ForegroundColor Gray
        Write-Host ""
        
        Write-Info "Public tier: 10 req/min | API key tier: 60 req/min | Partner tier: 600 req/min"
        Write-Warning "Remember: Keys are in-memory only. Run this command again after server restart."
        
    } catch {
        Write-Error "Failed to generate keys: $($_.Exception.Message)"
    } finally {
        Remove-Item $tempFile -ErrorAction SilentlyContinue
    }
}

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

function Invoke-Tests {
    # T008: Determine which tests to run based on flags
    $runAll = -not ($Unit -or $Contract -or $Integration -or $Validation)
    
    # Determine title based on what's running
    if ($runAll) {
        Write-Header "Running Observatory Test Suite"
    } elseif ($Validation) {
        Write-Header "Running Validation Suite"
    } else {
        $types = @()
        if ($Unit) { $types += "Unit" }
        if ($Contract) { $types += "Contract" }
        if ($Integration) { $types += "Integration" }
        Write-Header "Running $($types -join ' + ') Tests"
    }
    
    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites not met. Run: .\quick-start.ps1 setup"
        return
    }
    
    # T009: Define pytest arguments based on verbosity
    $pytestArgs = @()
    if ($Detail) {
        $pytestArgs += @("-v", "--tb=short")
    } else {
        $pytestArgs += @("-q", "--tb=line")
    }
    
    # T010: Add coverage if requested
    if ($Coverage) {
        $pytestArgs += @("--cov=app", "--cov-report=term-missing")
        if ($Detail) {
            Write-Info "Coverage reporting enabled"
        }
    }

    # Track results
    $results = @{}
    $exitCodes = @{}
    $serverProcess = $null
    $needsServer = ($Integration -or $Validation -or $runAll)

    # Check for API keys, generate if missing (needed for validation/integration)
    $apiKeyFile = Join-Path $PSScriptRoot "dev-api-keys.txt"
    $partnerKey = $null

    if ($needsServer) {
        if (-not (Test-Path $apiKeyFile)) {
            Write-Step "Generating API keys for testing..."
            Invoke-GenerateKeys
            Write-Host ""
        }

        # Load partner key for testing (highest rate limits)
        if (Test-Path $apiKeyFile) {
            $content = Get-Content $apiKeyFile -Raw
            if ($content -match 'PARTNER_KEY=([^\r\n]+)') {
                $partnerKey = $Matches[1]
                Write-Info "Using PARTNER_KEY for testing (600 req/min limit)"
                Write-Host ""
            }
        }
    }

    # Start server if integration or validation tests will run
    if ($needsServer) {
        $serverProcess = Start-TestServer
        Write-Host ""
    }

    try {
        # T008: Run unit tests if requested
        if ($Unit -or $runAll) {
            $result = Invoke-TestSuite -TestType "unit" -TestPath "tests/unit/" -PytestArgs $pytestArgs
            $exitCodes['unit'] = $result.ExitCode
            $results['unit'] = $result.Passed
        }

        # T008: Run contract tests if requested
        if ($Contract -or $runAll) {
            $result = Invoke-TestSuite -TestType "contract" -TestPath "tests/contract/" -PytestArgs $pytestArgs
            $exitCodes['contract'] = $result.ExitCode
            $results['contract'] = $result.Passed
        }

        # T008: Run integration tests if requested
        if ($Integration -or $runAll) {
            # Set API key as environment variable for integration tests
            if ($partnerKey) {
                $env:TEST_API_KEY = $partnerKey
            }

            $result = Invoke-TestSuite -TestType "integration" -TestPath "tests/integration/" -PytestArgs $pytestArgs
            $exitCodes['integration'] = $result.ExitCode
            $results['integration'] = $result.Passed

            # Clean up environment variable
            if ($partnerKey) {
                Remove-Item Env:\TEST_API_KEY -ErrorAction SilentlyContinue
            }
        }

        # T008: Run validation suite if requested
        if ($Validation -or $runAll) {
            Write-Step "Running validation suite..."

            if (Test-Path ".\scripts\validation.ps1") {
                # Pass base URL and API key to validation script
                $validationArgs = @{
                    BaseUrl = $Script:Config.BaseUrl
                }

                if ($partnerKey) {
                    $validationArgs['ApiKey'] = $partnerKey
                }

                & ".\scripts\validation.ps1" @validationArgs
                $exitCodes['validation'] = $LASTEXITCODE
                $results['validation'] = ($LASTEXITCODE -eq 0)

                if ($LASTEXITCODE -eq 0) {
                    if (-not $Detail) {
                        Write-Success "Validation suite passed"
                    }
                } else {
                    Write-Warning "Validation suite failed (exit code: $LASTEXITCODE)"
                }
            } else {
                Write-Warning "Validation script not found at .\scripts\validation.ps1"
                $results['validation'] = $false
            }
            Write-Host ""
        }
    }
    finally {
        # Always stop the server if we started it
        if ($serverProcess) {
            Write-Host ""
            Stop-TestServer -ServerProcess $serverProcess
        }
    }

    # Summary
    if ($results.Count -gt 0) {
        Write-Section "Test Summary"
        
        # Show results in the order they were run
        $testOrder = @('unit', 'contract', 'integration', 'validation')
        $allPassed = $true
        $failedSuites = @()
        
        # Show results in execution order
        foreach ($suite in $testOrder) {
            if ($results.ContainsKey($suite)) {
                if ($results[$suite]) {
                    Write-Success "$($suite.Substring(0,1).ToUpper())$($suite.Substring(1)) tests passed"
                } else {
                    Write-Error "$($suite.Substring(0,1).ToUpper())$($suite.Substring(1)) tests failed"
                    $failedSuites += $suite
                    $allPassed = $false
                }
            }
        }
        
        Write-Host ""
        if ($allPassed) {
            Write-Success "All tests passed!"
        } else {
            Write-Warning "Failed test suites: $($failedSuites -join ', ')"
            Write-Info "Run with -Detail flag for more information"
        }
    }
}

function Invoke-QuickTests {
    param(
        [switch]$ReturnExitCode
    )

    Write-Header "Running Quick Test Suite"

    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites not met. Run: .\quick-start.ps1 setup"
        if ($ReturnExitCode) {
            # Set global variable and exit early
            $global:LastQuickTestExitCode = 1
            return
        }
        return
    }

    Write-Step "Running essential unit tests (fast subset)..."
    Write-Info "Testing: database, auth, rate limiting, and validation"
    Write-Host ""

    # In demo context, use quieter output to match demo style
    $quietMode = $ReturnExitCode
    $pytestArgs = if ($quietMode) { @("-q", "--tb=line") } else { @("-v", "--tb=short") }

    & "$($Script:Config.VenvPath)\python.exe" -m pytest `
        tests/unit/test_database.py `
        tests/unit/test_auth.py `
        tests/unit/test_ratelimit.py `
        tests/unit/test_validator.py `
        @pytestArgs

    $exitCode = $LASTEXITCODE

    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Success "Quick tests passed!"
        Write-Info "Run '.\quick-start.ps1 test' for full suite"
    } else {
        Write-Error "Some tests failed"
        Write-Info "See output above for details"
    }

    if ($ReturnExitCode) {
        # Store exit code in global variable instead of returning
        $global:LastQuickTestExitCode = $exitCode
    }
}

# ============================================================================
# SERVER FUNCTIONS
# ============================================================================

function Start-Server {
    param([bool]$Background = $false)

    Write-Header "Starting $($Script:Config.ServiceName)"

    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites not met. Run: .\quick-start.ps1 setup"
        return
    }

    Write-Result "Service" $Script:Config.ServiceName
    Write-Result "Version" $Script:Config.Version
    Write-Result "Base URL" $Script:Config.BaseUrl "Green"
    Write-Result "Port" $Port "Cyan"

    # T012: Check if clean logging is requested and available
    if ($Clean) {
        $cleanServerScript = Join-Path $PSScriptRoot "run_clean_server.py"
        if (-not (Test-Path $cleanServerScript)) {
            Write-Warning "Clean logging script not found (run_clean_server.py missing). Using standard mode."
            $Clean = $false
        } else {
            Write-Result "Logging" "Clean (no ANSI codes)" "Yellow"
        }
    }

    Write-Host ""

    Write-Step "Starting FastAPI server..."

    if ($NewWindow) {
        # Start server in new Windows Terminal window with Orion profile
        # T012: Use clean server script if -Clean flag is set
        $pythonExe = "$($Script:Config.VenvPath)\python.exe"
        if ($Clean) {
            $cmdCommand = "cd /d `"$PWD`" && `"$pythonExe`" run_clean_server.py $Port --reload"
        } else {
            $cmdCommand = "cd /d `"$PWD`" && `"$pythonExe`" -m uvicorn app.main:app --host 0.0.0.0 --port $Port --reload"
        }

        # Use Windows Terminal with Orion profile
        Start-Process wt.exe -ArgumentList "-p", "Orion", "cmd", "/k", $cmdCommand
        Write-Success "Server starting in new Windows Terminal (Orion profile)"
        
        if ($Clean) {
            Write-Info "Using clean logging (ANSI-free output)"
        }
        Write-Info "Waiting for server to initialize..."
        Start-Sleep -Seconds 3

        # Verify server is responding
        try {
            $null = Invoke-WebRequest -Uri "$($Script:Config.BaseUrl)/health" -Method GET -ErrorAction Stop -TimeoutSec 5
            Write-Success "Server is ready at $($Script:Config.BaseUrl)"
        } catch {
            Write-Warning "Server may still be starting. Check the server window."
        }
    }
    elseif ($Background) {
        # T012: Support clean logging in background mode
        if ($Clean) {
            Start-Job -ScriptBlock {
                param($VenvPath, $Port, $ScriptRoot)
                & "$VenvPath\python.exe" "$ScriptRoot\run_clean_server.py" $Port
            } -ArgumentList $Script:Config.VenvPath, $Port, $PSScriptRoot
        } else {
            Start-Job -ScriptBlock {
                param($VenvPath, $Port)
                & "$VenvPath\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port $Port
            } -ArgumentList $Script:Config.VenvPath, $Port
        }

        Write-Host ""
        Write-Success "Server started in background"
        if ($Clean) {
            Write-Info "Using clean logging (ANSI-free output)"
        }
        Start-Sleep -Seconds 2
    } else {
        # T012: Support clean logging in foreground mode
        Write-Info "Press Ctrl+C to stop the server"
        if ($Clean) {
            Write-Info "Using clean logging (no ANSI escape codes)"
        }
        Write-Host ""

        if ($Clean) {
            & "$($Script:Config.VenvPath)\python.exe" run_clean_server.py $Port --reload
        } else {
            & "$($Script:Config.VenvPath)\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port $Port --reload
        }
    }
}

# ============================================================================
# API TESTING FUNCTIONS
# ============================================================================

function Test-HealthEndpoint {
    Write-Section "Testing Health Endpoint"

    try {
        $response = Invoke-WebRequest -Uri "$($Script:Config.BaseUrl)/health" -Method GET -ErrorAction Stop
        $data = $response.Content | ConvertFrom-Json

        Write-ApiCall "GET" "/health" $response.StatusCode
        Write-Result "Status" $data.status "Green"
        Write-Result "Version" $data.version
        Write-Result "Timestamp" $data.timestamp

        return $true
    } catch {
        Write-ApiCall "GET" "/health" "ERROR"
        Write-Error "Failed to connect to server"
        Write-Info "Is the server running? Try: .\quick-start.ps1 serve"
        return $false
    }
}

function Test-AnalyzeEndpoint {
    Write-Section "Testing Analysis Endpoint"

    $conversationText = @"
Human: What is the meaning of life?
AI: The meaning of life is a profound philosophical question. Many find meaning through relationships, personal growth, and contributing to something larger than themselves.
Human: That's quite philosophical. Can you be more specific?
AI: Certainly. From a practical perspective, meaning often comes from: pursuing your passions, helping others, continuous learning, and finding purpose in your daily actions.
"@
    
    $body = @{
        conversation_text = $conversationText
        options = @{
            pattern_types = @("dialectic", "sentiment")
            include_insights = $true
        }
    } | ConvertTo-Json
    
    Write-Step "Sending analysis request..."
    Write-Info "Conversation length: $($conversationText.Length) characters"
    Write-Host ""
    
    try {
        $response = Invoke-WebRequest -Uri "$($Script:Config.BaseUrl)/api/v1/analyze" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body `
            -ErrorAction Stop
        
        $data = $response.Content | ConvertFrom-Json
        
        Write-ApiCall "POST" "/api/v1/analyze" $response.StatusCode
        Write-Result "Analysis ID" $data.id "Green"
        Write-Result "Status" $data.status "Yellow"
        Write-Result "Created" $data.created_at
        
        Write-Host ""
        Write-Step "Checking analysis result..."
        Start-Sleep -Seconds 2
        
        try {
            $resultResponse = Invoke-WebRequest -Uri "$($Script:Config.BaseUrl)/api/v1/analyze/$($data.id)" `
                -Method GET `
                -ErrorAction Stop
            
            $resultData = $resultResponse.Content | ConvertFrom-Json
            
            Write-ApiCall "GET" "/api/v1/analyze/$($data.id)" $resultResponse.StatusCode
            Write-Result "Final Status" $resultData.status "Green"
            
            if ($resultData.confidence_score) {
                Write-Result "Confidence" "$([math]::Round($resultData.confidence_score, 2))" "Cyan"
            }
            
            if ($resultData.processing_time) {
                Write-Result "Processing Time" "$([math]::Round($resultData.processing_time, 2))s" "Magenta"
            }
            
        } catch {
            Write-Warning "Analysis may still be processing"
        }
        
    } catch {
        Write-ApiCall "POST" "/api/v1/analyze" "ERROR"
        Write-Error $_.Exception.Message
    }
}

function Test-RateLimiting {
    Write-Section "Testing Rate Limiting"

    Write-Step "Making rapid requests to test rate limiter..."
    Write-Info "Public tier: 10 requests/minute total (including previous health/analyze requests)"
    Write-Info "Expect some requests to be rate limited (429) if limit exceeded"
    Write-Host ""

    $successCount = 0
    $rateLimitedCount = 0

    for ($i = 1; $i -le 12; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "$($Script:Config.BaseUrl)/health" -Method GET -ErrorAction Stop
            $successCount++

            if ($response.Headers["X-RateLimit-Remaining"]) {
                $remaining = $response.Headers["X-RateLimit-Remaining"]
                Write-Host "  Request $i`: " -ForegroundColor Gray -NoNewline
                Write-Host "[OK] OK" -ForegroundColor Green -NoNewline
                Write-Host " (Remaining: $remaining)" -ForegroundColor Cyan
            }
        } catch {
            if ($_.Exception.Response.StatusCode -eq 429) {
                $rateLimitedCount++
                Write-Host "  Request $i`: " -ForegroundColor Gray -NoNewline
                Write-Host "[FAIL] 429 Rate Limited" -ForegroundColor Yellow
            }
        }

        Start-Sleep -Milliseconds 100
    }

    Write-Host ""
    Write-Result "Successful Requests" $successCount "Green"
    Write-Result "Rate Limited" $rateLimitedCount "Yellow"

    if ($rateLimitedCount -gt 0) {
        Write-Host ""
        Write-Success "Rate limiting is working correctly!"
    }
}

function Test-AuthenticationMetrics {
    Write-Section "Testing Authentication & Metrics"

    Write-Info "Testing unauthenticated access to /metrics..."
    try {
        Invoke-WebRequest -Uri "$($Script:Config.BaseUrl)/metrics" -Method GET -ErrorAction Stop | Out-Null
        Write-Error "Unexpected: Metrics accessible without auth"
    } catch {
        if ($_.Exception.Response.StatusCode -eq 401) {
            Write-ApiCall "GET" "/metrics" "401"
            Write-Success "Authentication required (as expected)"
        }
    }

    Write-Host ""

    # Check for API key and demonstrate authenticated access
    $apiKeyFile = Join-Path $PSScriptRoot "dev-api-keys.txt"
    if (Test-Path $apiKeyFile) {
        $content = Get-Content $apiKeyFile -Raw
        if ($content -match 'DEV_KEY=([^\r\n]+)') {
            $apiKey = $Matches[1]
            Write-Step "Testing authenticated access with DEV_KEY..."

            try {
                $headers = @{"Authorization" = "Bearer $apiKey"}
                $response = Invoke-WebRequest -Uri "$($Script:Config.BaseUrl)/metrics" -Headers $headers -ErrorAction Stop
                $data = $response.Content | ConvertFrom-Json

                Write-ApiCall "GET" "/metrics" $response.StatusCode
                Write-Success "Authenticated access successful!"
                Write-Result "Tier" $data.tier "Cyan"
                Write-Result "Total Analyses" $data.database_stats.total_analyses "Cyan"
                Write-Result "Completed" $data.database_stats.completed_analyses "Cyan"
                if ($data.database_stats.avg_processing_time -gt 0) {
                    Write-Result "Avg Processing Time" "$([math]::Round($data.database_stats.avg_processing_time, 2))s" "Cyan"
                }
            } catch {
                Write-Warning "Could not fetch metrics: $($_.Exception.Message)"
            }
        }
    } else {
        Write-Info "To test with API key, generate keys first:"
        Write-Host '  .\quick-start.ps1 keys' -ForegroundColor DarkGray
    }
}

# ============================================================================
# DEMO FUNCTION
# ============================================================================

function Invoke-Demo {
    Write-Host ""
    Write-Header "$($Script:Config.ServiceName) - Full Demo"
    
    # Get test counts for info
    $unitCount = (& "$($Script:Config.VenvPath)\python.exe" -m pytest tests/unit/ --collect-only -q 2>&1 | Select-String "(\d+) test" | ForEach-Object { $_.Matches.Groups[1].Value })
    $contractCount = (& "$($Script:Config.VenvPath)\python.exe" -m pytest tests/contract/ --collect-only -q 2>&1 | Select-String "(\d+) test" | ForEach-Object { $_.Matches.Groups[1].Value })
    $integCount = (& "$($Script:Config.VenvPath)\python.exe" -m pytest tests/integration/ --collect-only -q 2>&1 | Select-String "(\d+) test" | ForEach-Object { $_.Matches.Groups[1].Value })
    $totalTests = [int]$unitCount + [int]$contractCount + [int]$integCount
    
    Write-Info "This demo will:"
    Write-Host "  1. Run quick tests (essential unit tests)" -ForegroundColor Gray
    Write-Host "  2. Start the server in background" -ForegroundColor Gray
    Write-Host "  3. Test all API endpoints" -ForegroundColor Gray
    Write-Host "  4. Show rate limiting in action" -ForegroundColor Gray
    Write-Host "  5. Clean up" -ForegroundColor Gray
    Write-Host ""
    Write-Info "Full test suite: $totalTests tests ($unitCount unit + $contractCount contract + $integCount integration)"
    Write-Info "Run '.\quick-start.ps1 test' for complete test coverage"
    Write-Host ""
    
    Read-Host "Press Enter to continue"

    # Quick tests - use global variable to avoid PowerShell output capture issues
    Invoke-QuickTests -ReturnExitCode
    $testResult = $global:LastQuickTestExitCode

    if ($testResult -ne 0) {
        Write-Host ""
        Write-Warning "Quick tests failed. Continuing with demo anyway..."
        Start-Sleep -Seconds 2
    }

    Write-Host ""

    # Check for API keys, generate if missing
    $apiKeyFile = Join-Path $PSScriptRoot "dev-api-keys.txt"
    if (-not (Test-Path $apiKeyFile)) {
        Write-Step "No API keys found - generating development keys..."
        Invoke-GenerateKeys
        Write-Host ""
    }

    # Start server
    Start-Server -Background $true

    Write-Host ""
    Write-Step "Waiting for server to start..."
    Start-Sleep -Seconds 3

    # Test endpoints
    $serverRunning = Test-HealthEndpoint
    
    if ($serverRunning) {
        Write-Host ""
        Test-AnalyzeEndpoint
        
        Write-Host ""
        Test-RateLimiting
        
        Write-Host ""
        Test-AuthenticationMetrics
    }
    
    # Cleanup
    Write-Host ""
    Write-Section "Demo Complete"
    Write-Step "Stopping background server..."
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    Write-Success "Server stopped"
    Write-Success "Demo completed successfully!"
}

# ============================================================================
# VALIDATION FUNCTION
# ============================================================================

function Invoke-Validation {
    Write-Header "Running Automated Validation Suite"
    
    # T011: Deprecation warning
    Write-Warning "The 'validate' action is deprecated. Use 'test -Validation' instead."
    Write-Info "Example: .\quick-start.ps1 test -Validation"
    Write-Host ""

    # Check if validation script exists
    $validationScript = Join-Path $PSScriptRoot "scripts\validation.ps1"

    if (-not (Test-Path $validationScript)) {
        Write-Error "Validation script not found at: $validationScript"
        return
    }

    # Check if server is running
    Write-Step "Checking server status..."
    $serverProcess = $null
    try {
        $null = Invoke-WebRequest -Uri "$($Script:Config.BaseUrl)/health" -Method GET -ErrorAction Stop -TimeoutSec 2
        Write-Success "Server is running at $($Script:Config.BaseUrl)"
        $serverWasRunning = $true
    } catch {
        Write-Info "Server not running. Starting server for validation..."
        $serverWasRunning = $false

        # Check if port is already in use
        $portInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($portInUse) {
            Write-Error "Port $Port is already in use by another process"
            Write-Info "Close the other process or use a different port: .\quick-start.ps1 validate -Port 8001"
            return
        }

        # Start server as background process (not in new window)
        Write-Info "Starting validation server in background..."
        $serverProcess = Start-Process -FilePath "$($Script:Config.VenvPath)\python.exe" `
            -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", $Port `
            -PassThru -NoNewWindow -RedirectStandardOutput "nul" -RedirectStandardError "nul"

        Write-Info "Waiting for server to start (this can take up to 45 seconds)..."
        $retries = 0
        $maxRetries = 45

        while ($retries -lt $maxRetries) {
            Start-Sleep -Milliseconds 1000
            if ($retries % 5 -eq 0 -and $retries -gt 0) {
                Write-Host " ${retries}s" -ForegroundColor DarkGray -NoNewline
            } else {
                Write-Host "." -NoNewline -ForegroundColor Gray
            }

            try {
                $testResponse = Invoke-WebRequest -Uri "$($Script:Config.BaseUrl)/health" -Method GET -ErrorAction Stop -TimeoutSec 3
                Write-Host ""
                Write-Success "Server is ready! (started in ${retries}s)"
                break
            } catch {
                $retries++
                if ($retries -eq $maxRetries) {
                    Write-Host ""
                    Write-Error "Server failed to start after $maxRetries seconds"
                    Write-Warning "Check the server window for error messages"
                    Write-Info "Common issues: Port already in use, missing dependencies"
                    return
                }
            }
        }
    }

    Write-Host ""

    # Check for API key in dev-api-keys.txt
    $apiKeyFile = Join-Path $PSScriptRoot "dev-api-keys.txt"
    $apiKey = $null

    if (Test-Path $apiKeyFile) {
        $content = Get-Content $apiKeyFile -Raw
        if ($content -match 'DEV_KEY=([^\r\n]+)') {
            $apiKey = $Matches[1]
            Write-Success "Using API key from dev-api-keys.txt"
        }
    } else {
        Write-Warning "No API keys found - some tests will be skipped"
        Write-Info "Generate keys with: .\quick-start.ps1 keys"
    }

    # Run validation script
    Write-Section "Executing Validation Tests"
    Write-Host ""

    $validationArgs = @(
        "-BaseUrl", $Script:Config.BaseUrl
    )

    if ($apiKey) {
        $validationArgs += "-ApiKey", $apiKey
    }

    & $validationScript @validationArgs

    $exitCode = $LASTEXITCODE

    # Cleanup: Stop validation server if we started it
    if ($serverProcess) {
        Write-Host ""
        Write-Step "Stopping validation server..."
        try {
            Stop-Process -Id $serverProcess.Id -Force -ErrorAction Stop
            Write-Success "Validation server stopped"
        } catch {
            Write-Warning "Could not stop server process. You may need to close it manually."
        }
    }

    Write-Host ""

    if ($exitCode -eq 0) {
        Write-Success "Validation passed!"
    } else {
        Write-Warning "Validation completed with failures"
    }

    exit $exitCode
}

# ============================================================================
# CODE QUALITY ACTIONS (Feature 002 - T013-T015)
# ============================================================================

function Invoke-Lint {
    <#
    .SYNOPSIS
        Run code linter using ruff
    .DESCRIPTION
        Executes ruff check on the codebase. In default mode, suppresses output
        unless issues are found. In Detail mode, shows full linter output.
    #>
    Write-Header "Running Code Linter"

    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites not met. Run: .\quick-start.ps1 setup"
        return
    }

    $pythonExe = Get-PythonExePath

    Write-Step "Running ruff check..."

    # T013: Apply verbosity control to linter
    $command = { & $pythonExe -m ruff check . }

    try {
        Invoke-CommandWithVerbosity -Command $command -SuccessMessage "No linting issues found" -ErrorMessage "Linting found issues"
    } catch {
        # Linting failed - error already displayed by helper
        exit 1
    }
}

function Invoke-Format {
    <#
    .SYNOPSIS
        Format code using ruff
    .DESCRIPTION
        Executes ruff format on the codebase. Shows summary of files changed
        in default mode, full output in Detail mode.
    #>
    Write-Header "Formatting Code"

    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites not met. Run: .\quick-start.ps1 setup"
        return
    }

    $pythonExe = Get-PythonExePath

    Write-Step "Running ruff format..."

    # T014: Format with verbosity control
    if ($Detail) {
        # Detail mode: Show full formatting output
        & $pythonExe -m ruff format .
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            Write-Success "Code formatted successfully"
        } else {
            Write-Error "Formatting failed (exit code: $exitCode)"
            exit 1
        }
    } else {
        # Default mode: Show summary only
        $output = & $pythonExe -m ruff format . 2>&1
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            # Extract summary line (e.g., "12 files reformatted, 45 files left unchanged")
            $summary = $output | Where-Object { $_ -match "files?" } | Select-Object -Last 1

            if ($summary) {
                Write-Success $summary.ToString().Trim()
            } else {
                Write-Success "Code formatted successfully"
            }
        } else {
            # Formatting failed - show output
            Write-Host $output -ForegroundColor Red
            Write-Error "Formatting failed (exit code: $exitCode)"
            exit 1
        }
    }
}

function Invoke-Check {
    <#
    .SYNOPSIS
        Run all code quality checks
    .DESCRIPTION
        Executes both linting (ruff check) and type checking (mypy) on the codebase.
        Reports results for each check and overall status.
    #>
    Write-Header "Running Code Quality Checks"

    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites not met. Run: .\quick-start.ps1 setup"
        return
    }

    $pythonExe = Get-PythonExePath
    $allPassed = $true

    # T015: Run linter
    Write-Section "Running Linter (ruff check)"
    Write-Step "Checking code style..."

    & $pythonExe -m ruff check .
    $lintExitCode = $LASTEXITCODE

    Write-Host ""
    if ($lintExitCode -eq 0) {
        Write-Success "Linting passed"
    } else {
        Write-Error "Linting failed"
        $allPassed = $false
    }

    # T015: Run type checker
    Write-Host ""
    Write-Section "Running Type Checker (mypy)"
    Write-Step "Checking type annotations..."

    & $pythonExe -m mypy app/
    $mypyExitCode = $LASTEXITCODE

    Write-Host ""
    if ($mypyExitCode -eq 0) {
        Write-Success "Type checking passed"
    } else {
        Write-Error "Type checking failed"
        $allPassed = $false
    }

    # Summary
    Write-Host ""
    Write-Section "Quality Check Summary"

    if ($allPassed) {
        Write-Success "All quality checks passed!"
        exit 0
    } else {
        Write-Warning "Some quality checks failed"
        Write-Info "Review the output above for details"
        exit 1
    }
}

# ============================================================================
# HELP FUNCTION
# ============================================================================

function Show-Help {
    Write-Host ""
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host "   Atrium Observatory Quick Start" -ForegroundColor White
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\quick-start.ps1 [action] [options]" -ForegroundColor White
    Write-Host ""
    
    Write-Host "ACTIONS:" -ForegroundColor Yellow
    Write-Host "  setup      " -ForegroundColor Green -NoNewline
    Write-Host "  Set up virtual environment and install dependencies"
    Write-Host "  test       " -ForegroundColor Green -NoNewline
    Write-Host "  Run the full test suite (unit + contract + integration)"
    Write-Host "  serve      " -ForegroundColor Green -NoNewline
    Write-Host "  Start the development server"
    Write-Host "  demo       " -ForegroundColor Green -NoNewline
    Write-Host "  Run a full demonstration (quick tests + server + API calls)"
    Write-Host "  health     " -ForegroundColor Green -NoNewline
    Write-Host "  Test the health endpoint"
    Write-Host "  analyze    " -ForegroundColor Green -NoNewline
    Write-Host "  Test the analysis endpoint with sample data"
    Write-Host "  keys       " -ForegroundColor Green -NoNewline
    Write-Host "  Generate development API keys"
    Write-Host "  validate   " -ForegroundColor Green -NoNewline
    Write-Host "  Run automated validation suite (starts server if needed)"
    Write-Host "  lint       " -ForegroundColor Green -NoNewline
    Write-Host "  Run code linter (ruff check)"
    Write-Host "  format     " -ForegroundColor Green -NoNewline
    Write-Host "  Format code with ruff"
    Write-Host "  check      " -ForegroundColor Green -NoNewline
    Write-Host "  Run all code quality checks (lint + type check)"
    Write-Host "  clean      " -ForegroundColor Green -NoNewline
    Write-Host "  Remove virtual environment and caches"
    Write-Host "  help       " -ForegroundColor Green -NoNewline
    Write-Host "  Show this help message"
    Write-Host ""

    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "  -Port <number>  " -ForegroundColor Cyan -NoNewline
    Write-Host "  Specify server port (default: 8000)"
    Write-Host "  -NewWindow      " -ForegroundColor Cyan -NoNewline
    Write-Host "  Start server in new PowerShell window (for 'serve' action)"
    Write-Host "  -Detail         " -ForegroundColor Cyan -NoNewline
    Write-Host "  Enable detailed output with progress steps"
    Write-Host ""
    Write-Host "  Test Filtering:" -ForegroundColor Yellow
    Write-Host "  -Unit           " -ForegroundColor Cyan -NoNewline
    Write-Host "  Run only unit tests (fast, no external dependencies)"
    Write-Host "  -Contract       " -ForegroundColor Cyan -NoNewline
    Write-Host "  Run only contract tests (API contract validation)"
    Write-Host "  -Integration    " -ForegroundColor Cyan -NoNewline
    Write-Host "  Run only integration tests (requires server/services)"
    Write-Host "  -Validation     " -ForegroundColor Cyan -NoNewline
    Write-Host "  Run only validation suite (automated API tests)"
    Write-Host "  -Coverage       " -ForegroundColor Cyan -NoNewline
    Write-Host "  Generate code coverage report (works with any test type)"
    Write-Host ""
    
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\quick-start.ps1 setup" -ForegroundColor White
    Write-Host "    Initialize the development environment" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\quick-start.ps1 test" -ForegroundColor White
    Write-Host "    Run all tests (unit + contract + integration + validation)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\quick-start.ps1 test -Unit" -ForegroundColor White
    Write-Host "    Run only unit tests (fast, ~2 seconds)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\quick-start.ps1 test -Unit -Coverage" -ForegroundColor White
    Write-Host "    Run unit tests with code coverage report" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\quick-start.ps1 test -Detail" -ForegroundColor White
    Write-Host "    Run all tests with verbose output" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\quick-start.ps1 serve -Port 8001" -ForegroundColor White
    Write-Host "    Start server on port 8001" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\quick-start.ps1 keys" -ForegroundColor White
    Write-Host "    Generate API keys for development" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\quick-start.ps1 demo" -ForegroundColor White
    Write-Host "    Run complete demo with all features" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\quick-start.ps1 serve -NewWindow" -ForegroundColor White
    Write-Host "    Start server in new window, script continues" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\quick-start.ps1 validate" -ForegroundColor White
    Write-Host "    Run automated validation (auto-starts server if needed)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Code Quality Examples:" -ForegroundColor DarkGray
    Write-Host "  .\quick-start.ps1 lint" -ForegroundColor White
    Write-Host "    Check code style (fast, read-only)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\quick-start.ps1 format" -ForegroundColor White
    Write-Host "    Auto-format all code with ruff" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\quick-start.ps1 check" -ForegroundColor White
    Write-Host "    Pre-commit checks (lint + type check)" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "MORE INFO:" -ForegroundColor Yellow
    Write-Host "  Docs:  " -ForegroundColor Cyan -NoNewline
    Write-Host "http://localhost:$Port/docs" -ForegroundColor White
    Write-Host "  API:   " -ForegroundColor Cyan -NoNewline
    Write-Host "http://localhost:$Port/api/v1/" -ForegroundColor White
    Write-Host "  README:" -ForegroundColor Cyan -NoNewline
    Write-Host " ./README.md" -ForegroundColor White
    Write-Host ""
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

switch ($Action.ToLower()) {
    'setup' {
        Invoke-Setup
    }
    'test' {
        Invoke-Tests
    }
    'serve' {
        Start-Server -Background $false
    }
    'keys' {
        Invoke-KeyManagement
    }
    'demo' {
        Invoke-Demo
    }
    'health' {
        if (Test-HealthEndpoint) {
            Write-Host ""
            Write-Success "Health check passed!"
        }
    }
    'analyze' {
        Test-AnalyzeEndpoint
    }
    'validate' {
        Invoke-Validation
    }
    'lint' {
        Invoke-Lint
    }
    'format' {
        Invoke-Format
    }
    'check' {
        Invoke-Check
    }
    'clean' {
        Invoke-Clean
    }
    'help' {
        Show-Help
    }
    default {
        Show-Help
    }
}

Write-Host ""
