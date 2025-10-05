# Final Fixes for Feature 002 - Test Infrastructure

**Date**: 2025-10-05  
**Status**: Near Complete - 2 Critical Fixes Needed  
**Current Pass Rate**: 80% (20/25 validation tests)

---

## Current Status

### What's Working ✅
- Unit tests: 100% passing
- Contract tests: 100% passing
- Integration tests: 100% passing
- Validation tests: 80% passing (20/25)
- `Invoke-GenerateKeys` issue resolved
- Virtual environment working correctly
- OpenAPI specification now accessible

### What Needs Fixing ⚠️

**Issue #1**: Validation tests don't use API keys (causes 2 skips + impacts other tests)
**Issue #2**: Pytest output not shown in verbose mode
**Issue #3**: ReDoc endpoint failing (1 test)

---

## Fix #1: Use Partner Key for Validation Tests

### Problem
Validation tests run without API keys, causing:
- 2 tests skipped (authenticated endpoints)
- Public tier rate limiting (10 req/min) causes failures when validation runs alone
- Tests hit 429 errors instead of testing actual functionality

### Solution
Load partner key from `dev-api-keys.txt` when running validation tests.

### Implementation

**Location**: `quick-start.ps1`, in the test prerequisite section (around line 700-750)

**Current Code** (broken):
```powershell
# No API key loading for validation
```

**Fixed Code**:
```powershell
# Load API keys for testing
$apiKey = $null

if (Test-Path "dev-api-keys.txt") {
    $keyContent = Get-Content "dev-api-keys.txt" -Raw
    
    # Prefer partner key for higher rate limits (600 req/min)
    if ($keyContent -match 'PARTNER_KEY=([^\r\n]+)') {
        $apiKey = $matches[1]
        if ($Verbose) {
            Write-Host "$(Get-Timestamp) Using PARTNER_KEY for testing (600 req/min)" -ForegroundColor Cyan
        } else {
            Write-Host "[INFO] Using PARTNER_KEY for testing (600 req/min limit)" -ForegroundColor Cyan
        }
    }
    # Fallback to dev key
    elseif ($keyContent -match 'DEV_KEY=([^\r\n]+)') {
        $apiKey = $matches[1]
        if ($Verbose) {
            Write-Host "$(Get-Timestamp) Using DEV_KEY for testing (60 req/min)" -ForegroundColor Cyan
        } else {
            Write-Host "[INFO] Using DEV_KEY for testing (60 req/min limit)" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "[WARN] No API keys found - generate with: .\quick-start.ps1 keys" -ForegroundColor Yellow
}
```

**Then pass to validation script**:
```powershell
# When invoking validation script (around line 850-900)
$validationParams = @{
    BaseUrl = $baseUrl
}

if ($apiKey) {
    $validationParams['ApiKey'] = $apiKey
}

& ".\scripts\validate.ps1" @validationParams
```

### Expected Impact
- ✅ 2 skipped tests will now run (authenticated endpoints)
- ✅ Partner key (600 req/min) eliminates rate limiting issues
- ✅ All validation tests should pass (except ReDoc issue)
- ✅ No need for rate limit bypass header
- ✅ Pass rate: 88-96% (22-24/25 tests)

---

## Fix #2: Show Pytest Output in Verbose Mode

### Problem
When running with `-Verbose`, the actual pytest output is not shown. User only sees:
```
[2025-10-05 17:35:37] Running unit tests...
[2025-10-05 17:35:37] Running: pytest tests/unit/ -v --tb=short
# Nothing here - pytest output is hidden!

[2025-10-05 17:35:41] Running contract tests...
```

### Solution
In verbose mode, let pytest write directly to console instead of capturing output.

### Implementation

**Location**: `quick-start.ps1`, test execution functions

**Current Code** (broken):
```powershell
if ($Verbose) {
    Write-Host "$(Get-Timestamp) Running unit tests..."
    Write-Host "$(Get-Timestamp) Running: pytest tests/unit/ -v --tb=short"
    # Output is still being hidden somehow
    $result = uv run pytest tests/unit/ -v --tb=short
}
```

