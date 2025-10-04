# Task Delegation Proposal: Phase 1 Endpoints & Phase 2 Auth/Rate Limiting

**To**: GitHub Copilot
**From**: Claude (Primary Agent)
**Date**: 2025-10-04
**Status**: Ready for Review

---

## Executive Summary

Claude has completed the core algorithmic components of the Observatory service (analyzer, validator, job manager). This proposal delegates the remaining Phase 1 infrastructure tasks (database, API endpoints) and all of Phase 2 (authentication, rate limiting) to Copilot for parallel implementation.

This enables Claude to proceed with Phase 3 (complex batch processing) while Copilot handles well-defined infrastructure and middleware tasks that align with its documented strengths.

---

## Background: Current Implementation Status

### ✅ Completed by Claude (T001-T019)

**Phase 1.1: Setup**
- Project structure, pyproject.toml, Docker configuration
- Environment management (.env.example)
- FastAPI app initialization

**Phase 1.2: Tests (TDD)**
- Unit tests for analyzer, validator, jobs (all passing)
- Contract tests for all API endpoints
- Integration tests for end-to-end flows

**Phase 1.3: Core Components**
- `app/core/analyzer.py` - Pattern analysis engine (9/9 tests passing)
- `app/core/validator.py` - Input validation and security (13/13 tests passing)
- `app/core/jobs.py` - Cancellable async job manager
- `app/core/config.py` - Configuration management
- `app/models/schemas.py` - Pydantic request/response models

### 📋 Available for Implementation

All core business logic is implemented and tested. The following tasks require integration and infrastructure work:

- Database layer (SQLAlchemy models, TTL enforcement)
- API endpoint implementation (wire schemas to core components)
- Authentication middleware
- Rate limiting middleware

---

## Delegation Scope: Tasks T020-T033

### Phase 1.3 Completion: Database & Endpoints (T020-T026)

#### T020: SQLAlchemy Models (`app/models/database.py`)

**Objective**: Create database models for persisting analysis results

**Requirements**:
- `Analysis` model with fields:
  - `id` (UUID, primary key)
  - `conversation_text` (Text)
  - `status` (Enum: pending, processing, completed, failed, cancelled)
  - `observer_output` (Text, nullable)
  - `patterns` (JSON, nullable)
  - `confidence_score` (Float, nullable)
  - `processing_time` (Float, nullable)
  - `created_at` (DateTime)
  - `last_accessed_at` (DateTime)
  - `expires_at` (DateTime, nullable)
  - `error` (Text, nullable)

**Validation**: Must support both SQLite (dev) and PostgreSQL (production)

**Testing**: Create `tests/unit/test_database.py` to verify model creation and queries

---

#### T021: Database Initialization

**Objective**: Set up database connection and table creation

**Requirements**:
- Database connection management using `app/core/config.py` settings
- Async SQLAlchemy session management
- Table creation on startup
- Connection pooling configuration

**File**: `app/models/database.py` (extend)

**Testing**: Verify database tables are created correctly

---

#### T021A: TTL Enforcement (FR-013)

**Objective**: Implement scheduled cleanup for expired data

**Requirements**:
- Use APScheduler to run cleanup job every 24 hours
- Delete analysis results older than 30 days (based on `last_accessed_at`)
- Delete analysis metadata older than 90 days (based on `created_at`)
- Log cleanup events via audit logging (T021B)

**File**: `app/models/database.py` (extend with cleanup functions)

**Configuration**: Use `settings.ttl_results` and `settings.ttl_metadata` from config

**Testing**: Create `tests/unit/test_ttl.py` to verify expiration logic

---

#### T021B: Audit Logging (FR-013)

**Objective**: Log all analysis requests and retention events

**Requirements**:
- Structured logging for:
  - Analysis creation (conversation_id, timestamp, request_size)
  - Analysis completion (conversation_id, status, processing_time)
  - Analysis cancellation (conversation_id, user/system initiated)
  - TTL cleanup events (records_deleted, oldest_date)
- JSON log format when `settings.log_format == "json"`
- Configurable log level via `settings.log_level`

**File**: `app/core/logging.py` (create)

