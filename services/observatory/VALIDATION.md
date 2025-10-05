# Observatory Service - Human Validation Guide

**Version**: 0.1.0  
**Last Updated**: 2025-01-04  
**Purpose**: Manual validation checklist for server operations and interface functionality

---

## Prerequisites

Before starting validation, ensure:

- [ ] Python 3.11+ installed (`python --version`)
- [ ] uv package manager installed (`uv --version`)
- [ ] Ollama running with Observer model (`ollama list | Select-String observer`)
- [ ] Terminal in `services/observatory` directory

---

## Phase 1: Server Startup & Health Checks

### 1.1 Start the Server

```powershell
# Using quick-start script (recommended)
.\quick-start.ps1 serve

# Or manually
uv run fastapi dev main.py --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Validation**:
- [ ] Server starts without errors
- [ ] No deprecation warnings in console
- [ ] Port 8000 is accessible

### 1.2 Root Endpoint

```powershell
curl http://localhost:8000/
```

**Expected Response**:
```json
{
  "service": "atrium-observatory",
  "version": "0.1.0",
  "status": "operational",
  "docs": "/docs"
}
```

**Validation**:
- [ ] Returns 200 OK
- [ ] JSON structure correct
- [ ] Version matches current release

### 1.3 Health Check

```powershell
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-04T...",
  "version": "0.1.0",
  "dependencies": {
    "database": "connected",
    "ollama": "connected"
  }
}
```

**Validation**:
- [ ] Returns 200 OK
- [ ] Status is "healthy"
- [ ] Database shows "connected"
- [ ] Ollama shows "connected"

**If Ollama is DOWN**:
```json
{
  "dependencies": {
    "ollama": "error: Connection refused"
  }
}
```
- [ ] Error message is clear
- [ ] Server still responds (degraded mode OK)

---

## Phase 2: API Documentation

### 2.1 OpenAPI/Swagger UI

Open in browser:
```
http://localhost:8000/docs
```

**Validation**:
- [ ] Swagger UI loads correctly
- [ ] See 4 main endpoint groups:
  - **analysis** - POST /api/v1/analyze
  - **batch** - POST /api/v1/batch/submit
  - **examples** - GET /examples/
  - **health** - GET /health
- [ ] Can expand endpoints to see schemas
- [ ] "Try it out" buttons visible

### 2.2 ReDoc Alternative

Open in browser:
```
http://localhost:8000/redoc
```

**Validation**:
- [ ] ReDoc UI loads
- [ ] Same endpoints listed
- [ ] Cleaner documentation view

---

## Phase 3: Example Data Tests

### 3.1 List Available Examples

```powershell
curl http://localhost:8000/examples/
```

**Expected Response**:
```json
{
  "examples": [
    "dialectic-simple",
    "dialectic-complex",
    "exploration"
  ],
  "count": 3
}
```

**Validation**:
- [ ] Returns array of example IDs
- [ ] Count matches array length
- [ ] Contains at least 3 examples

### 3.2 Get Specific Example

```powershell
curl http://localhost:8000/examples/dialectic-simple
```

**Expected Response**:
```json
{
  "id": "dialectic-simple",
  "conversation": "Human: ...\nAssistant: ...",
  "metadata": { ... }
}
```

**Validation**:
- [ ] Returns conversation text
- [ ] Includes metadata
- [ ] Text contains "Human:" and "Assistant:" markers

### 3.3 Invalid Example (Error Handling)

```powershell
curl http://localhost:8000/examples/nonexistent
```

**Expected Response**:
```json
{
  "detail": "Example 'nonexistent' not found"
}
```

**Validation**:
- [ ] Returns 404 status
- [ ] Error message is helpful
- [ ] Doesn't crash server

---

## Phase 4: Authentication & API Keys

### 4.1 Generate Development API Key

```powershell
# Using quick-start script
.\quick-start.ps1 keys

