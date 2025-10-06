# Implementation Plan: Unified Microservice Interface

**Branch**: `006-unified-microservice-interface` | **Date**: 2025-01-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/006-unified-microservice-interface/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path ✓
2. Fill Technical Context ✓
3. Fill Constitution Check ✓
4. Evaluate Constitution Check → PASS ✓
5. Execute Phase 0 → research.md ✓
6. Execute Phase 1 → contracts, data-model.md, quickstart.md ✓
7. Re-evaluate Constitution Check → PASS ✓
8. Plan Phase 2 → Task generation approach ✓
9. STOP - Ready for /tasks command ✓
```

**IMPORTANT**: The /plan command STOPS at step 8. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

Build a public-facing web interface for Atrium Grounds that exposes the Observatory conversation analysis API through an accessible, non-technical UI. Users can explore pre-cached conversation examples instantly, try live demos with rate limits, and progress to custom analysis with API keys.

**Technical Approach**: FastAPI server-side rendered web app (Jinja2 templates) acting as stateless proxy to Observatory API. Static JSON files for cached demos, no database, no auth logic (passthrough to Observatory). Estimated ~500 LOC, 3-5 day implementation.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.115+, Jinja2 3.1+, httpx 0.28+ (Observatory client), uvicorn 0.34+
**Storage**: Static JSON files (cached demo results), no database
**Testing**: pytest, httpx TestClient for integration tests
**Target Platform**: Linux server (Docker container), port 8080
**Project Type**: Single service (stateless web proxy)
**Performance Goals**: <100ms for cached demos, <3s for live API calls, handle 10 concurrent users comfortably
**Constraints**: No direct private data access, must respect Observatory rate limits, progressive disclosure tiers
**Scale/Scope**: MVP with 10-15 cached examples, ~10 HTML templates, ~500 LOC total

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check

**I. Language & Tone Standards** ✓
- Public UI uses grounded, accessible language (no "REST", "FastAPI", "endpoints" in user-facing content)
- Technical docs for developers use precise terms
- No mystical or overly ceremonious language

**II. Ethical Boundaries** ✓
- No direct access to private conversation archives
- Uses only curated public examples
- Calls Observatory API (service boundary maintained)
- No private data storage

**III. Progressive Disclosure** ✓
- Three tiers: Public (cached demos) → API Key (custom input) → Partner (production)
- Matches Observatory authentication tiers
- Clear upgrade paths shown

**IV. Multi-Interface Access** ✓
- Web UI for human exploration
- API passthrough for developer access
- OpenAPI docs embedded for AI/developer use

**V. Invitation Over Intrusion** ✓
- "Try it now" demos, no signup required
- Clear documentation and examples
- Export-friendly (API provides data formats)

**VI. Service Independence** ✓
- Separate `services/web-interface/` directory
- Own Dockerfile, independent deployment
- Clean HTTP boundary with Observatory
- No shared database

**VII. Groundskeeper Stewardship** ✓
- Quality over quantity (curator-controlled examples)
- Organic growth (Observatory only for MVP)
- Patient care (3-5 day thoughtful implementation)

**VIII. Technical Pragmatism** ✓
- FastAPI/Jinja2 chosen for simplicity (no framework overhead)
- Static caching justified (fast demos, no Observatory load)
- No database justified (stateless, simple deployment)
- Minimal code approach (~500 LOC)

**Violations**: None

**Result**: ✅ PASS - All constitution principles satisfied

## Project Structure

### Documentation (this feature)
```
specs/006-unified-microservice-interface/
├── plan.md              # This file (/plan output)
├── spec.md              # Feature specification
├── TECH-DECISIONS.md    # Technical stack decisions
├── collaboration/
│   └── CLARIFICATIONS-RESPONSE.md
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.openapi.yaml
└── tasks.md             # Phase 2 output (/tasks command)
```

### Source Code (repository root)
```
services/web-interface/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings (Observatory URL, etc.)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── pages.py            # HTML page routes
│   │   └── proxy.py            # Observatory API proxy
│   ├── templates/
│   │   ├── base.html           # Base layout
│   │   ├── index.html          # Landing page
│   │   ├── demo.html           # Demo interface
│   │   ├── docs.html           # API documentation
│   │   └── components/         # Reusable template parts
│   │       ├── nav.html
│   │       └── example-card.html
│   └── static/
│       ├── examples/           # Cached demo results (JSON)
│       │   ├── dialectic-simple.json
│       │   ├── dialectic-complex.json
│       │   └── exploration.json
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js          # Minimal JS (HTMX if needed)
├── tests/
│   ├── test_pages.py           # Page rendering tests
│   ├── test_proxy.py           # Observatory proxy tests
│   └── test_integration.py     # Full user flow tests
├── Dockerfile
├── pyproject.toml
├── .env.example
└── README.md
```

**Structure Decision**: Single service architecture. The web interface is an independent microservice that proxies requests to Observatory API. No frontend/backend split needed—server-side rendering handles both presentation and API calls. Tests follow pytest patterns established in Observatory service.

## Phase 0: Outline & Research

**Status**: ✓ Complete (all decisions in TECH-DECISIONS.md)

### Research Tasks Completed

1. **FastAPI + Jinja2 SSR Pattern**
   - **Decision**: Use Jinja2 templates with FastAPI
   - **Rationale**: Minimal complexity, no build pipeline, Python consistency
   - **Alternatives**: React (rejected—build overhead), Vue (rejected—framework complexity)

2. **Caching Strategy**
   - **Decision**: Static JSON files for curated examples
   - **Rationale**: Simple, fast (<100ms), curator-controlled, no Observatory load
   - **Alternatives**: Redis (rejected—over-engineering), Database (rejected—stateless principle)

3. **Authentication Passthrough**
   - **Decision**: No auth logic in web interface, use Observatory API keys
   - **Rationale**: Zero duplication, security stays in Observatory
   - **Alternatives**: OAuth in web interface (rejected—complexity), Duplicate auth (rejected—violates DRY)

4. **Health Monitoring**
   - **Decision**: Direct call to Observatory `/health` on page load
   - **Rationale**: Simple, no background processes, user sees live status
   - **Alternatives**: Separate monitoring service (rejected—over-engineering)

5. **Observatory Client Library**
   - **Decision**: Use httpx for HTTP calls to Observatory
   - **Rationale**: Async support, same library Observatory uses for testing
   - **Alternatives**: requests (rejected—no async), custom client (rejected—unnecessary)

**Output**: All technical uncertainties resolved. Stack confirmed as FastAPI + Jinja2 + httpx + static files.

## Phase 1: Design & Contracts

**Status**: Will execute (creating artifacts now)

### 1. Data Model

See `data-model.md` for full entity definitions. Key entities:

- **CachedExample**: Conversation sample with pre-generated analysis
- **DemoRequest**: User-initiated demo (Observatory API call)
- **AnalysisResult**: Observatory response (patterns, sentiment, topics)

### 2. API Contracts

See `contracts/api.openapi.yaml` for complete OpenAPI specification.

**Public Routes** (no auth):
- `GET /` - Landing page
- `GET /demo` - Demo interface
- `GET /docs` - API documentation
- `GET /examples/{id}` - Load cached example

**Proxy Routes** (auth via Observatory API key):
- `POST /api/analyze` - Proxy to Observatory (custom input)
- `GET /api/health` - Observatory health status

### 3. Contract Tests

Generated contract tests (will fail until implementation):
- `tests/test_pages.py` - Page routes return 200, correct templates
- `tests/test_proxy.py` - Proxy routes call Observatory correctly
- `tests/test_examples.py` - Cached examples load and render

### 4. Quickstart

See `quickstart.md` for complete setup and validation steps.

**Quick validation**:
```bash
cd services/web-interface
uv run uvicorn app.main:app --reload
curl http://localhost:8080/
curl http://localhost:8080/examples/dialectic-simple
```

### 5. Agent Context

Agent-specific context file will be created as `CLAUDE.md` with implementation guidance for Claude Code.

**Output**: Complete design artifacts ready for task generation.

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:

1. **Load task template** from `.specify/templates/tasks-template.md`

2. **Generate from contracts** (priority order):
   - Contract test tasks (one per endpoint) [P - can run parallel]
   - Model creation tasks (CachedExample, DemoRequest, AnalysisResult) [P]
   - Template creation tasks (one per HTML page) [P after models]
   - Route implementation tasks (one per router file)

3. **Generate from user stories**:
   - Integration test: "Visitor sees landing page and understands value in 30s"
   - Integration test: "Visitor clicks demo and sees results in 3s"
   - Integration test: "Developer provides API key and analyzes custom conversation"

4. **Implementation tasks** (make tests pass):
   - Task: Implement page routes (landing, demo, docs)
   - Task: Implement Observatory proxy with error handling
   - Task: Create cached example loader
   - Task: Implement rate limit display
   - Task: Add health check integration

5. **Infrastructure tasks**:
   - Task: Create Dockerfile
   - Task: Setup uv project (pyproject.toml)
   - Task: Generate 10-15 cached examples from Observatory
   - Task: Write deployment docs

**Ordering Strategy**:
- Tests before implementation (TDD)
- Models → Templates → Routes → Integration
- Mark [P] for parallelizable tasks (independent files)

**Estimated Output**: ~20-25 numbered tasks with dependencies marked

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, load test with 10 concurrent users)

## Complexity Tracking

No constitution violations or complexity deviations. Design is minimal and aligned with all principles.

## Progress Tracking

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning approach described (/plan command)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved (8/8 via TECH-DECISIONS.md)
- [x] Complexity deviations documented (none)

---
*Based on Constitution v1.3.1 - See `.specify/memory/constitution.md`*