**Testing**: Verify logs are generated with correct structure

---

#### T021C: TTL Expiration Tests

**Objective**: Test TTL enforcement and cleanup

**File**: `tests/unit/test_ttl.py` (create)

**Test Cases**:
- Verify 30-day expiration for results
- Verify 90-day expiration for metadata
- Verify cleanup job deletes expired records
- Verify non-expired records are preserved

---

#### T022: POST `/api/v1/analyze` Endpoint

**Objective**: Accept conversation analysis requests

**File**: `app/api/v1/analyze.py` (create)

**Implementation**:
1. Accept `AnalysisRequest` from request body
2. Validate conversation using `InputValidator`
3. Create database record with status="pending"
4. Create async job using `JobManager.create_job()` with `AnalyzerEngine.analyze()`
5. Return `AnalysisStatusResponse` with 202 Accepted

**Error Handling**:
- 400 Bad Request: Validation failures (injection, length)
- 422 Unprocessable Entity: Invalid request schema

**Testing**: Contract tests already exist in `tests/contract/test_analyze_post.py`

---

#### T023: GET `/api/v1/analyze/{id}` Endpoint

**Objective**: Retrieve analysis results

**File**: `app/api/v1/analyze.py` (extend)

**Implementation**:
1. Query database for analysis by ID
2. Update `last_accessed_at` timestamp (for TTL)
3. If status="completed", return full `AnalysisResponse`
4. If status="processing/pending", return `AnalysisStatusResponse`
5. If status="failed", include error message

**Error Handling**:
- 404 Not Found: Analysis ID doesn't exist or expired

**Testing**: Contract tests already exist in `tests/contract/test_analyze_get.py`

---

#### T024: POST `/api/v1/analyze/{id}/cancel` Endpoint

**Objective**: Cancel ongoing analysis

**File**: `app/api/v1/analyze.py` (extend)

**Implementation**:
1. Query database for analysis by ID
2. Check if status allows cancellation (pending/processing)
3. Call `JobManager.cancel_job(job_id)`
4. Update database status to "cancelled"
5. Return `CancelResponse`

**Error Handling**:
- 404 Not Found: Analysis ID doesn't exist
- 409 Conflict: Analysis already completed/failed

**Testing**: Contract tests already exist in `tests/contract/test_analyze_cancel.py`

---

#### T025: GET `/health` Endpoint

**Objective**: Health check for monitoring

**File**: `app/api/v1/health.py` (create)

**Implementation**:
```python
@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=__version__
    )
```

**Testing**: Verify 200 OK response with correct schema

---

#### T026: Wire Endpoints to FastAPI App

**Objective**: Register all routers in main app

**File**: `app/main.py` (extend)

**Implementation**:
```python
from app.api.v1 import analyze, health

app.include_router(analyze.router, prefix="/api/v1", tags=["analysis"])
app.include_router(health.router, tags=["health"])
```

**Testing**: Run integration tests to verify all endpoints accessible

---

### Phase 2: Authentication & Rate Limiting (T027-T033)

#### T027: Test Public Tier Access

**Objective**: Verify endpoints work without authentication

**File**: `tests/integration/test_auth_public.py` (create)

**Test Cases**:
- POST /api/v1/analyze succeeds without auth
- Rate limits are enforced (10 req/min for public tier)

---

#### T028: Test API Key Validation

**Objective**: Verify API key authentication

**File**: `tests/unit/test_auth.py` (create)

**Test Cases**:
- Valid API key grants access
- Invalid API key returns 401
- Missing API key defaults to public tier

---

#### T029: Test Rate Limiting Enforcement

**Objective**: Verify rate limits per tier

**File**: `tests/unit/test_ratelimit.py` (create)

**Test Cases**:
- Public: 10 req/min, 500/day
- API Key: 60 req/min, 5K/day
- Partner: 600 req/min, 50K/day
- Rate limit headers present in responses

---

#### T030: API Key Authentication Middleware

**Objective**: Implement API key validation

**File**: `app/middleware/auth.py` (create)

**Implementation**:
- Check `Authorization: Bearer <api_key>` header
- If absent, set tier="public"
- If present, validate against stored keys (simple dict for Phase 2)
- Set `request.state.tier` for downstream use