**Fixed Code**:
```powershell
if ($Verbose) {
    Write-Host "$(Get-Timestamp) Running unit tests..."
    Write-Host "$(Get-Timestamp) Running: pytest tests/unit/ -v --tb=short"
    Write-Host ""  # Blank line for readability
    
    # Let pytest write directly to console
    uv run pytest tests/unit/ -v --tb=short
    $exitCode = $LASTEXITCODE
    
    Write-Host ""  # Blank line after pytest output
    if ($exitCode -eq 0) {
        Write-Host "$(Get-Timestamp) Unit tests: PASSED" -ForegroundColor Green
    } else {
        Write-Host "$(Get-Timestamp) Unit tests: FAILED (exit code: $exitCode)" -ForegroundColor Red
    }
} else {
    # Terse mode - suppress pytest output
    uv run pytest tests/unit/ -v --tb=short 2>&1 | Out-Null
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "[OK] Unit tests passed"
    } else {
        Write-Host "[FAIL] Unit tests failed (exit code: $exitCode)" -ForegroundColor Red
    }
}
```

**Apply this pattern to**:
- Unit tests function
- Contract tests function
- Integration tests function

### Expected Output in Verbose Mode
```powershell
[2025-10-05 17:35:37] Running unit tests...
[2025-10-05 17:35:37] Running: pytest tests/unit/ -v --tb=short

============================= test session starts ==============================
platform win32 -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0 -- ...
cachedir: .pytest_cache
rootdir: C:\Users\tmorg\Projects\atrium-grounds\services\observatory
collected 58 items

tests/unit/test_analyzer.py::test_dialectic_pattern_detection PASSED    [  1%]
tests/unit/test_analyzer.py::test_sentiment_analysis PASSED             [  2%]
tests/unit/test_analyzer.py::test_topic_extraction PASSED               [  3%]
...
============================= 58 passed in 2.34s ===============================

[2025-10-05 17:35:39] Unit tests: PASSED
```

---

## Fix #3: Investigate ReDoc Endpoint (Optional)

### Current Status
```
[FAIL] ReDoc documentation accessible
```

### Investigation Steps

1. **Manual test**:
```powershell
# With server running:
curl http://localhost:8000/redoc -UseBasicParsing

# Expected: HTML page with ReDoc
# Actual: ?
```

2. **Check app configuration** in `app/main.py`:
```python
app = FastAPI(
    title="Atrium Observatory API",
    docs_url="/docs",      # Swagger - works
    redoc_url="/redoc",    # ReDoc - fails
)
```

3. **Verify FastAPI version** supports ReDoc:
```powershell
uv pip list | Select-String fastapi
```

### Possible Fixes

**If endpoint returns 404**:
```python
# In app/main.py, ensure redoc_url is set
app = FastAPI(
    redoc_url="/redoc",  # Explicitly set
)
```

**If endpoint returns 500**:
- Check server logs for errors
- May be missing ReDoc static files

