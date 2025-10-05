#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated validation script for Observatory service

.DESCRIPTION
    Runs comprehensive automated tests against a running Observatory instance.
    Validates endpoints, authentication, rate limiting, and analysis functionality.

.PARAMETER BaseUrl
    Base URL of the Observatory service (default: http://localhost:8000)

.PARAMETER ApiKey
    Optional API key for authenticated tests

.PARAMETER Quick
    Run only essential validation checks (fast mode)

.EXAMPLE
    .\scripts\validation.ps1
    Run full validation suite against local server

.EXAMPLE
    .\scripts\validation.ps1 -Quick
    Run quick validation checks only

.EXAMPLE
    .\scripts\validation.ps1 -ApiKey "dev_YOUR_KEY" -BaseUrl "http://localhost:8001"
    Validate with custom API key and port
#>

param(
    [Parameter()]
    [string]$BaseUrl = "http://localhost:8000",

    [Parameter()]
    [string]$ApiKey = "",

    [Parameter()]
    [switch]$Quick
)

# ============================================================================
# CONFIGURATION
# ============================================================================

$Script:Config = @{
    BaseUrl = $BaseUrl
    ApiKey = $ApiKey
    Timeout = 30
    PassedTests = 0
    FailedTests = 0
    SkippedTests = 0
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Write-TestHeader {
    param([string]$Phase, [string]$Description)
    Write-Host ""
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host "  Phase $Phase`: $Description" -ForegroundColor White
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-TestResult {
    param(
        [string]$TestName,
        [bool]$Passed,
        [string]$Expected = "",
        [string]$Actual = "",
        [string]$ErrorMsg = ""
    )

    if ($Passed) {
        Write-Host "[OK] " -ForegroundColor Green -NoNewline
        Write-Host "$TestName" -ForegroundColor White
        $Script:Config.PassedTests++
    } else {
        Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
        Write-Host "$TestName" -ForegroundColor White
        if ($Expected) {
            Write-Host "  Expected: $Expected" -ForegroundColor Gray
        }
        if ($Actual) {
            Write-Host "  Actual: $Actual" -ForegroundColor Gray
        }
        if ($ErrorMsg) {
            Write-Host "  Error: $ErrorMsg" -ForegroundColor Red
        }
        $Script:Config.FailedTests++
    }
}

function Write-TestSkipped {
    param([string]$TestName, [string]$Reason)
    Write-Host "○ " -ForegroundColor Yellow -NoNewline
    Write-Host "$TestName" -ForegroundColor Gray
    Write-Host "  Skipped: $Reason" -ForegroundColor Yellow
    $Script:Config.SkippedTests++
}

function Invoke-ApiRequest {
    param(
        [string]$Method = "GET",
        [string]$Path,
        [hashtable]$Headers = @{},
        [object]$Body = $null
    )

    $uri = "$($Script:Config.BaseUrl)$Path"

    try {
        $params = @{
            Uri = $uri
            Method = $Method
            Headers = $Headers
            TimeoutSec = $Script:Config.Timeout
            ErrorAction = "Stop"
        }

        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
            $params.ContentType = "application/json"
        }

        $response = Invoke-WebRequest @params

        return @{
            Success = $true
            StatusCode = $response.StatusCode
            Headers = $response.Headers
            Content = $response.Content
            Data = ($response.Content | ConvertFrom-Json -ErrorAction SilentlyContinue)
        }
    } catch {
        return @{
            Success = $false
            StatusCode = $_.Exception.Response.StatusCode.value__
            Error = $_.Exception.Message
            Data = $null
        }
    }
}

# ============================================================================
# VALIDATION TESTS
# ============================================================================

function Test-ServerConnectivity {
    Write-TestHeader "1" "Server Connectivity"

    # Test 1: Server responds
    $response = Invoke-ApiRequest -Path "/"
    Write-TestResult -TestName "Server is reachable" `
        -Passed $response.Success `
        -ErrorMsg $response.Error

    # Test 2: Returns JSON
    $isJson = $null -ne $response.Data
    Write-TestResult -TestName "Returns JSON response" `
        -Passed $isJson

    # Test 3: Service name correct
    if ($response.Data) {
        $correctName = $response.Data.service -eq "Atrium Observatory"
        Write-TestResult -TestName "Service name is correct" `
            -Passed $correctName `
            -Expected "Atrium Observatory" `
            -Actual $response.Data.service
    }

    # Test 4: Version present
    if ($response.Data) {
        $hasVersion = $null -ne $response.Data.version
        Write-TestResult -TestName "Version information present" `
            -Passed $hasVersion
    }
}

function Test-HealthEndpoint {
    Write-TestHeader "2" "Health Check Endpoint"

    $response = Invoke-ApiRequest -Path "/health"

    # Test 1: Health endpoint responds
    Write-TestResult -TestName "Health endpoint accessible" `
        -Passed $response.Success

    if ($response.Success) {
        # Test 2: Status is healthy
        $isHealthy = $response.Data.status -eq "healthy"
        Write-TestResult -TestName "Service reports healthy status" `
            -Passed $isHealthy `
            -Expected "healthy" `
            -Actual $response.Data.status

        # Test 3: Timestamp present
        $hasTimestamp = $null -ne $response.Data.timestamp
        Write-TestResult -TestName "Timestamp included in response" `
            -Passed $hasTimestamp
    }
}

function Test-RateLimiting {
    Write-TestHeader "3" "Rate Limiting"

    # Test 1: Rate limit headers present
    $response = Invoke-ApiRequest -Path "/health"
    $hasHeaders = $response.Headers.ContainsKey("x-ratelimit-limit")
    Write-TestResult -TestName "Rate limit headers present" `
        -Passed $hasHeaders

    if ($hasHeaders) {
        # Test 2: Limit value correct
        $limit = [int]$response.Headers["x-ratelimit-limit"]
        $correctLimit = $limit -eq 10
        Write-TestResult -TestName "Public tier limit is 10 req/min" `
            -Passed $correctLimit `
            -Expected "10" `
            -Actual $limit.ToString()
    }

    # Test 3: Remaining count decreases
    $first = Invoke-ApiRequest -Path "/health"
    $second = Invoke-ApiRequest -Path "/health"

    if ($first.Headers.ContainsKey("x-ratelimit-remaining") -and $second.Headers.ContainsKey("x-ratelimit-remaining")) {
        $firstRemaining = [int]$first.Headers["x-ratelimit-remaining"]
        $secondRemaining = [int]$second.Headers["x-ratelimit-remaining"]
        $decreases = $secondRemaining -lt $firstRemaining

        Write-TestResult -TestName "Remaining count decrements correctly" `
            -Passed $decreases
    }
}

function Test-Authentication {
    Write-TestHeader "4" "Authentication"

    # Test 1: Unauthenticated metrics request fails
    $response = Invoke-ApiRequest -Path "/metrics"
    $requiresAuth = $response.StatusCode -eq 401
    Write-TestResult -TestName "Protected endpoint requires authentication" `
        -Passed $requiresAuth `
        -Expected "401 Unauthorized" `
        -Actual "$($response.StatusCode)"

    # Test 2: With API key (if provided)
    if ($Script:Config.ApiKey) {
        $headers = @{
            "Authorization" = "Bearer $($Script:Config.ApiKey)"
        }
        $response = Invoke-ApiRequest -Path "/metrics" -Headers $headers
        $authWorks = $response.Success
        Write-TestResult -TestName "API key grants access to protected endpoint" `
            -Passed $authWorks
    } else {
        Write-TestSkipped -TestName "API key authentication test" `
            -Reason "No API key provided (use -ApiKey parameter)"
    }
}

function Test-ExamplesEndpoint {
    Write-TestHeader "5" "Examples Endpoint"

    # Test 1: List examples
    $response = Invoke-ApiRequest -Path "/examples"
    Write-TestResult -TestName "Examples list endpoint accessible" `
        -Passed $response.Success

    if ($response.Success -and $response.Data) {
        # Test 2: Has examples array
        $hasExamples = $null -ne $response.Data.examples
        Write-TestResult -TestName "Response contains examples array" `
            -Passed $hasExamples

        # Test 3: Has categories
        $hasCategories = $null -ne $response.Data.categories
        Write-TestResult -TestName "Response contains categories" `
            -Passed $hasCategories

        # Test 4: At least one example
        if ($hasExamples) {
            $hasData = $response.Data.examples.Count -gt 0
            Write-TestResult -TestName "At least one example available" `
                -Passed $hasData `
                -Actual "$($response.Data.examples.Count) examples found"
        }
    }
}

function Test-ApiDocumentation {
    Write-TestHeader "6" "API Documentation"

    # Test 1: Swagger UI
    $response = Invoke-ApiRequest -Path "/docs"
    Write-TestResult -TestName "Swagger UI accessible" `
        -Passed $response.Success

    # Test 2: OpenAPI spec
    $response = Invoke-ApiRequest -Path "/openapi.json"
    Write-TestResult -TestName "OpenAPI specification available" `
        -Passed $response.Success

    if ($response.Success -and $response.Data) {
        # Test 3: Has paths
        $hasPaths = $null -ne $response.Data.paths
        Write-TestResult -TestName "OpenAPI spec contains endpoint definitions" `
            -Passed $hasPaths
    }

    # Test 4: ReDoc
    $response = Invoke-ApiRequest -Path "/redoc"
    Write-TestResult -TestName "ReDoc documentation accessible" `
        -Passed $response.Success
}

function Test-AnalysisEndpoint {
    Write-TestHeader "7" "Analysis Endpoint"

    # Test 1: POST without auth should fail or succeed based on config
    $body = @{
        conversation_text = "Human: Test\nAI: Response"
    }
    $response = Invoke-ApiRequest -Method "POST" -Path "/api/v1/analyze" -Body $body

    # Analysis endpoint may require auth or allow public access
    $validResponse = $response.Success -or ($response.StatusCode -eq 401) -or ($response.StatusCode -eq 429)
    Write-TestResult -TestName "Analysis endpoint responds to POST" `
        -Passed $validResponse `
        -Actual "Status: $($response.StatusCode)"

    # Test 2: With API key (if provided)
    if ($Script:Config.ApiKey) {
        $headers = @{
            "Authorization" = "Bearer $($Script:Config.ApiKey)"
        }
        $response = Invoke-ApiRequest -Method "POST" -Path "/api/v1/analyze" -Body $body -Headers $headers

        $accepted = $response.StatusCode -eq 202
        Write-TestResult -TestName "Analysis accepts request with API key" `
            -Passed $accepted `
            -Expected "202 Accepted" `
            -Actual "$($response.StatusCode)"

        # Test 3: Response has analysis ID
        if ($response.Success -and $response.Data) {
            $hasId = $null -ne $response.Data.id
            Write-TestResult -TestName "Analysis response includes ID" `
                -Passed $hasId

            # Test 4: Can retrieve analysis
            if ($hasId) {
                Start-Sleep -Milliseconds 500
                $getResponse = Invoke-ApiRequest -Path "/api/v1/analyze/$($response.Data.id)" -Headers $headers
                Write-TestResult -TestName "Can retrieve analysis by ID" `
                    -Passed $getResponse.Success
            }
        }
    } else {
        Write-TestSkipped -TestName "Authenticated analysis tests" `
            -Reason "No API key provided"
    }
}

function Test-ErrorHandling {
    Write-TestHeader "8" "Error Handling"

    # Test 1: Invalid endpoint returns 404
    $response = Invoke-ApiRequest -Path "/nonexistent-endpoint"
    $is404 = $response.StatusCode -eq 404
    Write-TestResult -TestName "Invalid endpoint returns 404" `
        -Passed $is404 `
        -Expected "404" `
        -Actual "$($response.StatusCode)"

    # Test 2: Invalid example returns 404
    $response = Invoke-ApiRequest -Path "/examples/nonexistent"
    $is404 = $response.StatusCode -eq 404
    Write-TestResult -TestName "Invalid example ID returns 404" `
        -Passed $is404

    # Test 3: Malformed JSON returns 400/422
    try {
        $uri = "$($Script:Config.BaseUrl)/api/v1/analyze"
        $response = Invoke-WebRequest -Uri $uri -Method POST -Body "invalid json" -ContentType "application/json" -ErrorAction SilentlyContinue
        $statusCode = $response.StatusCode
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
    }

    $isClientError = $statusCode -ge 400 -and $statusCode -lt 500
    Write-TestResult -TestName "Malformed request returns client error" `
        -Passed $isClientError `
        -Actual "Status: $statusCode"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Start-Validation {
    Write-Host ""
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host "  Atrium Observatory - Automated Validation Suite" -ForegroundColor White
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Base URL: $($Script:Config.BaseUrl)" -ForegroundColor Gray
    Write-Host "  Mode: $(if ($Quick) { 'Quick' } else { 'Full' })" -ForegroundColor Gray
    if ($Script:Config.ApiKey) {
        Write-Host "  API Key: Provided (***$(($Script:Config.ApiKey).Substring([Math]::Max(0, ($Script:Config.ApiKey).Length - 8))))" -ForegroundColor Gray
    } else {
        Write-Host "  API Key: Not provided (some tests will be skipped)" -ForegroundColor Yellow
    }
    Write-Host ""

    # Run validation tests
    Test-ServerConnectivity
    Test-HealthEndpoint

    if (-not $Quick) {
        Test-RateLimiting
        Test-Authentication
        Test-ExamplesEndpoint
        Test-ApiDocumentation
        Test-AnalysisEndpoint
        Test-ErrorHandling
    }

    # Summary
    Write-Host ""
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host "  Validation Summary" -ForegroundColor White
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host ""

    $total = $Script:Config.PassedTests + $Script:Config.FailedTests + $Script:Config.SkippedTests
    $passRate = if ($total -gt 0) { [math]::Round(($Script:Config.PassedTests / $total) * 100, 1) } else { 0 }

    Write-Host "  Passed:  " -ForegroundColor Gray -NoNewline
    Write-Host $Script:Config.PassedTests -ForegroundColor Green -NoNewline
    Write-Host " / $total" -ForegroundColor Gray

    Write-Host "  Failed:  " -ForegroundColor Gray -NoNewline
    Write-Host $Script:Config.FailedTests -ForegroundColor Red -NoNewline
    Write-Host " / $total" -ForegroundColor Gray

    Write-Host "  Skipped: " -ForegroundColor Gray -NoNewline
    Write-Host $Script:Config.SkippedTests -ForegroundColor Yellow -NoNewline
    Write-Host " / $total" -ForegroundColor Gray

    Write-Host ""
    Write-Host "  Pass Rate: " -ForegroundColor Gray -NoNewline
    if ($passRate -ge 90) {
        Write-Host "${passRate}%" -ForegroundColor Green
    } elseif ($passRate -ge 70) {
        Write-Host "${passRate}%" -ForegroundColor Yellow
    } else {
        Write-Host "${passRate}%" -ForegroundColor Red
    }

    Write-Host ""

    if ($Script:Config.FailedTests -eq 0) {
        Write-Host "[OK] All tests passed!" -ForegroundColor Green
        return 0
    } else {
        Write-Host "[FAIL] Some tests failed. Please review the output above." -ForegroundColor Red
        return 1
    }
}

# Run validation
exit (Start-Validation)
