# Clean Logging for Observatory Server

**Problem**: Uvicorn outputs ANSI escape codes that show as garbage in Windows PowerShell:
```
←[32mINFO←[0m:     127.0.0.1:57693 - "←[1mGET /health HTTP/1.1←[0m" ←[32m200 OK←[0m
```

**Solution**: Custom logging configuration without ANSI codes + Python launcher script

---

## Quick Solution (Immediate Use)

### Option 1: Use the Clean Server Script

```powershell
# Start server with clean logs
uv run python run_clean_server.py

# With custom port
uv run python run_clean_server.py 8001

# With auto-reload (development)
uv run python run_clean_server.py 8000 --reload
```

**Output**:
```
[2025-01-04 20:30:15] INFO     Started server process [12345]
[2025-01-04 20:30:15] INFO     Waiting for application startup
[2025-01-04 20:30:15] INFO     Application startup complete
[2025-01-04 20:30:15] INFO     Uvicorn running on http://0.0.0.0:8000
[2025-01-04 20:30:20] INFO     127.0.0.1:12345 - "GET /health HTTP/1.1" 200
```

### Option 2: Disable Colors with Uvicorn Flag

```powershell
# Windows PowerShell
$env:NO_COLOR="1"
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-use-colors

# PowerShell Core
$env:NO_COLOR = "1"
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-use-colors
```

---

## Files Created

### 1. `app/core/log_config.py`

Custom logging configuration with clean formatters:

**Features**:
- No ANSI escape codes
- Clean timestamps `[2025-01-04 20:30:15]`
- Simple indicators (✓ ✗ ! →) or plain text
- Two configurations:
  - `LOGGING_CONFIG`: With Unicode indicators
  - `LOGGING_CONFIG_SIMPLE`: Plain ASCII only

**Usage in code**:
```python
import uvicorn
from app.core.log_config import LOGGING_CONFIG_SIMPLE

uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port=8000,
    log_config=LOGGING_CONFIG_SIMPLE,
)
```

### 2. `run_clean_server.py`

Python wrapper script that launches uvicorn with clean logging:

**Source**:
```python
"""Launch uvicorn with clean logging configuration."""
import sys
import uvicorn
from app.core.log_config import LOGGING_CONFIG_SIMPLE

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    reload = "--reload" in sys.argv
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        log_config=LOGGING_CONFIG_SIMPLE,
        access_log=True,
    )
```

---

## Integration with quick-start.ps1 (Pending)

**Note**: Claude is currently modifying `quick-start.ps1` for validation fixes. 
Once Claude's changes are committed, add this enhancement:

### Add `-Clean` Flag Parameter

```powershell
param(
    # ... existing parameters ...
    
    [Parameter()]
    [switch]$Clean  # Clean logs without ANSI codes
)
```

### Update Invoke-Server Function

```powershell
function Invoke-Server {
    # ... existing code ...
    
    if ($Clean) {
        # Use clean logging
        if ($NewWindow) {
            $serverScript = "cd '$PWD'; & '$($Script:Config.VenvPath)\python.exe' run_clean_server.py $Port $(if($Reload){'--reload'})"
            Start-Process $pwsh -ArgumentList "-NoExit", "-Command", $serverScript
        } else {
            & "$($Script:Config.VenvPath)\python.exe" run_clean_server.py $Port $(if($Reload){'--reload'})
        }
    } else {
        # Existing uvicorn command
        # ...
    }
}
```

### Usage

```powershell
# Clean logs in new window
.\quick-start.ps1 serve -NewWindow -Clean

# Clean logs in foreground
.\quick-start.ps1 serve -Clean

# Demo with clean logs
.\quick-start.ps1 demo -Clean
```

---

## Log Format Examples

### Before (With ANSI Codes)

```
←[32mINFO←[0m:     Will watch for changes in these directories
←[32mINFO←[0m:     Uvicorn running on ←[1mhttp://0.0.0.0:8000←[0m
←[32mINFO←[0m:     127.0.0.1:57693 - "←[1mGET /health HTTP/1.1←[0m" ←[32m200 OK←[0m
←[32mINFO←[0m:     127.0.0.1:57693 - "←[1mGET /metrics HTTP/1.1←[0m" ←[31m401 Unauthorized←[0m
{"timestamp": "2025-10-05T02:24:51.099719", "event": "rate_limit_exceeded", ...}
```

### After (Clean, Option 1 - With Indicators)

```
[2025-01-04 20:30:15] ℹ INFO     Will watch for changes in these directories
[2025-01-04 20:30:15] ℹ INFO     Uvicorn running on http://0.0.0.0:8000
[2025-01-04 20:30:20] ℹ INFO     127.0.0.1:57693 - "GET /health HTTP/1.1" 200
[2025-01-04 20:30:21] ℹ INFO     127.0.0.1:57693 - "GET /metrics HTTP/1.1" 401
[2025-01-04 20:30:22] ⚠ WARNING  Rate limit exceeded for 127.0.0.1
```

### After (Clean, Option 2 - Plain Text)