**Configuration**: Use `settings.api_key_salt` for validation

---

#### T031: Rate Limiter with Redis

**Objective**: Implement Redis-based rate limiting

**File**: `app/middleware/ratelimit.py` (create)

**Implementation**:
- Use Redis to track request counts per IP/API key
- Enforce limits based on `request.state.tier`:
  - Public: `settings.rate_limit_public` req/min
  - API Key: `settings.rate_limit_api_key` req/min
  - Partner: `settings.rate_limit_partner` req/min
- Return 429 Too Many Requests when exceeded
- Include rate limit headers:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

**Dependencies**: Requires Redis connection via `settings.redis_url`

---

#### T032: Apply Middleware to FastAPI App

**Objective**: Register auth and rate limit middleware

**File**: `app/main.py` (extend)

**Implementation**:
```python
from app.middleware.auth import AuthMiddleware
from app.middleware.ratelimit import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)
```

**Order matters**: Auth before rate limiting

---

#### T033: GET `/metrics` Endpoint (Authenticated)

**Objective**: Provide usage metrics for authenticated users

**File**: `app/api/v1/health.py` (extend)

**Implementation**:
- Require authentication (API key or higher)
- Return request counts, rate limit status
- Return database statistics (total analyses, avg processing time)

**Error Handling**:
- 401 Unauthorized: No valid API key

---

## Integration Points: What You'll Use

### Core Components (Already Implemented)

```python
# Analyzer
from app.core.analyzer import AnalyzerEngine

analyzer = AnalyzerEngine(
    ollama_base_url=settings.ollama_base_url,
    model=settings.ollama_model
)
result = await analyzer.analyze(conversation_text)
```

```python
# Validator
from app.core.validator import InputValidator

validator = InputValidator(max_length=settings.max_conversation_length)
validation = validator.validate(conversation_text)

if not validation.is_valid:
    raise HTTPException(status_code=400, detail=validation.error)
```

```python
# Job Manager
from app.core.jobs import JobManager

job_manager = JobManager()
job_id = await job_manager.create_job(
    analyzer.analyze,
    conversation_text,
    timeout=settings.analysis_timeout
)
```

```python
# Config
from app.core.config import settings

# All environment variables available as:
settings.database_url
settings.redis_url
settings.rate_limit_public
# etc.
```

### Schemas (Already Defined)

```python
from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatusResponse,
    CancelResponse,
    HealthResponse
)

# Use these for request/response typing
@router.post("/analyze", response_model=AnalysisStatusResponse)
async def create_analysis(request: AnalysisRequest):
    ...
```

---

## Testing Strategy

### Run Existing Tests

All core component tests are already written and passing:

```bash
# Verify core components work
uv run pytest tests/unit/test_analyzer.py -v
uv run pytest tests/unit/test_validator.py -v
uv run pytest tests/unit/test_jobs.py -v

# Contract tests will fail until endpoints implemented
uv run pytest tests/contract/ -v
```

### Write Missing Tests

You'll need to create:
- `tests/unit/test_database.py` (T020)
- `tests/unit/test_ttl.py` (T021C)
- `tests/integration/test_auth_public.py` (T027)
- `tests/unit/test_auth.py` (T028)
- `tests/unit/test_ratelimit.py` (T029)

### Integration Test Flow

Once endpoints are implemented, run:

```bash
# Should all pass if correctly wired
uv run pytest tests/contract/ -v
uv run pytest tests/integration/ -v
```

---

## Success Criteria

### Phase 1.3 Complete (T020-T026)
- ✅ Database models created and tested
- ✅ TTL enforcement working (30/90 day cleanup)
- ✅ Audit logging functional
- ✅ All three endpoints implemented (analyze, get, cancel)
- ✅ Health endpoint working
- ✅ All contract tests passing (tests/contract/)
- ✅ Integration tests passing (tests/integration/)

### Phase 2 Complete (T027-T033)
- ✅ Public tier works without auth
- ✅ API key validation working
- ✅ Rate limiting enforced per tier
- ✅ Rate limit headers present
- ✅ Metrics endpoint functional
- ✅ All auth/rate limit tests passing

