# Validation Script Bug Fixes

## Issues Found and Fixed

### Bug #1: Reserved Variable Name Collision
**Issue**: `$args` is a reserved PowerShell variable
**Location**: `quick-start.ps1:813`
**Symptom**: Arguments passed incorrectly showing `Base URL: -BaseUrl` instead of actual URL

**Fix**: Renamed variable to `$validationArgs`
```powershell
# Before (broken)
$args = @("-BaseUrl", $Script:Config.BaseUrl)
& $validationScript @args

# After (fixed)
$validationArgs = @("-BaseUrl", $Script:Config.BaseUrl)
& $validationScript @validationArgs
```

---

### Bug #2: Null Reference Exceptions
**Issue**: Script didn't handle failed HTTP requests, causing null reference errors
**Location**: `validation.ps1:213, 231`
**Symptom**:
```
You cannot call a method on a null-valued expression.
At validation.ps1:213 char:5
+     $hasHeaders = $response.Headers.ContainsKey(...)
```

**Fix**: Added proper null checks before accessing properties
```powershell
# Before (broken)
$hasHeaders = $response.Headers.ContainsKey("x-ratelimit-limit")

# After (fixed)
$hasHeaders = $response.Success -and $response.Headers -and
              $response.Headers.ContainsKey("x-ratelimit-limit")
```

---

### Bug #3: Insufficient Server Startup Time
**Issue**: Server startup timeout too short (10s → 30s still insufficient on some systems)
**Location**: `quick-start.ps1:772`
**Symptom**: `Server failed to start after 10 seconds` even when server actually starting

**Fixes Applied**:
1. Increased timeout: 10s → 45s
2. Added progress indicators (shows elapsed time every 5s)
3. Added port conflict detection
4. Better error messages with troubleshooting hints

```powershell
# Before
$maxRetries = 10
while ($retries -lt $maxRetries) {
    Start-Sleep -Seconds 1
    # ... check health ...
}

# After
$maxRetries = 45
while ($retries -lt $maxRetries) {
    Start-Sleep -Milliseconds 1000
    # Show progress every 5 seconds
    if ($retries % 5 -eq 0 -and $retries -gt 0) {
        Write-Host " ${retries}s" -NoNewline
    } else {
        Write-Host "." -NoNewline
    }
    # ... check health with better timeout ...
}
```

4. Added early port conflict detection:
```powershell
$portInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Error "Port $Port is already in use"
    return
}
```

---

## Testing Checklist

After fixes, verify:
- [x] `.\quick-start.ps1 validate` passes arguments correctly
- [x] Server startup waits appropriate time (45s max)
- [x] No null reference errors when server is down
- [x] Port conflict detected early
- [x] Progress feedback during startup
- [x] API key auto-detected from `dev-api-keys.txt`

---

## Usage Examples

### Successful Validation Flow
```powershell
# 1. Generate keys (if not exists)
.\quick-start.ps1 keys

# 2. Run validation (auto-starts server)
.\quick-start.ps1 validate

# Expected output:
# [OK] Server is running at http://127.0.0.1:8000
# OR
# [INFO] Server not running. Starting server in new window...
# [INFO] Waiting for server to start (this can take up to 45 seconds)...
# ..... 5s..... 10s
# [OK] Server is ready! (started in 12s)
```

### With Existing Server
```powershell
# 1. Start server in background
.\quick-start.ps1 serve -NewWindow

# 2. Run validation
.\quick-start.ps1 validate
# [OK] Server is running at http://127.0.0.1:8000
# (runs tests immediately)
```

### Direct Script Usage
```powershell
# Run validation script directly
.\scripts\validation.ps1 -BaseUrl "http://127.0.0.1:8000"

# With API key
.\scripts\validation.ps1 -ApiKey "dev_YOUR_KEY_HERE"

# Quick mode
.\scripts\validation.ps1 -Quick
```

---

## Known Limitations

1. **Server startup on slow systems**: May need >45s on first run (cold start)
   - **Workaround**: Start server manually first, then run validation

2. **Port conflicts**: Script detects but doesn't auto-resolve
   - **Workaround**: Specify different port: `.\quick-start.ps1 validate -Port 8001`

3. **PowerShell version differences**: Works best with PowerShell 7+ (pwsh)
   - **Detection**: Script auto-detects and uses `pwsh` if available

---

## Troubleshooting

### Validation still fails with "Server not responding"
**Cause**: Server crashed during startup or port blocked by firewall
**Check**:
1. Look at server window for error messages
2. Check firewall: `netsh advfirewall firewall show rule name=all | Select-String "8000"`
3. Try different port: `.\quick-start.ps1 validate -Port 8001`

### Tests fail but server is running
**Cause**: Server running on different port or address
**Check**:
```powershell
# Verify server URL
curl http://127.0.0.1:8000/health

# If using different port
.\scripts\validation.ps1 -BaseUrl "http://127.0.0.1:8001"
```

### API key tests skipped
**Cause**: Keys not found in `dev-api-keys.txt` or malformed file
**Fix**:
```powershell
# Regenerate keys
.\quick-start.ps1 keys

# Verify file format
cat dev-api-keys.txt
# Should contain: DEV_KEY=dev_xxxxx...
```
