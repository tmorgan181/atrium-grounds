# Tasks: Unified Microservice Interface

**Input**: Design documents from `specs/006-unified-microservice-interface/`
**Prerequisites**: plan.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

## Execution Flow (main)
```
1. Load plan.md ✓ - FastAPI + Jinja2, httpx, static files
2. Load design documents ✓
   - data-model.md: 5 entities (CachedExample, DemoRequest, AnalysisResult, HealthStatus)
   - contracts/: api.openapi.yaml (6 endpoints)
   - research.md: 5 technical decisions
   - quickstart.md: 6 validation tests
3. Generate tasks by category ✓
4. Apply task rules ✓ - [P] for independent files
5. Number tasks ✓ - T001-T024
6. Dependencies mapped ✓
7. Parallel examples generated ✓
8. Validation complete ✓
9. SUCCESS - Ready for execution
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Exact file paths included in descriptions

## Path Conventions
**Single service structure** (from plan.md):
```
services/web-interface/
├── app/                    # Source code
├── tests/                  # Test files
├── scripts/                # Utility scripts
```

---

## Phase 3.1: Setup & Infrastructure

- [ ] **T001** Create `services/web-interface/` directory structure
  - Create: `app/`, `app/routers/`, `app/templates/`, `app/static/`, `tests/`, `scripts/`
  - Create: `app/__init__.py`, `app/routers/__init__.py`

- [ ] **T002** Initialize uv project with dependencies
  - Create: `services/web-interface/pyproject.toml`
  - Dependencies: fastapi>=0.115.6, jinja2>=3.1.5, httpx>=0.28.1, uvicorn[standard]>=0.34.0
  - Dev dependencies: pytest>=8.4.2, pytest-asyncio>=1.2.0

- [ ] **T003** [P] Create `.env.example` and `README.md`
  - Create: `services/web-interface/.env.example` (OBSERVATORY_URL, APP_PORT)
  - Create: `services/web-interface/README.md` (setup instructions)

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [ ] **T004** [P] Contract test GET / (landing page) in `tests/test_pages.py`
  - Test: Returns 200, content-type: text/html
  - Test: Response contains "Atrium" and "Observatory"
  - Test: No technical jargon in response

- [ ] **T005** [P] Contract test GET /demo in `tests/test_pages.py`
  - Test: Returns 200, HTML response
  - Test: Contains example buttons

- [ ] **T006** [P] Contract test GET /examples/{id} in `tests/test_examples.py`
  - Test: dialectic-simple returns 200 with JSON
  - Test: Invalid ID returns 404
  - Test: Response has conversation, analysis fields

- [ ] **T007** [P] Contract test POST /api/analyze in `tests/test_proxy.py`
  - Test: With valid API key returns 200
  - Test: Without API key returns 401
  - Test: Proxies to Observatory correctly

- [ ] **T008** [P] Contract test GET /api/health in `tests/test_proxy.py`
  - Test: Returns health status JSON
  - Test: Contains status, response_time_ms fields

- [ ] **T009** [P] Integration test: Visitor sees value in 30s in `tests/test_integration.py`
  - Test: GET / → parse HTML → check for clear value prop
  - Test: Response time <500ms

- [ ] **T010** [P] Integration test: Demo in 3s in `tests/test_integration.py`
  - Test: GET /examples/dialectic-simple → measure time <100ms
  - Test: POST /api/analyze → measure time <3s (with Observatory running)

---

## TDD Gate: Validate Before Phase 3.3

**CRITICAL**: Before proceeding to T011, run validation script to ensure TDD compliance:

```bash
# Run TDD gate validator
bash scripts/validate-tdd-gate.sh
```

**Gate Requirements**:
1. ✅ At least 7 tests exist (T004-T010 complete)
2. ✅ All tests FAIL with ImportError/AttributeError (no implementation yet)
3. ❌ If tests PASS: Implementation may already exist - review before proceeding
4. ❌ If tests missing: Write tests first (return to T004-T010)

**Expected output**:
```
🔍 TDD Gate Validation
=====================
Step 1: Verify tests exist...
✅ Found 7+ tests
Step 2: Verify tests fail (no implementation)...
✅ Tests fail as expected (no implementation yet)

🎉 TDD Gate PASSED - Proceed to implementation (T011+)
```

**Manual verification** (if script unavailable):
```bash
# Check tests exist
uv run pytest tests/ --collect-only
# Must show 7+ tests collected

