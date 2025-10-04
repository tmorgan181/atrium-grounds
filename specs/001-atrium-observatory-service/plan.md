# Implementation Plan: Atrium Observatory Service

**Feature**: 001-atrium-observatory-service
**Status**: Ready for Implementation
**Created**: 2025-10-04
**Planning Complete**: 2025-10-04

## Overview

Migrate the existing Observatory Flask application to a standalone microservice within Atrium Grounds, transforming it from a local Ollama-dependent tool into a public API service while preserving all analysis capabilities.

## Architecture Decisions

### Service Design
- **Framework**: FastAPI (async, auto-documented, aligns with constitution)
- **Model Backend**: Ollama Observer model (Phases 1-4)
  - Direct integration preserving existing PatternAnalyzer behavior
  - Backend abstraction deferred to Phase 5 if production needs require it
  - Follows constitution's "add complexity only when needed" principle
- **Database**: SQLite for development, PostgreSQL for production
- **Queue**: Redis for batch job management
- **Deployment**: Docker container with docker-compose for local dev

### Groundskeeper Data Curation Workflow
**Ethical Boundary Protection**: Conversation data flows from private archives to public service only through manual curation by the groundskeeper (maintainer).

**Curation Process**:
1. Maintainer reviews conversations in private Atrium archives
2. Identifies conversations suitable for public examples (non-sensitive, educational value)
3. Manually copies/sanitizes conversation text into `services/observatory/examples/`
4. Adds metadata (category, description) to example manifest
5. Examples become accessible via `/examples` API endpoint

**No Automated Sync**: The service NEVER has direct filesystem access to private archives. This manual curation step is the boundary enforcement mechanism.

### API Structure
```
/api/v1/
├── /analyze              # POST - Single conversation analysis
├── /analyze/batch        # POST - Batch analysis request
├── /analyze/{id}         # GET - Retrieve analysis results
├── /analyze/{id}/cancel  # POST - Cancel ongoing analysis
├── /examples             # GET - List curated examples
├── /examples/{name}      # GET - Load specific example
├── /health               # GET - Service health check
└── /metrics              # GET - Usage metrics (authenticated)
```

### Data Model

**Analysis Request**:
```
{
  "conversation_text": str,
  "options": {
    "pattern_types": ["dialectic", "sentiment", "topics", "dynamics"],
    "include_insights": bool,
    "callback_url": str (optional, for async)
  }
}
```

**Analysis Response**:
```
{
  "id": uuid,
  "status": "completed" | "processing" | "failed" | "cancelled",
  "observer_output": str,
  "patterns": {
    "dialectic": [...],
    "sentiment": {...},
    "topics": [...],
    "dynamics": {...}
  },
  "summary_points": [str],
  "confidence_score": float,
  "processing_time": float,
  "created_at": timestamp,
  "expires_at": timestamp
}
```

## Migration Strategy

### Sacred Boundaries Enforcement (Constitution Compliance)
**ABSOLUTE RULE:** The Observatory service MUST NEVER access private Atrium archives directly. All migration, data flows, and example curation must occur via manual groundskeeper review and explicit copying/sanitization. This is non-negotiable and required by the Atrium Grounds constitution's ethical boundaries principle.

### Phase 1: Core Service (Week 1)
**Goal**: Functional API with existing analysis capabilities

1. **Project Setup**
   - Create `services/observatory/` structure
   - Set up FastAPI app with uv/pyproject.toml
   - Configure logging and environment management
   - Docker containerization

2. **Port Existing Components**
   - Migrate `PatternAnalyzer` → `AnalyzerEngine`
   - Migrate `SecurityMediator` → `InputValidator`
   - Migrate `ProcessManager` → `JobManager`
   - Adapt Ollama integration for async operation

3. **Implement Core Endpoints**
   - POST `/analyze` - Single analysis
   - GET `/analyze/{id}` - Retrieve results
   - POST `/analyze/{id}/cancel` - Cancel operation
   - GET `/health` - Service status

4. **Data Persistence**
   - SQLite schema for analysis storage
   - Result expiration logic (30-day TTL)
   - Request logging for transparency

### Phase 2: Authentication & Rate Limiting (Week 2)
**Goal**: Multi-tier access control

1. **Auth Implementation**
   - Public tier: Simple token or no auth
   - API key tier: Key generation and validation
   - JWT tier: OAuth2 integration prep

2. **Rate Limiting**
   - Redis-based rate limiter
   - Tier-based limits (10/60/600 req/min)
   - Daily quotas (500/5K/50K per day)
   - Rate limit headers in responses

3. **Middleware Stack**
   - Request authentication
   - Rate limit enforcement
   - Usage tracking/metrics
   - Error handling

### Phase 3: Batch Processing (Week 3)
**Goal**: Async multi-conversation analysis

1. **Job Queue System**
   - Redis queue for batch jobs
   - Worker process for async analysis
   - Job status tracking
   - Priority queue support

2. **Batch Endpoints**
   - POST `/analyze/batch` - Submit batch
   - GET `/analyze/batch/{id}` - Batch status
   - Webhook notifications
   - Result aggregation

3. **Scaling Considerations**
   - Worker pool management
   - Job cancellation/reprioritization
   - Progress reporting
   - Error recovery

### Phase 4: Web Interface & Examples (Week 4)
**Goal**: User-friendly web UI and curated examples

1. **Frontend Migration**
   - Port existing `observatory.html` to modern framework (or keep simple)
   - Real-time analysis feedback
   - Example browser interface
   - Cancellation controls

2. **Example Management**
   - Curated conversation examples
   - Example categorization
   - GET `/examples` and `/examples/{name}`
   - Example contribution workflow

