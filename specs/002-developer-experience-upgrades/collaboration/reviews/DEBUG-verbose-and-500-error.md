# Feature 002 - Final Debug Report: Verbose Mode & Test Failures

**Date**: 2025-10-05  
**Status**: Close to Complete - 3 Issues Remaining  
**Current Pass Rate**: 75% (18/24 validation tests)

---

## Progress Update

### What's Now Working ✅
- Partner key loading successful
- API key being passed to validation script
- When verbose mode works, pass rate is 75% (18/24)
- Unit/Contract/Integration tests: 100%

### New Issues Discovered

---

## Issue #1: PowerShell Verbose Noise in Server Startup

### Problem
When using `-Verbose` flag, PowerShell's built-in verbose output pollutes the display during server health checks:

```powershell
[2025-10-05 18:20:02] Starting test server in background...
VERBOSE: GET with 0-byte payload      # PowerShell verbose, not ours
VERBOSE: GET with 0-byte payload      # 17 lines of noise!
VERBOSE: GET with 0-byte payload
...
VERBOSE: received 79-byte response of content type application/json
[OK] Test server ready
```

### Root Cause
`Invoke-WebRequest` in the server health check respects PowerShell's `-Verbose` preference variable. When user passes `-Verbose` to quick-start.ps1, it sets `$VerbosePreference = 'Continue'`, which makes ALL cmdlets show verbose output.

### Fix Required

**Location**: Server health check function in `quick-start.ps1`

```powershell
# Before server health check loop, suppress PowerShell verbose temporarily
$originalVerbose = $VerbosePreference
$VerbosePreference = 'SilentlyContinue'

# Server health check loop
for ($i = 0; $i -lt 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            if ($Verbose) {
                Write-Host "$(Get-Timestamp) Server responded successfully"
            }
            break
        }
    } catch {
        # Ignore startup errors
    }
    Start-Sleep -Seconds 1
}

# Restore verbose preference
$VerbosePreference = $originalVerbose

if ($Verbose) {
    Write-Host "[OK] Test server ready"
}
```

**Impact**: Clean verbose output, no "VERBOSE: GET with 0-byte payload" spam

---

## Issue #2: Rate Limiting Still Causing Failures in Non-Verbose Mode

### Evidence
```powershell
# Without -Verbose:
[FAIL] Server is reachable
  Error: The remote server returned an error: (429) Too Many Requests.
# 13/15 tests fail

# With -Verbose:  
[OK] Server is reachable
# 18/24 tests pass
```

### Analysis
The verbose mode **waits 17 seconds** before starting validation (health check loop with 1s delays), giving time for rate limits to reset. Non-verbose mode **doesn't wait as long**, so validation hits an already-exhausted rate limit.

### Root Cause
The server health check makes too many requests too quickly in non-verbose mode.

### Fix Required

**Make health check use same timing in both modes**:

```powershell
# Same logic for both verbose and non-verbose
for ($i = 0; $i -lt 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            break
        }
    } catch {
        # Continue on error
    }
    Start-Sleep -Seconds 1  # Always wait 1 second between attempts
}
```

**Impact**: Consistent behavior, no rate limit exhaustion

---

## Issue #3: Actual Test Failures (6 tests)

Now that we can see the real failures with `-Verbose`, here are the actual issues:

### Failure #1: API Key Authentication (1 test)
```
[FAIL] API key grants access to protected endpoint
```

**Investigation needed**: What endpoint is being tested? Is the API key being sent correctly?

**Action**: Check validation script to see which endpoint and how key is sent.

---

### Failure #2: Analysis Endpoint Returns 500 (1 test)
```
[FAIL] Analysis accepts request with API key
  Expected: 202 Accepted
  Actual: 500
```

**This is a real bug in the application!** The analysis endpoint is crashing when receiving a request.

**Investigation Required**:
1. Check server logs for the 500 error
2. What's the request payload being sent?
3. Is Ollama running?

**Likely causes**:
- Ollama not running (would return 503, not 500 though)
- Invalid request payload format
- Missing database table/migration
- Exception in analysis code

**Action**: Run server manually and check logs:
```powershell
# Terminal 1: Start server with logs visible
.\quick-start.ps1 serve

# Terminal 2: Send test request
curl -X POST http://localhost:8000/api/v1/analyze `
  -H "Authorization: Bearer PARTNER_KEY_HERE" `
  -H "Content-Type: application/json" `
  -d '{"conversation": "Human: Hello\nAssistant: Hi there!"}'

# Check Terminal 1 for error details
```

---

### Failure #3: OpenAPI Spec (1 test)
```
[FAIL] OpenAPI specification available
```

**Interesting**: This passes sometimes, fails other times. Likely rate limiting related.

**Action**: Should auto-resolve with rate limit fixes above.

---

### Failure #4: ReDoc Documentation (1 test)
```
[FAIL] ReDoc documentation accessible
```

**Persistent issue across all test runs.**

**Investigation**:
```powershell
curl http://localhost:8000/redoc
```

**Possible causes**:
- Route not configured in FastAPI app
- ReDoc template file missing
- Returns 404 or 500

---

### Failure #5 & #6: 404 Tests Return 429 (2 tests)
```
[FAIL] Invalid endpoint returns 404
  Expected: 404
  Actual: 429
