# Observatory Development Workflow

Complete guide for setting up, testing, and running the Observatory service.

## Quick Start (One-Time Setup)

```powershell
# 1. Setup everything (installs dependencies + generates API keys)
.\quick-start.ps1 setup

# 2. Validate the service (auto-starts server, runs tests, auto-stops)
.\quick-start.ps1 validate

# 3. Start the service for development
.\quick-start.ps1 serve
```

That's it! You're ready to develop.

---

## Detailed Workflow

### Step 1: Initial Setup

```powershell
.\quick-start.ps1 setup
```

**What it does:**
- ✅ Creates virtual environment with `uv`
- ✅ Installs all dependencies
- ✅ Installs dev dependencies (pytest, ruff, etc.)
- ✅ **Auto-generates API keys** if they don't exist
- ✅ Keys saved to `dev-api-keys.txt`

**Output:**
```
[OK] Dependencies installed!
[OK] API keys already exist
[OK] Setup complete!
```

---

### Step 2: Run Validation

```powershell
.\quick-start.ps1 validate
```

**What it does:**
1. ✅ Checks if server is running
2. ✅ If not, starts server **in background** (not new window)
3. ✅ Auto-detects API keys from `dev-api-keys.txt`
4. ✅ Runs comprehensive validation suite
5. ✅ **Automatically stops validation server** when done
6. ✅ Reports pass/fail status

**Output:**
```
[INFO] Server not running. Starting server for validation...
[OK] Server is ready! (started in 8s)
[OK] Using API key from dev-api-keys.txt

===============================================================
  Phase 1: Server Connectivity
===============================================================
[OK] Server is reachable
[OK] Returns JSON response
...
[OK] All tests passed!

[INFO] Stopping validation server...
[OK] Validation server stopped
[OK] Validation passed!
```

---

### Step 3: Start Development Server

```powershell
# Option A: Run in current terminal (blocks)
.\quick-start.ps1 serve

# Option B: Run in new window (non-blocking)
.\quick-start.ps1 serve -NewWindow
```

**What it does:**
- ✅ Starts FastAPI server with hot reload
- ✅ Auto-loads API keys from `dev-api-keys.txt` (shows in startup logs)
- ✅ Server accessible at `http://127.0.0.1:8000`

**Output:**
```
[OK] Server starting in new pwsh window
[OK] Server is ready at http://127.0.0.1:8000

# In server window:
INFO: Application startup complete
✓ Development API keys registered:
  - API Key tier (60 req/min)
  - Partner tier (600 req/min)
  Keys loaded from dev-api-keys.txt
```

---

## Testing Workflows

### Run All Tests

```powershell
# All test suites (unit + contract + integration + validation)
.\quick-start.ps1 test
```

**New in Feature 002**: Quiet output by default! Add `-Detail` for verbose output.

### Test Filtering (NEW - Feature 002)

Run specific test types for faster feedback:

```powershell
# Unit tests only (~2 seconds, 60x faster!)
.\quick-start.ps1 test -Unit

# Contract tests only
.\quick-start.ps1 test -Contract

# Integration tests only
.\quick-start.ps1 test -Integration

# Validation suite only
.\quick-start.ps1 test -Validation

# Combine multiple types
.\quick-start.ps1 test -Unit -Contract
```

### Coverage Reports (NEW - Feature 002)

```powershell
# Generate coverage for any test type
.\quick-start.ps1 test -Unit -Coverage
.\quick-start.ps1 test -Coverage  # All tests with coverage
```

### Verbosity Control (NEW - Feature 002)

```powershell
# Default: Quiet, scannable output
.\quick-start.ps1 test -Unit

# Detail: Full pytest output with diagnostics
.\quick-start.ps1 test -Unit -Detail
```

---

## Code Quality (NEW - Feature 002)

### Quick Linting

```powershell
# Check code style (fast, read-only)
.\quick-start.ps1 lint

# With full details
.\quick-start.ps1 lint -Detail
```

### Auto-Format Code

```powershell
# Format all code with ruff
.\quick-start.ps1 format

# Shows: "12 files reformatted, 45 files left unchanged"
```

### Pre-Commit Checks

```powershell
# Run linting + type checking (recommended before commit)
.\quick-start.ps1 check

# Runs both:
# - ruff check (linting)
# - mypy app/ (type checking)
```

**Best Practice**: Run `.\quick-start.ps1 check` before committing code!

---

## Verbosity Control (NEW - Feature 002)

All actions now support minimal output by default, with `-Detail` for diagnostics:

```powershell
# Default: Minimal, scannable output
.\quick-start.ps1 setup
# Output: ~8 lines, <5 seconds to scan

# Detail: Full diagnostic output
.\quick-start.ps1 setup -Detail
# Output: Full tool output (uv, pip, etc.)
```

**Actions with verbosity control:**
- `setup` - Dependencies installation
- `test` - Test execution
- `lint` - Code linting
- All other actions respect `-Detail` flag

---

## Clean Logging for Windows (NEW - Feature 002)

For Windows PowerShell 5.1 or CI/CD environments without ANSI support:

```powershell
# Start server with ANSI-free logs
.\quick-start.ps1 serve -Clean

# Works in all modes:
.\quick-start.ps1 serve -Clean -NewWindow
```

**When to use `-Clean`:**
- Windows PowerShell 5.1 (no ANSI support)
- CI/CD pipelines
- Log file capture
- Screen readers

---

## API Key Management

### View Current Keys

```powershell
cat dev-api-keys.txt
```

### Regenerate Keys

```powershell
.\quick-start.ps1 keys
```