3. **Documentation**
   - OpenAPI spec auto-generation
   - Usage guides and tutorials
   - API client examples (Python, JS)
   - Integration patterns

### Phase 5: Production Readiness (Week 5)
**Goal**: Deployable, monitorable service

1. **Observability**
   - Structured logging
   - Metrics collection (Prometheus)
   - Distributed tracing
   - Error reporting

2. **Testing**
   - Unit tests for analyzers
   - Integration tests for API
   - Load testing for rate limits
   - Security testing for injection

3. **Deployment**
   - Production Docker image
   - docker-compose for full stack
   - Environment configuration
   - CI/CD integration

4. **Documentation**
   - README with setup instructions
   - API documentation site
   - Contributing guidelines
   - Migration guide from old Observatory

## Technical Specifications

### Dependencies (pyproject.toml)
```toml
[project]
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "sqlalchemy>=2.0.0",
    "redis>=5.0.0",
    "pydantic>=2.0.0",
    "httpx>=0.24.0",
    "python-multipart>=0.0.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]
```

### Directory Structure
```
services/observatory/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── api/
│   │   ├── v1/
│   │   │   ├── analyze.py   # Analysis endpoints
│   │   │   ├── examples.py  # Example endpoints
│   │   │   └── health.py    # Health/metrics
│   ├── core/
│   │   ├── analyzer.py      # Analysis engine (from PatternAnalyzer)
│   │   ├── validator.py     # Input validation (from SecurityMediator)
│   │   ├── jobs.py          # Job management (from ProcessManager)
│   │   └── config.py        # Configuration
│   ├── models/
│   │   ├── schemas.py       # Pydantic models
│   │   └── database.py      # SQLAlchemy models
│   └── middleware/
│       ├── auth.py          # Authentication
│       └── ratelimit.py     # Rate limiting
├── tests/
├── examples/                # Curated conversations
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

### Security Considerations

1. **Input Validation**
   - Preserve existing injection detection patterns
   - Character limits (10K per conversation)
   - Content sanitization
   - Rate limit bypass prevention

2. **Data Privacy**
   - No conversation persistence beyond analysis
   - Encrypted data at rest (for cached results)
   - Audit logging for all requests
   - Compliance with ethical boundaries principle

3. **API Security**
   - HTTPS only in production
   - CORS configuration
   - API key rotation support
   - Request signing for webhooks

## Success Criteria

### Functional Requirements Met
- [ ] All FR-001 through FR-013 implemented
- [ ] Existing Observatory features preserved
- [ ] Multi-tier authentication working
- [ ] Rate limiting enforced correctly
- [ ] Batch processing operational
- [ ] Examples accessible via API

### Performance Targets
- [ ] Single analysis: < 30s (matching existing timeout)
- [ ] API response time: < 200ms (excluding analysis)
- [ ] Batch job start: < 5s
- [ ] 99.9% uptime
- [ ] Support 10 concurrent analyses

### Quality Gates
- [ ] 80%+ test coverage
- [ ] All security patterns validated
- [ ] OpenAPI spec generated
- [ ] Documentation complete
- [ ] Docker image < 500MB
- [ ] CI/CD pipeline passing

## Risks & Mitigations

**Risk**: Ollama model unavailability in production
**Mitigation**: Abstract model backend, support multiple providers

**Risk**: Analysis timeouts causing poor UX
**Mitigation**: Implement streaming responses, progress updates

**Risk**: Rate limit circumvention
**Mitigation**: Multiple limit layers (IP, key, user), fingerprinting

**Risk**: Conversation data leakage
**Mitigation**: TTL enforcement, encryption, audit logs, no direct persistence

## Multi-Agent Development Notes

**Current Approach**: Solo development by Claude Code as primary agent for this first feature. This establishes reference patterns for constitutional compliance.

**Delegation Opportunities** (for future features or if parallel work needed):

**Good Candidates for Copilot Delegation**:
- **Phase 2 (Auth & Rate Limiting)**: Isolated middleware with clear contracts, minimal architecture decisions
- **Phase 4 (Web Interface)**: Frontend work after backend API is stable
- **Testing**: Test suite development can run parallel to implementation

**Should Stay with Claude Code**:
- **Phase 1 (Core Service)**: Architecture decisions and pattern establishment
- **Phase 3 (Batch Processing)**: Complex async logic and job management
- **Phase 5 (Production Readiness)**: System-wide integration and deployment

**Git Operations**: Per worktrees protocol, prefer Copilot for branch/worktree creation when multi-agent work begins. Both agents commit their own work.

**Coordination**: Use `specs/001-atrium-observatory-service/collaboration/` directory for task delegation docs if multi-agent becomes beneficial.

## Ongoing Maintenance Tasks

**Weekly**:
- Monitor analysis error rates and timeouts
- Review rate limit effectiveness
- Check storage usage and TTL cleanup

**Monthly**:
- Curate new example conversations from private archives
- Review and update dependency versions (uv lock)
- Analyze usage patterns and adjust rate limits

**Quarterly**:
- Evaluate Ollama Observer model updates
- Review security patterns for new injection techniques
- Assess need for additional pattern detectors
- Consider backend abstraction if scaling issues emerge

**Annual**:
- Constitution compliance audit
- Performance benchmarking
- API versioning strategy review
- User feedback integration

**Continuous**:
- Respond to security advisories
- Monitor CI/CD pipeline health
- Keep documentation synchronized with code changes

## Next Steps

1. Create `services/observatory/` directory structure
2. Set up FastAPI project with uv
3. Port PatternAnalyzer to async AnalyzerEngine
4. Implement `/analyze` endpoint with export functionality (FR-014)
5. Add SQLite storage for results
6. Write initial test suite

Ready to begin implementation with Phase 1, Step 1: Project Setup.