---

## Coordination with Claude

### What Claude Will Work On (Parallel)

**Phase 3: Batch Processing (T034-T042)**
- Redis job queue for batch requests
- Async worker process
- Webhook notification system
- Batch analysis endpoints

### Synchronization Points

1. **After T026**: Claude will integrate batch endpoints with your database layer
2. **After T033**: Claude will apply auth/rate limiting to batch endpoints
3. **End of Week 3**: Joint code review and integration testing

### Communication Protocol

- **Commits**: Use format `feat(001): <task-id> <description>` (e.g., `feat(001): T020 database models`)
- **Blockers**: Create GitHub issue with `[BLOCKER]` prefix
- **Questions**: Tag in PR comments or create discussion in `collaboration/` folder

---

## Environment Setup

You already have everything you need:

```bash
cd services/observatory

# Install dependencies
uv sync --dev

# Run tests
uv run pytest tests/unit/ -v

# Run linter
uv run ruff check .

# Type check
uv run mypy app/
```

### Redis for Development

For rate limiting tests, start Redis:

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or via docker-compose
docker-compose up -d redis
```

---

## Questions & Clarifications

### Q: Should I use async or sync database sessions?
**A**: Use async (asyncio + SQLAlchemy async). All core components are async.

### Q: How should API keys be stored initially?
**A**: For Phase 2, use a simple in-memory dict. Production key management is Phase 5.

### Q: What if tests are blocking on implementation details?
**A**: Tests were written with expected interfaces. If something doesn't make sense, check with Claude or update the test (with justification in commit message).

### Q: Should I implement actual Ollama calls in endpoints?
**A**: No - the `AnalyzerEngine` already handles that. Just call `await analyzer.analyze()`.

---

## Acceptance & Next Steps

**For Copilot to Accept This Delegation**:
1. Review the scope and ask any clarifying questions
2. Confirm environment is set up (uv, Redis, tests passing)
3. Begin with T020 (database models) and work sequentially through T033
4. Commit after each task completion
5. Run tests continuously (`uv run pytest -v`)

**Estimated Timeline**:
- Phase 1.3 completion (T020-T026): 2-3 days
- Phase 2 completion (T027-T033): 2-3 days
- **Total**: Week 2 complete by end of sprint

---

## Appendix: File Tree Reference

```
services/observatory/
├── app/
│   ├── __init__.py ✅
│   ├── main.py ✅ (extend in T026, T032)
│   ├── api/
│   │   └── v1/
│   │       ├── analyze.py ❌ (create in T022-T024)
│   │       └── health.py ❌ (create in T025, extend in T033)
│   ├── core/
│   │   ├── analyzer.py ✅
│   │   ├── validator.py ✅
│   │   ├── jobs.py ✅
│   │   ├── config.py ✅
│   │   └── logging.py ❌ (create in T021B)
│   ├── models/
│   │   ├── schemas.py ✅
│   │   └── database.py ❌ (create in T020-T021A)
│   └── middleware/
│       ├── auth.py ❌ (create in T030)
│       └── ratelimit.py ❌ (create in T031)
├── tests/
│   ├── unit/
│   │   ├── test_analyzer.py ✅ (9/9 passing)
│   │   ├── test_validator.py ✅ (13/13 passing)
│   │   ├── test_jobs.py ✅
│   │   ├── test_database.py ❌ (create)
│   │   ├── test_ttl.py ❌ (create in T021C)
│   │   ├── test_auth.py ❌ (create in T028)
│   │   └── test_ratelimit.py ❌ (create in T029)
│   ├── contract/
│   │   ├── test_analyze_post.py ✅ (will pass after T022)
│   │   ├── test_analyze_get.py ✅ (will pass after T023)
│   │   └── test_analyze_cancel.py ✅ (will pass after T024)
│   └── integration/
│       ├── test_analysis_flow.py ✅ (will pass after T026)
│       └── test_auth_public.py ❌ (create in T027)
```

---

**Ready for Copilot review and acceptance.**

Claude will await confirmation before proceeding with Phase 3 batch processing work.

🤖 Generated by Claude Code
📅 2025-10-04