[FAIL] Invalid example ID returns 404
```

**Root cause**: These tests run at the end, after 20+ validation requests. Even with partner key (600/min), if validation runs quickly, these might hit the rate limit.

**Two solutions**:

**Option A: Add small delay in validation script**
```powershell
# Between test phases
Start-Sleep -Milliseconds 100
```

**Option B: Test-mode header bypass** (as suggested earlier)
```python
# In app/middleware/ratelimit.py
if request.headers.get("X-Test-Mode") == "validation":
    return await call_next(request)
```

**Recommendation**: Option A first (simpler), then Option B if needed.

---

## Improved Verbose Mode Design

### Current Problem
Verbose mode shows TOO MUCH noise from PowerShell built-ins.

### Proposed Solution
Our custom verbose should be **structured and informative**, not just "show everything."

### Implementation

```powershell
# At start of script, control PowerShell's verbose separately
param(
    [switch]$Verbose
)

if ($Verbose) {
    # Don't automatically enable PowerShell verbose for everything
    $VerbosePreference = 'SilentlyContinue'
    
    # We'll manually show what we want with Write-Host
}

# Helper for our custom verbose output
function Write-VerboseStep {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "$(Get-Timestamp) $Message" -ForegroundColor Cyan
    }
}

# Usage:
Write-VerboseStep "Checking Python installation..."
Write-VerboseStep "Starting test server in background..."
Write-VerboseStep "Running unit tests..."
```

This gives us **clean, controlled verbose output** instead of PowerShell's noisy default.

---

## Action Plan

### Phase 1: Fix Verbose Mode Noise (10 min)

1. **Suppress PowerShell verbose in health check**
```powershell
$VerbosePreference = 'SilentlyContinue'
# health check loop
$VerbosePreference = $originalVerbose
```

2. **Standardize health check timing** (same in both modes)
```powershell
# Always use 1-second delays, max 10 attempts
```

### Phase 2: Fix Real Application Bug (20 min)

3. **Investigate 500 error on analysis endpoint**
```powershell
# Check server logs
# Test endpoint manually
# Fix the actual bug in application code
```

This is **CRITICAL** - a 500 error means something is broken in the app.

### Phase 3: Fix Remaining Test Issues (15 min)

4. **Investigate ReDoc failure**
```powershell
curl http://localhost:8000/redoc
# Check what error it returns
```

5. **Add small delays in validation script**
```powershell
# Between test phases to avoid rate limit
Start-Sleep -Milliseconds 100
```

6. **Check API key auth test**
```powershell
# What endpoint is failing?
# Is key being sent correctly?
```

---

## Expected Results After Fixes

### Verbose Mode Output (Clean)
```powershell
PS> .\quick-start.ps1 test -Verbose -Validation

===============================================================
  Running Validation Suite
===============================================================

[2025-10-05 18:30:00] Checking Python installation...
[OK] Python found: Python 3.12.6
[2025-10-05 18:30:00] Checking uv package manager...
[OK] uv found: uv 0.8.22
[2025-10-05 18:30:00] Checking virtual environment...
[OK] Virtual environment found

[INFO] Using PARTNER_KEY for testing (600 req/min limit)

[2025-10-05 18:30:00] Starting test server in background...
[2025-10-05 18:30:08] Server responded successfully
[OK] Test server ready

[2025-10-05 18:30:08] Running validation suite...

===============================================================
  Atrium Observatory - Automated Validation Suite
===============================================================

# Clean validation output, no VERBOSE: spam

Pass Rate: 96% (23/24 tests)
```

### Test Pass Rates After All Fixes
- Unit: 100%
- Contract: 100%
- Integration: 100%
- Validation: **96%** (23/24)
  - Only ReDoc might still fail (minor issue)

**Overall: 97-98%**

---

## Critical Finding: 500 Error

**This is the most important issue.** The analysis endpoint returning 500 means there's a real bug in the application code, not just test infrastructure issues.

**Must investigate**:
1. What's causing the 500?
2. Is Ollama running?
3. Is the database properly initialized?
4. What's the exact error in server logs?

**Action**: Before fixing test infrastructure, fix the actual application bug causing 500 errors.

---

## Recommended Order

1. **Fix 500 error** (CRITICAL - application bug)
2. **Suppress verbose noise** (improves DX)
3. **Standardize health check timing** (fixes rate limit)
4. **Investigate remaining failures** (polish)

**Estimated Total Time**: 45-60 minutes

---

**Status**: Ready for Final Implementation  
**Blocker**: 500 error on analysis endpoint must be fixed first  
**Expected Outcome**: 96-98% pass rate, clean verbose output
