# Tasks: Atrium Observatory Service

**Input**: Design documents from `/specs/001-atrium-observatory-service/`
**Prerequisites**: plan.md (✓), spec.md (✓)
**Target**: `services/observatory/` - FastAPI microservice with Ollama integration

## Execution Flow (main)
```
1. Load plan.md from feature directory
   ✓ Extract: FastAPI, uv, SQLite, Redis, Docker, Ollama
   ✓ Structure: services/observatory/ with app/, tests/, examples/
2. Load optional design documents:
   → No contracts/ (will define API inline)
   → No data-model.md (entities in plan)
   → No research.md (decisions in plan)
3. Generate tasks by category:
   ✓ Setup: Project init, uv, Docker
   ✓ Tests: Endpoint tests, analyzer tests
   ✓ Core: Analyzer engine, endpoints, validators
   ✓ Integration: DB, auth, rate limiting
   ✓ Polish: Examples, docs, production config
4. Apply task rules:
   ✓ Different files = mark [P] for parallel
   ✓ Same file = sequential (no [P])
   ✓ Tests before implementation (TDD)
5. Number tasks sequentially (T001-T055)
6. Dependencies based on 5-week phased plan
7. Parallel execution examples provided
8. Validate task completeness:
   ✓ All endpoints have tests
   ✓ All core components covered
   ✓ Migration strategy addressed
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

---

## Phase 1: Core Service (Week 1)

### Phase 1.1: Setup
- [ ] **T001** Create `services/observatory/` directory structure per plan
- [ ] **T002** Initialize uv project with `pyproject.toml` (FastAPI, SQLAlchemy, Redis dependencies)
- [ ] **T003** [P] Create `Dockerfile` for service containerization
- [ ] **T004** [P] Create `docker-compose.yml` with SQLite, Redis services
- [ ] **T005** [P] Configure ruff and mypy in `pyproject.toml`
- [ ] **T006** [P] Create `.env.example` with environment variables
- [ ] **T007** Create `app/__init__.py` and `app/main.py` with FastAPI app initialization

### Phase 1.2: Core Components - Tests First (TDD)
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [ ] **T008** [P] Test analyzer engine in `tests/unit/test_analyzer.py` (validate PatternAnalyzer migration)
- [ ] **T009** [P] Test input validator in `tests/unit/test_validator.py` (SecurityMediator patterns)
- [ ] **T010** [P] Test job manager in `tests/unit/test_jobs.py` (ProcessManager cancellation)
- [ ] **T011** [P] Contract test POST `/api/v1/analyze` in `tests/contract/test_analyze_post.py`
- [ ] **T012** [P] Contract test GET `/api/v1/analyze/{id}` in `tests/contract/test_analyze_get.py`
- [ ] **T013** [P] Contract test POST `/api/v1/analyze/{id}/cancel` in `tests/contract/test_analyze_cancel.py`
- [ ] **T014** [P] Integration test conversation analysis flow in `tests/integration/test_analysis_flow.py`

### Phase 1.3: Core Implementation (ONLY after tests are failing)

- [ ] **T015** [P] Port PatternAnalyzer to `app/core/analyzer.py` (async Ollama integration via httpx client or ollama-python async methods; implement confidence scoring 0.0-1.0 based on conversation length, pattern clarity, model certainty per FR-012)
- [ ] **T016** [P] Port SecurityMediator to `app/core/validator.py` (injection prevention)
- [ ] **T017** [P] Port ProcessManager to `app/core/jobs.py` (cancellable analysis)
- [ ] **T018** [P] Create config management in `app/core/config.py` (environment vars, settings)
- [ ] **T019** [P] Create Pydantic schemas in `app/models/schemas.py` (AnalysisRequest, AnalysisResponse with confidence_score field)
- [ ] **T020** Create SQLAlchemy models in `app/models/database.py` (Analysis table with TTL)
- [ ] **T021** Database initialization and migrations in `app/models/database.py`
- [ ] **T021A** Implement TTL enforcement via scheduled cleanup job (APScheduler or FastAPI BackgroundTasks) for analysis results (30-day TTL) and metadata (90-day TTL) in `app/models/database.py` (FR-013)
- [ ] **T021B** Implement audit logging for all analysis requests and retention events in `app/core/logging.py` (FR-013 compliance)
- [ ] **T021C** [P] Test TTL expiration and automated cleanup in `tests/unit/test_ttl.py` (verify 30/90-day enforcement)
- [ ] **T022** POST `/api/v1/analyze` endpoint in `app/api/v1/analyze.py`
- [ ] **T023** GET `/api/v1/analyze/{id}` endpoint in `app/api/v1/analyze.py`
- [ ] **T024** POST `/api/v1/analyze/{id}/cancel` endpoint in `app/api/v1/analyze.py`
- [ ] **T025** GET `/health` endpoint in `app/api/v1/health.py`
- [ ] **T026** Wire endpoints to FastAPI app in `app/main.py`

---

## Phase 2: Authentication & Rate Limiting (Week 2)

### Phase 2.1: Auth - Tests First
- [ ] **T027** [P] Test public tier access in `tests/integration/test_auth_public.py`
- [ ] **T028** [P] Test API key validation in `tests/unit/test_auth.py`
- [ ] **T029** [P] Test rate limiting enforcement in `tests/unit/test_ratelimit.py`

### Phase 2.2: Auth Implementation
- [ ] **T030** [P] API key authentication middleware in `app/middleware/auth.py`
- [ ] **T031** [P] Rate limiter with Redis in `app/middleware/ratelimit.py` (10/60/600 req/min tiers)
- [ ] **T032** Apply middleware to FastAPI app in `app/main.py`
- [ ] **T033** GET `/metrics` endpoint (authenticated) in `app/api/v1/health.py`

---

## Phase 3: Batch Processing (Week 3)

### Phase 3.1: Batch - Tests First
- [ ] **T034** [P] Test batch job submission in `tests/contract/test_analyze_batch.py`
- [ ] **T035** [P] Test job queue management in `tests/unit/test_queue.py`
- [ ] **T036** [P] Test webhook notifications in `tests/integration/test_webhooks.py`

### Phase 3.2: Batch Implementation
- [ ] **T037** [P] Redis job queue in `app/core/queue.py` (enforce max 1,000 conversations per batch per FR-011)
- [ ] **T038** [P] Async worker process in `app/core/worker.py` (batch analysis)
- [ ] **T039** POST `/api/v1/analyze/batch` endpoint in `app/api/v1/analyze.py` (validate batch size ≤1,000 conversations, reject oversized batches with 400 error)
- [ ] **T040** GET `/api/v1/analyze/batch/{id}` endpoint in `app/api/v1/analyze.py`
- [ ] **T041** Webhook notification system in `app/core/notifications.py`
- [ ] **T042** Job cancellation and reprioritization in `app/core/queue.py`

---

## Phase 4: Web Interface & Examples (Week 4)

### Phase 4.1: Examples Management
- [ ] **T043** [P] Create `services/observatory/examples/` directory with sample conversations
- [ ] **T044** [P] Example manifest JSON in `examples/manifest.json` (categories, metadata)
- [ ] **T045** [P] Contract test GET `/examples` in `tests/contract/test_examples.py`
- [ ] **T046** [P] Contract test GET `/examples/{name}` in `tests/contract/test_examples_get.py`
- [ ] **T047** GET `/examples` endpoint in `app/api/v1/examples.py`
- [ ] **T048** GET `/examples/{name}` endpoint in `app/api/v1/examples.py`

### Phase 4.2: Export Functionality (FR-014)
- [ ] **T049** [P] Test export formats in `tests/unit/test_export.py` (JSON, CSV, Markdown)
- [ ] **T050** Export utility in `app/core/export.py` (format conversion)
- [ ] **T051** Add export parameter to GET `/api/v1/analyze/{id}` endpoint

---

## Phase 5: Production Readiness (Week 5)

### Phase 5.1: Observability
- [ ] **T052** [P] Structured logging configuration in `app/core/logging.py`
- [ ] **T053** [P] Prometheus metrics collection in `app/core/metrics.py`
- [ ] **T054** [P] Error reporting and monitoring setup

### Phase 5.2: Polish & Documentation
- [ ] **T055** [P] Generate OpenAPI spec and serve at `/docs`
- [ ] **T056** [P] Create `services/observatory/README.md` (setup, usage, API docs)
- [ ] **T057** [P] Update root `README.md` with Observatory service link
- [ ] **T058** [P] Create deployment guide in `services/observatory/DEPLOY.md` (include HTTPS/TLS configuration requirements for production)
- [ ] **T059** Performance testing and optimization: Test with 5 concurrent users analyzing 1K-10K message conversations using k6 or locust; verify <30s analysis completion, <200ms API response times (excluding analysis duration)
- [ ] **T060** Security audit (injection patterns, rate limit bypass)

---

## Dependencies

### Critical Paths
- **T001-T007** (Setup) blocks everything
- **T008-T014** (Tests) blocks **T015-T026** (Core Implementation)
- **T020-T021** (Database) blocks **T022-T024** (Endpoints)
- **T027-T029** (Auth Tests) blocks **T030-T033** (Auth Impl)
- **T034-T036** (Batch Tests) blocks **T037-T042** (Batch Impl)
- **T015** (Analyzer) blocks **T022** (Analyze endpoint)
- **T016** (Validator) blocks **T022** (Input validation)
- **T017** (Jobs) blocks **T024** (Cancel endpoint)

### Phase Blockers
- Phase 1 must complete before Phase 2
- Phase 2 auth middleware blocks Phase 3 (batch needs auth)
- Phase 1-3 APIs block Phase 4 (examples endpoint)
- Everything blocks Phase 5 (polish)

---

## Parallel Execution Examples

### Phase 1 Setup (Launch together)
```bash
Task: "Create Dockerfile for service"
Task: "Create docker-compose.yml"
Task: "Configure ruff and mypy"
Task: ".env.example with environment variables"
```

### Phase 1 Tests (Launch together after setup)
```bash
Task: "Test analyzer engine in tests/unit/test_analyzer.py"
Task: "Test input validator in tests/unit/test_validator.py"
Task: "Test job manager in tests/unit/test_jobs.py"
Task: "Contract test POST /api/v1/analyze"
Task: "Contract test GET /api/v1/analyze/{id}"
Task: "Contract test POST /api/v1/analyze/{id}/cancel"
Task: "Integration test conversation analysis flow"
```

### Phase 1 Core (Launch together after tests fail)
```bash
Task: "Port PatternAnalyzer to app/core/analyzer.py"
Task: "Port SecurityMediator to app/core/validator.py"
Task: "Port ProcessManager to app/core/jobs.py"
Task: "Create config in app/core/config.py"
Task: "Pydantic schemas in app/models/schemas.py"
```

### Phase 5 Polish (Launch together)
```bash
Task: "Structured logging config"
Task: "Prometheus metrics"
Task: "README.md documentation"
Task: "DEPLOY.md guide"
```

---

## Notes

- **[P] tasks** = Different files, no dependencies
- **Verify tests FAIL** before implementing (TDD)
- **Commit after each task** for clean history
- **Port existing code** from `/Projects/Atrium/apps/observatory/` where applicable
- **Ethical boundaries**: No direct filesystem access to private archives
- **Manual curation**: Examples added via groundskeeper workflow only

---

## Validation Checklist

- [x] All endpoints have corresponding contract tests
- [x] All core components (analyzer, validator, jobs) have unit tests
- [x] All tests come before implementation (TDD enforced)
- [x] Parallel tasks are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] All 14 functional requirements have task coverage
- [x] Migration strategy from Flask Observatory addressed
- [x] Constitution compliance maintained throughout