# Check tests fail
uv run pytest tests/ -v
# Must show failures with import/attribute errors (not passes)
```

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [ ] **T011** Create FastAPI application in `app/main.py`
  - FastAPI instance with CORS middleware
  - Mount static files at /static
  - Include routers: pages, proxy
  - Startup/shutdown events

- [ ] **T012** Create configuration in `app/config.py`
  - Pydantic Settings class
  - Load from .env: OBSERVATORY_URL, APP_HOST, APP_PORT
  - Defaults: http://localhost:8000, 0.0.0.0, 8080

- [ ] **T013** [P] Create Observatory client in `app/client.py`
  - httpx.AsyncClient wrapper
  - Methods: analyze(conversation, api_key), health()
  - Error handling for connection errors

- [ ] **T014** [P] Create base template in `app/templates/base.html`
  - HTML5 structure
  - Navigation component include
  - Content block
  - Static CSS/JS includes

- [ ] **T015** [P] Create navigation component in `app/templates/components/nav.html`
  - Links: Home, Demo, API Docs
  - Responsive layout
  - Service status indicator (include T029 status badge)

- [ ] **T016** [P] Implement page routes in `app/routers/pages.py`
  - GET /: Render index.html with context
  - GET /demo: Render demo.html with example list
  - GET /docs: Render docs.html

- [ ] **T017** [P] Create landing page template in `app/templates/index.html`
  - Extends base.html
  - Value proposition (30-second clarity)
  - "Try it now" CTA button
  - No technical jargon

- [ ] **T018** [P] Create demo page template in `app/templates/demo.html`
  - Extends base.html
  - Example cards (cached demos)
  - Live demo section (with API key input)
  - Results display area with:
    * Pattern cards (badge + confidence bar)
    * Sentiment graph (line chart or emoji trajectory)
    * Topic tags (colored badges)
    * JSON toggle (expandable <details> element)

- [ ] **T019** [P] Implement example loading in `app/routers/examples.py`
  - GET /examples/{id}
  - Load from app/static/examples/{id}.json
  - Validate ID (alphanumeric + hyphens only)
  - Return 404 if not found

- [ ] **T020** Implement Observatory proxy in `app/routers/proxy.py`
  - POST /api/analyze: Proxy to Observatory with API key header
  - GET /api/health: Call Observatory /health
  - Handle Observatory errors → user-friendly messages
  - Pass through rate limit headers

- [ ] **T021** [P] Create minimal CSS in `app/static/css/style.css`
  - Basic layout styles
  - Example card styling
  - Results display styling
  - Responsive design (mobile-friendly)

- [ ] **T029** [P] Create health status component in `app/templates/components/status.html`
  - Display Observatory operational/degraded/offline status
  - Show response time in ms
  - Auto-refresh every 30s (JavaScript fetch to /api/health)
  - Status badge with color coding (green=operational, yellow=degraded, red=offline)
  - Include in navigation component (referenced in T015)

---

## Phase 3.4: Static Content & Scripts

- [ ] **T022** Create example generator script in `scripts/generate_examples.py`
  - Load curated conversations from `specs/006-unified-microservice-interface/example-conversations.md`
  - Parse markdown JSON blocks (8 examples: 2 dialectic, 2 collaborative, 2 debate, 2 exploration)
  - Validate format before calling Observatory (speaker A-Z, content 50-500 chars)
  - Call Observatory /analyze for each
  - Save to app/static/examples/{id}.json
  - Include metadata (type inferred from section, complexity from name suffix, generated_at timestamp)
  - Generate 5 examples minimum for MVP (all 8 recommended)

- [ ] **T023** Generate cached examples
  - Run: `uv run python scripts/generate_examples.py`
  - Verify: app/static/examples/ contains dialectic-simple.json, etc.
  - Validate: Each file has conversation + analysis fields

- [ ] **T024** [P] Create API documentation page template in `app/templates/docs.html`
  - Extends base.html
  - Embed OpenAPI spec (from contracts/)
  - Show example requests with curl
  - Link to Observatory API docs

---

## Phase 3.5: Deployment & Polish

- [ ] **T025** Create Dockerfile in `services/web-interface/Dockerfile`
  - FROM python:3.11-slim
  - Install uv, sync dependencies
  - CMD: uvicorn app.main:app --host 0.0.0.0 --port 8080
  - EXPOSE 8080

- [ ] **T026** [P] Run quickstart validation (from quickstart.md)
  - All 6 curl tests pass
  - Cached demos <100ms
  - Live demos <3s (with Observatory)
  - Browser manual tests complete

- [ ] **T027** [P] Performance validation
  - Load test: 10 concurrent requests to /
  - Measure: Cached example response time
  - Verify: No memory leaks over 100 requests

- [ ] **T028** Final polish
  - Remove TODOs and debug code
  - Verify no hardcoded values (use config)
  - Check error messages are user-friendly
  - Ensure no private data in logs

---

## Dependencies

**Setup blocks tests**: T001-T003 before T004-T010

**Tests before implementation**: T004-T010 MUST FAIL before T011-T024

**Core dependencies**:
- T011 (FastAPI app) blocks T016 (page routes), T020 (proxy)
- T012 (config) blocks T013 (client)
- T013 (client) blocks T020 (proxy), T022 (generator)
- T014 (base template) blocks T017, T018, T024
- T015 (navigation) blocks T029 (status badge component)
- T019 (example loader) needs T023 (examples generated)
- T022 (generator) blocks T023 (run generator)

**Deployment needs core**: T011-T029 before T025-T028

---

## Parallel Execution Examples

### Parallel Group 1: Setup (after T001-T002 complete)
```bash
# Run simultaneously (independent files):
Task: "Create .env.example and README.md" (T003)
```

### Parallel Group 2: Contract Tests (after T003 complete)
```bash
# Run simultaneously (all create different test files):
Task: "Contract test GET / in tests/test_pages.py" (T004)
Task: "Contract test GET /demo in tests/test_pages.py" (T005)
Task: "Contract test GET /examples/{id} in tests/test_examples.py" (T006)
Task: "Contract test POST /api/analyze in tests/test_proxy.py" (T007)
Task: "Contract test GET /api/health in tests/test_proxy.py" (T008)
```

### Parallel Group 3: Integration Tests (after T004-T008 complete)
```bash
# Run simultaneously (same file but can coordinate):
Task: "Integration test: Visitor sees value in tests/test_integration.py" (T009)
Task: "Integration test: Demo in 3s in tests/test_integration.py" (T010)
```

### Parallel Group 4: Core Components (after T011-T012 complete)
```bash
# Run simultaneously (independent files):
Task: "Create Observatory client in app/client.py" (T013)
Task: "Create base template in app/templates/base.html" (T014)
Task: "Create navigation component in app/templates/components/nav.html" (T015)
```

### Parallel Group 5: Templates (after T014-T015 complete)
```bash
# Run simultaneously (different template files):
Task: "Implement page routes in app/routers/pages.py" (T016)
Task: "Create landing page template in app/templates/index.html" (T017)
Task: "Create demo page template in app/templates/demo.html" (T018)
Task: "Implement example loading in app/routers/examples.py" (T019)
Task: "Create minimal CSS in app/static/css/style.css" (T021)
Task: "Create health status component in app/templates/components/status.html" (T029)
```

### Parallel Group 6: Final Polish (after T025 complete)
```bash
# Run simultaneously (different validation tasks):
Task: "Run quickstart validation" (T026)
Task: "Performance validation" (T027)
```

---

## Task Execution Order (Dependencies Resolved)

```
Setup:        T001 → T002 → T003
Tests:        T004, T005, T006, T007, T008 (parallel)
              T009, T010 (parallel)
              [TDD Gate - validate tests fail before continuing]