# Or manually
uv run python -c "from app.core.dev_keys import generate_dev_keys; import json; print(json.dumps(generate_dev_keys(), indent=2))"
```

**Expected Output**:
```json
{
  "dev_key": "dev_xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "dev_hash": "$2b$12$..."
}
```

**Validation**:
- [ ] Key starts with "dev_"
- [ ] Key is 32+ characters
- [ ] Hash is bcrypt format
- [ ] Keys saved to `dev-api-keys.txt`

### 4.2 Test Unauthenticated Request

```powershell
$body = @{
  conversation = "Human: Hello\nAssistant: Hi there!"
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/analyze `
  -H "Content-Type: application/json" `
  -d $body
```

**Expected Response**:
```json
{
  "detail": "API key required"
}
```

**Validation**:
- [ ] Returns 401 Unauthorized
- [ ] Clear error message
- [ ] Rate limiting still applies to unauthenticated requests

### 4.3 Test Authenticated Request

```powershell
$key = "dev_YOUR_KEY_HERE"  # From step 4.1
$body = @{
  conversation = "Human: Hello\nAssistant: Hi there!"
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/analyze `
  -H "X-API-Key: $key" `
  -H "Content-Type: application/json" `
  -d $body
```

**Expected Response**: (Takes 5-15 seconds)
```json
{
  "analysis_id": "uuid-here",
  "dialectic_patterns": [ ... ],
  "themes": [ ... ],
  "sentiment": { ... },
  "metadata": {
    "processing_time": 8.5,
    "conversation_length": 123
  }
}
```

**Validation**:
- [ ] Returns 200 OK
- [ ] Analysis contains dialectic_patterns
- [ ] Contains themes array
- [ ] Sentiment scores present
- [ ] Processing time < 30 seconds

---

## Phase 5: Analysis Functionality

### 5.1 Simple Conversation Analysis

```powershell
$key = "dev_YOUR_KEY_HERE"
$body = @{
  conversation = "Human: What is the capital of France?`nAssistant: The capital of France is Paris."
  options = @{
    pattern_types = @("dialectic", "themes", "sentiment")
  }
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/analyze `
  -H "X-API-Key: $key" `
  -H "Content-Type: application/json" `
  -d $body
```

**Validation**:
- [ ] Returns within 10 seconds
- [ ] Patterns detected (may be minimal for simple conversation)
- [ ] No errors in response
- [ ] Confidence scores between 0.0-1.0

### 5.2 Multi-Turn Conversation

```powershell
$key = "dev_YOUR_KEY_HERE"
$conversation = @"
Human: I've been thinking about the nature of consciousness.
Assistant: That's a profound topic. What aspects interest you most?
Human: Whether AI systems like you could ever be truly conscious.
Assistant: That raises deep questions about the nature of experience itself.
"@

$body = @{
  conversation = $conversation
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/analyze `
  -H "X-API-Key: $key" `
  -H "Content-Type: application/json" `
  -d $body
```

**Validation**:
- [ ] Detects multiple dialectic patterns
- [ ] Themes include philosophical concepts
- [ ] Sentiment shows thoughtful tone
- [ ] Processing time scales reasonably (< 30s)

### 5.3 Edge Case: Empty Conversation

```powershell
$key = "dev_YOUR_KEY_HERE"
$body = @{
  conversation = ""
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/analyze `
  -H "X-API-Key: $key" `
  -H "Content-Type: application/json" `
  -d $body
```

**Expected Response**:
```json
{
  "detail": "Conversation text cannot be empty"
}
```

**Validation**:
- [ ] Returns 422 Unprocessable Entity
- [ ] Error message is clear
- [ ] Doesn't attempt analysis

### 5.4 Edge Case: Malformed Input

```powershell
$key = "dev_YOUR_KEY_HERE"
$body = @{
  conversation = "<script>alert('xss')</script>"
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/analyze `
  -H "X-API-Key: $key" `
  -H "Content-Type: application/json" `
  -d $body
```

**Validation**:
- [ ] Input is sanitized
- [ ] No script execution risk
- [ ] Analysis completes or rejects cleanly

---

## Phase 6: Rate Limiting

### 6.1 Public Tier Limits

Without API key, make 6 requests rapidly:

```powershell
1..6 | ForEach-Object {
  curl http://localhost:8000/health
  Write-Host "Request $_ sent"
}
```

**Expected Behavior**:
- First 5 requests: Return 200 OK
- 6th request: Returns 429 Too Many Requests

**Response Headers to Check**:
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 60
```

**Validation**:
- [ ] Rate limit enforces after 5 requests
- [ ] Headers show remaining quota
- [ ] Reset time is 60 seconds
- [ ] Error message explains limit

### 6.2 API Key Tier Limits

With API key, higher limits apply:

```powershell
$key = "dev_YOUR_KEY_HERE"
1..25 | ForEach-Object {
  curl http://localhost:8000/health -H "X-API-Key: $key"
  Write-Host "Request $_ sent"
}
```

**Expected Behavior**:
- First 20 requests: Return 200 OK
- 21st request: Returns 429

**Validation**:
- [ ] API key tier allows 20 requests/minute
- [ ] Rate limit is per-key, not per-IP
- [ ] Headers show correct tier limits

---

## Phase 7: Web Interface (Phase 4)

### 7.1 Access Web UI

Open in browser:
```
http://localhost:8000/
```

**If Phase 4 is complete, expect**:
- [ ] Static HTML page loads
- [ ] Form to input conversation text
- [ ] "Analyze" button present
- [ ] Results display area

**If Phase 4 is not implemented**:
- [ ] Returns JSON root endpoint (see 1.2)
- [ ] This is expected - web UI is Phase 4

### 7.2 Test Web Analysis (if available)

1. Paste conversation into text area
2. Click "Analyze"
3. Wait for results

**Validation**:
- [ ] Loading indicator appears
- [ ] Results display after processing
- [ ] Patterns shown in readable format
- [ ] Export button available

---

## Phase 8: Error Handling & Recovery

### 8.1 Ollama Service Down

1. Stop Ollama: `Stop-Service ollama` (if running as service)
2. Try analysis request

**Expected**:
```json
{
  "detail": "Analysis service unavailable"
}
```

**Validation**:
- [ ] Returns 503 Service Unavailable
- [ ] Error message is user-friendly
- [ ] Server remains responsive
- [ ] Health check shows Ollama disconnected

3. Restart Ollama
4. Verify service reconnects

### 8.2 Database Connection

Health endpoint should show database status:

```powershell
curl http://localhost:8000/health | ConvertFrom-Json | Select-Object -ExpandProperty dependencies
```

**Validation**:
- [ ] Database shows "connected"
- [ ] Uses SQLite by default (no external DB needed)

### 8.3 Server Restart

1. Stop server (Ctrl+C)
2. Restart server
3. Verify data persistence

**Validation**:
- [ ] Server restarts cleanly
- [ ] No data loss
- [ ] API keys still work
- [ ] Rate limits reset properly

---

## Phase 9: Performance Checks

### 9.1 Response Times

Test typical request timing:

```powershell
Measure-Command {
  curl http://localhost:8000/health
}
```

**Target Times**:
- Health check: < 100ms
- Examples list: < 50ms
- Simple analysis: < 15 seconds
- Complex analysis: < 30 seconds

**Validation**:
- [ ] Health checks are fast
- [ ] Analysis completes within timeout
- [ ] No memory leaks over time

### 9.2 Concurrent Requests

Open 3 terminals and run analysis simultaneously:

```powershell
# Terminal 1, 2, and 3
$key = "dev_YOUR_KEY_HERE"
.\quick-start.ps1 analyze
```

**Validation**:
- [ ] All requests complete
- [ ] No race conditions
- [ ] Response times don't degrade significantly

---

## Phase 10: Logging & Observability

### 10.1 Check Server Logs

Watch console output during operations:

**Expected Log Entries**:
```
INFO: GET /health - 200 OK - 0.05s
INFO: POST /api/v1/analyze - 200 OK - 12.3s
WARNING: Rate limit exceeded for IP 127.0.0.1
```

**Validation**:
- [ ] Request logs include method, path, status, timing
- [ ] Errors are clearly logged
- [ ] No sensitive data in logs (API keys masked)

### 10.2 Database File

Check SQLite database:

```powershell
ls data/observatory.db
```

**Validation**:
- [ ] Database file exists
- [ ] File size grows with usage
- [ ] Can be backed up easily

---

## Quick Validation Script

For rapid validation, run this PowerShell script:

```powershell
# Quick validation script
Write-Host "`n=== Observatory Service Validation ===" -ForegroundColor Cyan

# 1. Health Check
Write-Host "`n1. Health Check..." -ForegroundColor Yellow
$health = curl http://localhost:8000/health 2>$null
if ($?) { Write-Host "✓ Health OK" -ForegroundColor Green } else { Write-Host "✗ Health FAIL" -ForegroundColor Red }

# 2. Examples List
Write-Host "`n2. Examples..." -ForegroundColor Yellow
$examples = curl http://localhost:8000/examples/ 2>$null
if ($?) { Write-Host "✓ Examples OK" -ForegroundColor Green } else { Write-Host "✗ Examples FAIL" -ForegroundColor Red }

# 3. API Documentation
Write-Host "`n3. API Docs..." -ForegroundColor Yellow
$docs = curl http://localhost:8000/docs 2>$null
if ($?) { Write-Host "✓ Docs OK" -ForegroundColor Green } else { Write-Host "✗ Docs FAIL" -ForegroundColor Red }

# 4. Auth Test
Write-Host "`n4. Auth Check..." -ForegroundColor Yellow
$auth = curl -X POST http://localhost:8000/api/v1/analyze -H "Content-Type: application/json" -d '{"conversation":"test"}' 2>$null
if ($auth -match "401|API key") { Write-Host "✓ Auth Required OK" -ForegroundColor Green } else { Write-Host "✗ Auth FAIL" -ForegroundColor Red }

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

Save as `validate.ps1` and run:
```powershell
.\validate.ps1
```

---

## Troubleshooting

### Server Won't Start

**Symptom**: Port already in use  
**Fix**: Change port or kill existing process
```powershell
# Find process on port 8000
netstat -ano | Select-String ":8000"
# Kill process (replace PID)
Stop-Process -Id PID
```

### Ollama Not Connecting

**Symptom**: Analysis returns 503  
**Check**:
```powershell
ollama list
curl http://localhost:11434/api/version
```
**Fix**: Ensure Ollama is running and Observer model is pulled

### API Key Not Working

**Symptom**: 401 even with key  
**Check**:
- Key format: Must start with `dev_`
- Header name: Must be `X-API-Key`
- Key in dev-api-keys.txt: Hash must match

### Rate Limit Issues

**Symptom**: 429 Too Many Requests  
**Fix**: Wait 60 seconds or restart server to reset

---

## Sign-Off Checklist

Before marking validation complete:

- [ ] All health checks pass
- [ ] API documentation accessible
- [ ] Authentication working
- [ ] Analysis returns results
- [ ] Rate limiting enforces
- [ ] Error handling graceful
- [ ] Performance acceptable
- [ ] Logs are clean

**Validated By**: _________________  
**Date**: _________________  
**Version Tested**: 0.1.0  
**Notes**: _________________________________

---

## Next Steps

After validation:
1. Document any issues found
2. Verify fixes with re-validation
3. Test in production-like environment
4. Enable Redis for production workloads
5. Configure proper API key management
6. Set up monitoring/alerts

For production deployment, see `README.md` deployment section.
