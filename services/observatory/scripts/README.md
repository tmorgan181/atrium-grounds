# Observatory Scripts

Automation scripts for the Atrium Observatory service.

## Available Scripts

### `validation.ps1`

Automated validation suite that tests all Observatory service endpoints and functionality.

**Usage:**
```powershell
# Basic validation (no API key)
.\scripts\validation.ps1

# With API key for authenticated tests
.\scripts\validation.ps1 -ApiKey "dev_YOUR_KEY_HERE"

# Quick validation (essential checks only)
.\scripts\validation.ps1 -Quick

# Custom base URL
.\scripts\validation.ps1 -BaseUrl "http://localhost:8001"
```

**Features:**
- ✅ Server connectivity and health checks
- ✅ Rate limiting validation
- ✅ Authentication/authorization testing
- ✅ Examples endpoint verification
- ✅ API documentation accessibility
- ✅ Analysis endpoint functionality
- ✅ Error handling and edge cases

**Test Coverage:**
- Phase 1: Server Connectivity (4 tests)
- Phase 2: Health Endpoint (3 tests)
- Phase 3: Rate Limiting (3 tests)
- Phase 4: Authentication (2 tests)
- Phase 5: Examples Endpoint (4 tests)
- Phase 6: API Documentation (4 tests)
- Phase 7: Analysis Endpoint (4 tests)
- Phase 8: Error Handling (3 tests)

**Exit Codes:**
- `0` - All tests passed
- `1` - Some tests failed

---

## Integration with Quick-Start

The validation script is integrated into `quick-start.ps1`:

```powershell
# Run validation (auto-starts server if needed)
.\quick-start.ps1 validate

# Start server in new window, then run validation
.\quick-start.ps1 serve -NewWindow
.\quick-start.ps1 validate
```

**Behavior:**
- Checks if server is running
- Auto-starts server in new window if not running
- Auto-detects API keys from `dev-api-keys.txt`
- Runs full validation suite
- Reports pass/fail status

---

## Adding New Validation Tests

To add new validation tests, edit `validation.ps1`:

1. Create a new test function:
```powershell
function Test-NewFeature {
    Write-TestHeader "9" "New Feature Testing"

    $response = Invoke-ApiRequest -Path "/new-endpoint"
    Write-TestResult -TestName "New endpoint accessible" `
        -Passed $response.Success
}
```

2. Call the function in `Start-Validation`:
```powershell
function Start-Validation {
    # ... existing tests ...
    Test-NewFeature
}
```

3. Test results automatically increment counters and appear in summary

---

## Manual Testing

For manual validation, see `tests/VALIDATION.md` which provides:
- Step-by-step manual test procedures
- Expected responses and outputs
- Troubleshooting guidance
- Sign-off checklist

---

## Troubleshooting

### Validation fails with "Server not responding"
**Cause:** Server not running or wrong port
**Fix:**
```powershell
# Check if server is running
curl http://localhost:8000/health

# Start server manually
.\quick-start.ps1 serve -NewWindow
```

### API key tests skipped
**Cause:** No API key provided or not found in `dev-api-keys.txt`
**Fix:**
```powershell
# Generate keys
.\quick-start.ps1 keys

# Validation will auto-detect keys from dev-api-keys.txt
.\quick-start.ps1 validate
```

### Tests timing out
**Cause:** Server slow to respond or network issues
**Fix:** Increase timeout in validation.ps1 config:
```powershell
$Script:Config = @{
    Timeout = 60  # Increase from 30 to 60 seconds
}
```