```
[2025-01-04 20:30:15] INFO     Will watch for changes in these directories
[2025-01-04 20:30:15] INFO     Uvicorn running on http://0.0.0.0:8000
[2025-01-04 20:30:20] INFO     127.0.0.1:57693 - "GET /health HTTP/1.1" 200
[2025-01-04 20:30:21] INFO     127.0.0.1:57693 - "GET /metrics HTTP/1.1" 401
[2025-01-04 20:30:22] WARNING  Rate limit exceeded for 127.0.0.1
```

---

## Custom Log Formatting

### Structured Logging (JSON) - Already in Code

The custom logging from `app/core/logging.py` already outputs structured JSON:

```python
from app.core.logging import audit_log

audit_log("rate_limit_exceeded", 
    ip_address="127.0.0.1", 
    tier="public",
    endpoint="/api/v1/analyze"
)
```

**Output**:
```json
{"timestamp": "2025-01-04T20:30:22.123456", "event": "rate_limit_exceeded", "ip_address": "127.0.0.1", "tier": "public", "endpoint": "/api/v1/analyze"}
```

This is **intentional** for production log aggregation (ELK, Splunk, etc.). 
The clean formatter is for **development readability**.

### Development vs Production

**Development** (Clean, Readable):
```
[2025-01-04 20:30:22] ⚠ WARNING  Rate limit exceeded for 127.0.0.1
```

**Production** (Structured, Parseable):
```json
{"timestamp": "2025-01-04T20:30:22.123456", "event": "rate_limit_exceeded", "ip_address": "127.0.0.1"}
```

**Configuration**:
```python
# app/core/config.py
class Settings(BaseSettings):
    log_format: str = "text"  # "text" or "json"
    log_level: str = "info"
```

---

## Troubleshooting

### Still Seeing ANSI Codes?

**Cause**: Terminal doesn't respect `NO_COLOR` or uvicorn flag ignored

**Fix**: Use the `run_clean_server.py` script which forces clean config

### Unicode Indicators Not Showing?

**Cause**: Terminal doesn't support Unicode characters

**Solution**: Modify `log_config.py` to use plain ASCII:

```python
# In CleanFormatter.format()
indicators = {
    'INFO': '[INFO]',
    'WARNING': '[WARN]',
    'ERROR': '[ERROR]',
    # ...
}
```

### Want Custom Format?

Edit `app/core/log_config.py`:

```python
class CleanFormatter(logging.Formatter):
    def format(self, record):
        # Your custom format here
        return f"YOUR_FORMAT_HERE"
```

---

## Environment Variables

Control logging behavior with environment variables:

```powershell
# Disable all colors globally
$env:NO_COLOR = "1"

# Force ANSI colors (override auto-detection)
$env:FORCE_COLOR = "1"

# Set log level
$env:LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR

# Set log format
$env:LOG_FORMAT = "json"  # "text" or "json"
```

---

## Future Enhancements

### 1. Middleware for Clean HTTP Logs

Create custom middleware to format HTTP requests cleanly:

```python
# app/middleware/logging.py
from fastapi import Request
import time

async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Clean format
    print(f"[{datetime.now()}] {response.status_code} {request.method:4} {request.url.path:40} {duration*1000:.0f}ms")
    
    return response
```

### 2. Request ID Tracing

Add request IDs for distributed tracing:

```
[2025-01-04 20:30:22] [req-abc123] INFO GET /health 200 - 12ms
[2025-01-04 20:30:22] [req-abc123] INFO Analysis started
[2025-01-04 20:30:30] [req-abc123] INFO Analysis completed - 8.5s
```

### 3. Log Rotation

For production, add file logging with rotation:

```python
"handlers": {
    "file": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": "logs/observatory.log",
        "maxBytes": 10485760,  # 10MB
        "backupCount": 5,
        "formatter": "simple",
    }
}
```

---

## Testing

### Verify Clean Logs

```powershell
# Start server with clean logs
uv run python run_clean_server.py

# In another terminal, make requests
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/docs

# Check output - should have NO ←[XXm codes
```

### Compare Formats

```powershell
# With ANSI (default)
uv run python -m uvicorn app.main:app --port 8000 > ansi.log 2>&1

# Without ANSI (clean)
uv run python run_clean_server.py 8000 > clean.log 2>&1

# Compare
notepad ansi.log
notepad clean.log
```

---

## Summary

✅ **Created**:
- `app/core/log_config.py` - Custom logging configuration
- `run_clean_server.py` - Clean server launcher
- `docs/CLEAN-LOGGING.md` - This documentation

✅ **Usage**:
```powershell
uv run python run_clean_server.py 8000 --reload
```

⏳ **Pending** (After Claude finishes):
- Add `-Clean` flag to quick-start.ps1
- Integrate with `serve` and `demo` actions

**Before**:
```
←[32mINFO←[0m:     127.0.0.1 - "←[1mGET /health←[0m" ←[32m200 OK←[0m
```

**After**:
```
[2025-01-04 20:30:20] INFO     127.0.0.1 - "GET /health" 200
```

**Much better!** 🎉
