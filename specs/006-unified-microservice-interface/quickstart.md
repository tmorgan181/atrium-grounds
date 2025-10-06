# Quickstart: Unified Microservice Interface

**Feature**: 006-unified-microservice-interface
**Purpose**: Validate web interface setup and basic functionality

## Prerequisites

- Python 3.11+
- uv package manager
- Observatory service running on http://localhost:8000
- Observatory API keys generated (dev-api-keys.txt)

## Setup

### 1. Navigate to service directory
```bash
cd services/web-interface
```

### 2. Install dependencies
```bash
uv sync
```

### 3. Configure Observatory connection
```bash
# Copy example env file
cp .env.example .env

# Edit .env and set:
OBSERVATORY_URL=http://localhost:8000
OBSERVATORY_API_KEY=<your-dev-or-partner-key>
```

### 4. Generate cached examples (first time only)
```bash
# This script calls Observatory /analyze for curated conversations
# and saves results to app/static/examples/
uv run python scripts/generate_examples.py
```

Expected output:
```
Generating cached examples...
✓ dialectic-simple.json (2.1s)
✓ dialectic-complex.json (2.3s)
✓ exploration.json (1.9s)
✓ collaborative.json (2.0s)
✓ debate.json (2.2s)

Generated 5 examples in app/static/examples/
```

### 5. Start development server
```bash
uv run uvicorn app.main:app --reload --port 8080
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Validation

### Test 1: Landing Page
```bash
curl http://localhost:8080/
```

**Expected**:
- HTTP 200 OK
- HTML response containing "Atrium Grounds" and "Observatory"
- No technical jargon (no "FastAPI", "REST", "API endpoints")

### Test 2: Cached Example
```bash
curl http://localhost:8080/examples/dialectic-simple
```

**Expected**:
```json
{
  "id": "dialectic-simple",
  "title": "Dialectic Pattern - Simple",
  "conversation": [...],
  "analysis": {
    "patterns": [...],
    "sentiment": {...},
    "topics": [...]
  }
}
```

- HTTP 200 OK
- Valid JSON with all required fields
- Analysis data present (pre-generated)

### Test 3: Demo Page
```bash
curl http://localhost:8080/demo
```

**Expected**:
- HTTP 200 OK
- HTML with example buttons
- Demo interface rendered

### Test 4: Observatory Health Check
```bash
curl http://localhost:8080/api/health
```

**Expected** (if Observatory is running):
```json
{
  "status": "operational",
  "response_time_ms": 45,
  "last_checked": "2025-01-05T14:32:10Z"
}
```

### Test 5: Live Analysis (Authenticated)
```bash
curl -X POST http://localhost:8080/api/analyze \
  -H "X-API-Key: <your-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": [
      {"speaker": "A", "content": "What is truth?"},
      {"speaker": "B", "content": "Truth is subjective."}
    ]
  }'
```

**Expected**:
- HTTP 200 OK (if API key valid)
- JSON response with analysis (patterns, sentiment, topics)
- Response time <3s

### Test 6: Rate Limiting
```bash
# Make 101 requests rapidly (exceeds public tier limit of 100/min)
for i in {1..101}; do
  curl -s http://localhost:8080/api/health > /dev/null
done
```

**Expected**:
- First 100 requests: HTTP 200
- 101st request: HTTP 429 (rate limit exceeded)

## Browser Testing

### Manual Test Flow

1. **Open landing page**: http://localhost:8080/
   - Verify: Clear value proposition visible within 10 seconds
   - Verify: "Try it now" button present
   - Verify: No technical jargon

2. **Click "Try Example" button**
   - Verify: Results appear instantly (<100ms)
   - Verify: Patterns, sentiment, topics displayed
   - Verify: Visual presentation (not just raw JSON)

3. **Click "Try Live Demo" button**
   - Verify: Results appear within 3 seconds
   - Verify: Same Observatory analysis shown
   - Verify: Status indicator shows "Analyzing..."

4. **Navigate to API docs**: http://localhost:8080/docs
   - Verify: OpenAPI spec embedded
   - Verify: Example requests shown
   - Verify: Clear auth instructions

5. **Test custom analysis** (requires API key):
   - Enter API key in UI
   - Paste conversation
   - Submit
   - Verify: Analysis results displayed
   - Verify: Error handling for invalid key

## Performance Validation

### Cached Demo Performance
```bash
# Measure 10 cached example requests
for i in {1..10}; do
  curl -w "%{time_total}\n" -o /dev/null -s http://localhost:8080/examples/dialectic-simple
done
```

**Expected**: All responses <100ms

### Live Demo Performance
```bash
# Measure 5 live analysis requests (with auth)
for i in {1..5}; do
  curl -w "%{time_total}\n" -o /dev/null -s \
    -X POST http://localhost:8080/api/analyze \
    -H "X-API-Key: <key>" \
    -H "Content-Type: application/json" \
    -d '{"conversation": [...]}'
done
```

**Expected**: All responses <3s (depends on Observatory performance)

### Concurrent User Test
```bash
# Simulate 10 concurrent users
seq 10 | xargs -P10 -I{} curl -s http://localhost:8080/ > /dev/null
```

**Expected**: All requests succeed, no errors

## Troubleshooting

### Issue: Observatory connection refused
**Symptom**: `curl http://localhost:8080/api/health` returns 503

**Solution**:
1. Verify Observatory is running: `curl http://localhost:8000/health`
2. Check `.env` has correct `OBSERVATORY_URL`
3. Ensure no firewall blocking port 8000

### Issue: Cached examples missing
**Symptom**: `curl http://localhost:8080/examples/dialectic-simple` returns 404

**Solution**:
1. Run example generation: `uv run python scripts/generate_examples.py`
2. Verify files exist: `ls app/static/examples/`
3. Check Observatory is accessible (script needs it to generate)

### Issue: API key authentication fails
**Symptom**: `curl -X POST .../api/analyze` with key returns 401

**Solution**:
1. Verify API key is valid: Test directly on Observatory (`curl -H "X-API-Key: <key>" http://localhost:8000/examples`)
2. Check header name is `X-API-Key` (not `Authorization`)
3. Ensure key has appropriate tier (api-key or partner, not public)

### Issue: Rate limiting too strict
**Symptom**: Getting 429 errors with few requests

**Solution**:
1. Check Observatory rate limits: Public=100/min, API-key=1000/min, Partner=5000/min
2. Use higher tier API key for testing
3. Wait 1 minute for rate limit window to reset

## Success Criteria

✅ All 6 curl tests pass
✅ Browser navigation flows work
✅ Cached demos <100ms
✅ Live demos <3s
✅ 10 concurrent users handled without errors
✅ No private data exposure
✅ Clean, accessible UI (no technical jargon in public pages)

## Next Steps

After quickstart validation passes:

1. Run full test suite: `uv run pytest`
2. Review HTML templates for UX consistency
3. Load test with more concurrent users (50+)
4. Deploy to staging environment
5. Generate production-ready cached examples

---

**Quickstart by**: Claude Code (Sonnet 4.5)
**Based on**: data-model.md, contracts/api.openapi.yaml
