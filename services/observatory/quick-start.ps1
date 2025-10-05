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
    [ValidateSet('test', 'serve', 'demo', 'health', 'analyze', 'keys', 'setup', 'clean', 'validate', 'help')]
    [string]$Action = 'help',

    [Parameter()]
    [int]$Port = 8000,

    [Parameter()]
    [switch]$Detail,

    [Parameter()]
    [switch]$NewWindow
)

# ============================================================================
# CONFIGURATION
# ============================================================================

$Script:Config = @{
    ServiceName = "Atrium Observatory"
    Version     = "0.1.0"
    BaseUrl     = "http://localhost:$Port"
    VenvPath    = ".venv\Scripts"
    DataPath    = "data"
}

# ============================================================================
# COLOR SCHEME
# ============================================================================

function Write-Header {
    param([string]$Text)
    Write-Host ""
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
    Write-Host "-> " -ForegroundColor Magenta -NoNewline
    Write-Host $Text -ForegroundColor White
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
    Write-Host ""
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
    
    Write-Step "Creating virtual environment with uv..."
    uv venv
    
    Write-Step "Installing dependencies..."
    uv pip install -e .
    
    Write-Step "Installing development dependencies..."
    uv pip install -e ".[dev]"
    
    Write-Success "Setup complete!"
    Write-Info "Run '.\quick-start.ps1 test' to verify installation"
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
    Write-Header "Running Observatory Test Suite"
    
    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites not met. Run: .\quick-start.ps1 setup"
        return
    }
    
    # Get test counts dynamically
    Write-Step "Collecting test information..."
    $unitCount = (& "$($Script:Config.VenvPath)\python.exe" -m pytest tests/unit/ --collect-only -q 2>&1 | Select-String "(\d+) test" | ForEach-Object { $_.Matches.Groups[1].Value })
    $contractCount = (& "$($Script:Config.VenvPath)\python.exe" -m pytest tests/contract/ --collect-only -q 2>&1 | Select-String "(\d+) test" | ForEach-Object { $_.Matches.Groups[1].Value })
    $integCount = (& "$($Script:Config.VenvPath)\python.exe" -m pytest tests/integration/ --collect-only -q 2>&1 | Select-String "(\d+) test" | ForEach-Object { $_.Matches.Groups[1].Value })
    
    Write-Section "Unit Tests ($unitCount tests)"
    Write-Step "Running unit tests..."
    & "$($Script:Config.VenvPath)\python.exe" -m pytest tests/unit/ -v --tb=short
    $unitExitCode = $LASTEXITCODE
    
    Write-Host ""
    Write-Section "Contract Tests ($contractCount tests)"
    Write-Step "Running contract tests..."
    & "$($Script:Config.VenvPath)\python.exe" -m pytest tests/contract/ -v --tb=short
    $contractExitCode = $LASTEXITCODE
    
    Write-Host ""
    Write-Section "Integration Tests ($integCount tests)"
    Write-Step "Running integration tests..."
    & "$($Script:Config.VenvPath)\python.exe" -m pytest tests/integration/ -v --tb=short
    $integExitCode = $LASTEXITCODE
    
    Write-Host ""
    Write-Section "Test Summary"
    
    $totalTests = [int]$unitCount + [int]$contractCount + [int]$integCount
    
    if ($unitExitCode -eq 0) {
        Write-Success "Unit tests passed ($unitCount/$unitCount)"
    } else {
        Write-Error "Unit tests failed (exit code: $unitExitCode)"
    }
    
    if ($contractExitCode -eq 0) {
        Write-Success "Contract tests passed ($contractCount/$contractCount)"
    } else {
        Write-Error "Contract tests failed (exit code: $contractExitCode)"
    }
    
    if ($integExitCode -eq 0) {
        Write-Success "Integration tests passed ($integCount/$integCount)"
    } else {
        Write-Warning "Integration tests failed (exit code: $integExitCode)"
        Write-Info "Some integration tests may require the server running"
    }
    
    Write-Host ""
    if ($unitExitCode -eq 0 -and $contractExitCode -eq 0 -and $integExitCode -eq 0) {
        Write-Success "All $totalTests tests passed! "
    } else {
        $failedSuites = @()
        if ($unitExitCode -ne 0) { $failedSuites += "unit" }
        if ($contractExitCode -ne 0) { $failedSuites += "contract" }
        if ($integExitCode -ne 0) { $failedSuites += "integration" }
        Write-Warning "Failed test suites: $($failedSuites -join ', ')"
    }
}