**Note**: Keys are auto-loaded by server at startup. No manual configuration needed!

### Use Keys Manually

```powershell
# Load key into variable
$key = (cat dev-api-keys.txt | Select-String "DEV_KEY").ToString().Split("=")[1]

# Make authenticated request
$headers = @{"Authorization" = "Bearer $key"}
Invoke-WebRequest -Uri "http://127.0.0.1:8000/metrics" -Headers $headers
```

---

## Common Workflows

### Full Development Cycle (with Feature 002 enhancements)

```powershell
# 1. Setup (first time only)
.\quick-start.ps1 setup

# 2. Make code changes
# ... edit files ...

# 3. Quick validation (unit tests only, ~2 seconds)
.\quick-start.ps1 test -Unit

# 4. Check code quality before commit
.\quick-start.ps1 check

# 5. Auto-format if needed
.\quick-start.ps1 format

# 6. Run full test suite with coverage
.\quick-start.ps1 test -Coverage

# 7. Validate service (auto-starts/stops server)
.\quick-start.ps1 validate

# 8. Start dev server
.\quick-start.ps1 serve -NewWindow

# 9. Test manually
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/docs

# 10. Stop server (close window or Ctrl+C)
```

**Pro Tip**: Use `-Detail` flag anytime you need more diagnostic information!

### Quick Validation Loop

```powershell
# Run this after each change
.\quick-start.ps1 validate

# No need to manually start/stop server!
```

### Clean Slate

```powershell
# Remove everything and start fresh
.\quick-start.ps1 clean
.\quick-start.ps1 setup
```

---

## Troubleshooting

### "Port already in use"

**Solution 1**: Kill existing process
```powershell
# Find process on port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
Stop-Process -Id <PID>
```

**Solution 2**: Use different port
```powershell
.\quick-start.ps1 serve -Port 8001
.\quick-start.ps1 validate -Port 8001
```

### "API key tests skipped"

**Cause**: Keys not generated or file corrupted

**Fix**:
```powershell
.\quick-start.ps1 keys  # Regenerate
.\quick-start.ps1 validate  # Try again
```

### "Validation server won't stop"

**Cause**: Process tracking lost

**Fix**:
```powershell
# Manually kill Python processes
Get-Process python | Where-Object {$_.CommandLine -like "*uvicorn*"} | Stop-Process
```

### "Tests timing out"

**Cause**: Server slow to start on first run

**Fix**: Start server first, then validate
```powershell
.\quick-start.ps1 serve -NewWindow  # Start manually
.\quick-start.ps1 validate          # Will detect running server
```

---

## Advanced Usage

### Custom Validation

```powershell
# Direct script usage
.\scripts\validation.ps1 -BaseUrl "http://127.0.0.1:8001" -ApiKey "custom_key"

# Quick mode (essential tests only)
.\scripts\validation.ps1 -Quick
```

### Watch Mode (Auto-rerun tests)

```powershell
# Install pytest-watch
uv pip install pytest-watch

# Watch and re-run on changes
uv run ptw tests/unit/
```

### Coverage Reports

```powershell
# Generate HTML coverage report
uv run pytest --cov=app --cov-report=html tests/
start htmlcov/index.html
```

---

## Best Practices

1. **Always run `setup` first** - It handles everything (deps + keys)
2. **Use `validate` for quick checks** - Auto-manages server lifecycle
3. **Use `serve -NewWindow` for dev** - Keeps server separate from work
4. **Check `dev-api-keys.txt`** - Keys should exist after setup
5. **Run `clean` sparingly** - Only when dependencies are broken

---

## What Gets Auto-Generated

After `.\quick-start.ps1 setup`:

```
services/observatory/
├── .venv/                    # Virtual environment
├── dev-api-keys.txt         # API keys (auto-loaded by server)
├── data/                    # SQLite database (created on first run)
│   └── observatory.db
└── .pytest_cache/           # Test cache
```

**Important**: `dev-api-keys.txt` is in `.gitignore` - never committed!

---

## Quick Reference

| Command | Purpose | Server | Notes |
|---------|---------|--------|-------|
| `setup` | Install deps + generate keys | No | Use `-Detail` for full output |
| `test` | Run all tests | No | Quiet by default |
| `test -Unit` | **NEW** Run unit tests only | No | 60x faster! (~2s) |
| `test -Coverage` | **NEW** Run tests with coverage | No | Works with any test type |
| `lint` | **NEW** Check code style | No | Read-only check |
| `format` | **NEW** Auto-format code | No | Modifies files |
| `check` | **NEW** Lint + type check | No | Pre-commit validation |
| `validate` | Auto-managed validation | Auto-start/stop | *Deprecated: use `test -Validation`* |
| `serve` | Start dev server | Yes (foreground) | Add `-Clean` for ANSI-free logs |
| `serve -NewWindow` | Start in new window | Yes (background) | Recommended for dev |
| `keys` | Generate/regenerate API keys | No | Auto-loaded by server |
| `clean` | Remove all generated files | No | Fresh start |
| `health` | Test health endpoint | Requires running server | Quick check |
| `analyze` | Test analysis endpoint | Requires running server | Sample data test |

**All commands** support `-Detail` flag for verbose diagnostics!

---

## Integration with CI/CD

```yaml
# GitHub Actions example
- name: Setup
  run: .\quick-start.ps1 setup

- name: Run Tests
  run: .\quick-start.ps1 test

- name: Validate Service
  run: .\quick-start.ps1 validate
```

The validation will auto-start/stop the server, perfect for CI environments!