**If endpoint returns 429**:
- Use partner key in validation (Fix #1 above)

---

## Implementation Priority

### Must Fix (Blocks 100% pass rate)
1. **Fix #1: Use Partner Key** (15 minutes)
   - Eliminates rate limiting issues
   - Enables authenticated test execution
   - Expected impact: 88-96% pass rate

2. **Fix #2: Show Pytest Output** (20 minutes)
   - Critical for debugging test failures
   - Improves developer experience
   - Makes `-Verbose` actually useful

### Should Fix (Final polish)
3. **Fix #3: ReDoc Investigation** (15 minutes)
   - Only affects 1 test
   - May auto-resolve with partner key
   - Nice-to-have for documentation completeness

---

## Testing Checklist

After implementing fixes:

```powershell
# 1. Clean environment
.\quick-start.ps1 clean

# 2. Setup fresh
.\quick-start.ps1 setup

# 3. Generate API keys
.\quick-start.ps1 keys

# 4. Test with verbose to see pytest output
.\quick-start.ps1 test -Verbose

# Expected output:
# - Timestamps shown: [2025-10-05 HH:mm:ss]
# - "Using PARTNER_KEY for testing (600 req/min limit)"
# - Full pytest output for unit/contract/integration tests
# - All test suites pass
# - Validation shows 23-24/25 passing (92-96%)

# 5. Test validation in isolation
.\quick-start.ps1 test -Verbose -Validation

# Expected:
# - No rate limit exhaustion (using partner key)
# - Should pass 23-24/25 tests
# - Only ReDoc test might fail

# 6. Test terse mode still works
.\quick-start.ps1 test

# Expected:
# - Clean, minimal output
# - No pytest output shown
# - Clear pass/fail summary
```

---

## Expected Final Results

### Test Pass Rates After Fixes
- Unit: 100% (58/58)
- Contract: 100% (38/38)
- Integration: 100% (19/19)
- Validation: 92-96% (23-24/25)
  - Only ReDoc might fail
  - No skipped tests (partner key enables all)
  - No rate limit failures

### Overall: 96-98% (138-139/140 total tests)

---

## Code Snippets Ready for Implementation

### Snippet 1: API Key Loading
```powershell
# Add around line 720-750 in quick-start.ps1

# Load API keys for testing if available
$apiKey = $null

if (Test-Path "dev-api-keys.txt") {
    $keyContent = Get-Content "dev-api-keys.txt" -Raw
    
    # Prefer PARTNER_KEY for higher rate limits
    if ($keyContent -match 'PARTNER_KEY=([^\r\n]+)') {
        $apiKey = $matches[1]
        Write-Host "[INFO] Using PARTNER_KEY for testing (600 req/min limit)" -ForegroundColor Cyan
    }
    elseif ($keyContent -match 'DEV_KEY=([^\r\n]+)') {
        $apiKey = $matches[1]
        Write-Host "[INFO] Using DEV_KEY for testing (60 req/min limit)" -ForegroundColor Cyan
    }
}

if (-not $apiKey) {
    Write-Host "[WARN] No API keys found - some tests will be skipped" -ForegroundColor Yellow
    Write-Host "[INFO] Generate keys with: .\quick-start.ps1 keys" -ForegroundColor Cyan
}
```

### Snippet 2: Pytest Output in Verbose
```powershell
# Replace test execution sections (3 places: unit, contract, integration)

function Run-PytestSuite {
    param(
        [string]$Name,
        [string]$Path,
        [bool]$Verbose
    )
    
    if ($Verbose) {
        Write-Host "$(Get-Timestamp) Running $Name tests..."
        Write-Host "$(Get-Timestamp) Running: pytest $Path -v --tb=short"
        Write-Host ""
        
        # Let pytest write to console
        uv run pytest $Path -v --tb=short
        $exitCode = $LASTEXITCODE
        
        Write-Host ""
        if ($exitCode -eq 0) {
            Write-Host "$(Get-Timestamp) $Name tests: PASSED" -ForegroundColor Green
        } else {
            Write-Host "$(Get-Timestamp) $Name tests: FAILED" -ForegroundColor Red
        }
    } else {
        uv run pytest $Path -v --tb=short 2>&1 | Out-Null
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Host "[OK] $Name tests passed"
        } else {
            Write-Host "[FAIL] $Name tests failed" -ForegroundColor Red
        }
    }
    
    return $exitCode
}

# Usage:
$unitResult = Run-PytestSuite -Name "unit" -Path "tests/unit/" -Verbose $Verbose
$contractResult = Run-PytestSuite -Name "contract" -Path "tests/contract/" -Verbose $Verbose
$integrationResult = Run-PytestSuite -Name "integration" -Path "tests/integration/" -Verbose $Verbose
```

### Snippet 3: Pass API Key to Validation
```powershell
# When invoking validation script

$validationParams = @{
    BaseUrl = $baseUrl
}

if ($apiKey) {
    $validationParams['ApiKey'] = $apiKey
}

if ($Verbose) {
    Write-Host "$(Get-Timestamp) Running validation suite..."
}

& ".\scripts\validate.ps1" @validationParams
```

---

## Estimated Time

- Fix #1 (Partner key): 15 minutes
- Fix #2 (Pytest output): 20 minutes  
- Testing & verification: 10 minutes
- **Total: 45 minutes to 96%+ pass rate**

Fix #3 (ReDoc) can be investigated separately if needed.

---

**Status**: Ready for Implementation  
**Assignee**: Claude Code  
**Expected Outcome**: Feature 002 complete and ready for merge