function Invoke-QuickTests {
    Write-Header "Running Quick Test Suite"
    
    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites not met. Run: .\quick-start.ps1 setup"
        return
    }
    
    Write-Step "Running essential unit tests (fast subset)..."
    Write-Info "Testing: database, auth, rate limiting, and validation"
    Write-Host ""
    
    & "$($Script:Config.VenvPath)\python.exe" -m pytest `
        tests/unit/test_database.py `
        tests/unit/test_auth.py `
        tests/unit/test_ratelimit.py `
        tests/unit/test_validator.py `
        -v --tb=short
    
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Success "Quick tests passed! [OK]"
        Write-Info "Run '.\quick-start.ps1 test' for full suite"
    } else {
        Write-Error "Some tests failed"
        Write-Info "See output above for details"
    }
    
    return $exitCode
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
    Write-Host ""
    
    Write-Step "Starting FastAPI server..."

    if ($NewWindow) {
        # Start server in new PowerShell window (prefer PowerShell Core)
        $pwsh = if (Get-Command pwsh -ErrorAction SilentlyContinue) { "pwsh" } else { "powershell" }
        $serverScript = "cd '$PWD'; & '$($Script:Config.VenvPath)\python.exe' -m uvicorn app.main:app --host 0.0.0.0 --port $Port --reload"
        Start-Process $pwsh -ArgumentList "-NoExit", "-Command", $serverScript

        Write-Success "Server starting in new $pwsh window"
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
        Start-Job -ScriptBlock {
            param($VenvPath, $Port)
            & "$VenvPath\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port $Port
        } -ArgumentList $Script:Config.VenvPath, $Port

        Write-Success "Server started in background"
        Start-Sleep -Seconds 2
    } else {
        Write-Info "Press Ctrl+C to stop the server"
        Write-Host ""
        & "$($Script:Config.VenvPath)\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port $Port --reload
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
    Write-Info "Public tier allows 10 requests/minute"
    
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
        Write-Success "Rate limiting is working correctly!"
    }
}

function Test-AuthenticationMetrics {
    Write-Section "Testing Authentication & Metrics"
    
    Write-Step "Testing unauthenticated access to /metrics..."
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
    Write-Info "To test with API key, register a key and use:"
    Write-Host '  $headers = @{"Authorization" = "Bearer YOUR_API_KEY"}' -ForegroundColor DarkGray
    Write-Host '  Invoke-WebRequest -Uri "$baseUrl/metrics" -Headers $headers' -ForegroundColor DarkGray
}

# ============================================================================
# DEMO FUNCTION
# ============================================================================

function Invoke-Demo {
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
    
    # Quick tests
    $testResult = Invoke-QuickTests
    if ($testResult -ne 0) {
        Write-Host ""
        Write-Warning "Quick tests failed. Continuing with demo anyway..."
        Write-Host ""
        Start-Sleep -Seconds 2
    }
    
    # Start server
    Write-Host ""
    Start-Server -Background $true
    
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
    
    Write-Host ""
    Write-Success "Demo completed successfully! "
}

# ============================================================================
# VALIDATION FUNCTION
# ============================================================================

function Invoke-Validation {
    Write-Header "Running Automated Validation Suite"

    # Check if validation script exists
    $validationScript = Join-Path $PSScriptRoot "scripts\validation.ps1"

    if (-not (Test-Path $validationScript)) {
        Write-Error "Validation script not found at: $validationScript"
        return
    }

    # Check if server is running
    Write-Step "Checking server status..."
    try {
        $null = Invoke-WebRequest -Uri "$($Script:Config.BaseUrl)/health" -Method GET -ErrorAction Stop -TimeoutSec 2
        Write-Success "Server is running at $($Script:Config.BaseUrl)"
        $serverWasRunning = $true
    } catch {
        Write-Info "Server not running. Starting server in new window..."
        $serverWasRunning = $false

        # Start server in new window (prefer PowerShell Core for better Unicode support)
        $pwsh = if (Get-Command pwsh -ErrorAction SilentlyContinue) { "pwsh" } else { "powershell" }
        Write-Info "Using: $pwsh"
        
        $serverScript = "cd '$PWD'; & '$($Script:Config.VenvPath)\python.exe' -m uvicorn app.main:app --host 0.0.0.0 --port $Port"
        Start-Process $pwsh -ArgumentList "-NoExit", "-Command", $serverScript

        Write-Info "Waiting for server to start (this can take up to 30 seconds)..."
        $retries = 0
        $maxRetries = 30  # Increased from 10 to 30 seconds

        while ($retries -lt $maxRetries) {
            Start-Sleep -Seconds 1
            Write-Host "." -NoNewline -ForegroundColor Gray
            try {
                $null = Invoke-WebRequest -Uri "$($Script:Config.BaseUrl)/health" -Method GET -ErrorAction Stop -TimeoutSec 2
                Write-Host ""
                Write-Success "Server is ready!"
                break
            } catch {
                $retries++
                if ($retries -eq $maxRetries) {
                    Write-Host ""
                    Write-Error "Server failed to start after $maxRetries seconds"
                    Write-Warning "Check the server window for error messages"
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
            Write-Info "Found API key in dev-api-keys.txt"
        }
    }

    # Run validation script
    Write-Section "Executing Validation Tests"
    Write-Host ""

    $args = @(
        "-BaseUrl", $Script:Config.BaseUrl
    )

    if ($apiKey) {
        $args += "-ApiKey", $apiKey
    }

    & $validationScript @args

    $exitCode = $LASTEXITCODE

    Write-Host ""

    if (-not $serverWasRunning) {
        Write-Info "Server was started for validation. You can close the server window when done."
    }

    exit $exitCode
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
    Write-Host "  Enable detailed output"
    Write-Host ""
    
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\quick-start.ps1 setup" -ForegroundColor White
    Write-Host "    Initialize the development environment" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\quick-start.ps1 test" -ForegroundColor White
    Write-Host "    Run all tests" -ForegroundColor Gray
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