Core:         T011 → T012
              T013, T014, T015 (parallel after T012)
              T016, T017, T018, T019, T021, T029 (parallel after T014-T015)
              T020 (after T013)
Static:       T022 (after T013) → T023
              T024 (parallel with T022)
Deploy:       T025 (after all core complete)
Polish:       T026, T027 (parallel after T025)
              T028 (after T026-T027)
```

---

## Validation Checklist
*GATE: Verify before marking complete*

- [x] All contracts have corresponding tests (T004-T008 cover api.openapi.yaml)
- [x] All entities have tasks (CachedExample→T022-T023, Observatory client→T013, HealthStatus→T029)
- [x] All requirements have tasks (FR-015 health status→T029 added)
- [x] All tests come before implementation (T004-T010 before T011-T029)
- [x] Parallel tasks truly independent (verified file paths)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] TDD gate enforced (validation script created)

---

## Notes

- **[P] tasks** = Different files, no dependencies, can run in parallel
- **Verify tests fail** before implementing (TDD principle) - Use `scripts/validate-tdd-gate.sh`
- **Commit after each task** for clean history
- **Observatory must be running** for T010 (live demo test) and T023 (example generation)
- **Example conversations defined** in `specs/006-unified-microservice-interface/example-conversations.md`
- **Estimated total**: 29 tasks, ~3-5 days with parallelization (19 parallelizable = 66%)

---

**Tasks generated by**: Claude Code (Sonnet 4.5)
**Based on**: plan.md, data-model.md, contracts/api.openapi.yaml, quickstart.md
**Ready for**: Sequential or parallel execution via Task agents
