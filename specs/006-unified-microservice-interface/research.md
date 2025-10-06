# Research: Unified Microservice Interface

**Feature**: 006-unified-microservice-interface
**Date**: 2025-01-05
**Status**: Complete

## Research Summary

All technical decisions documented in [TECH-DECISIONS.md](TECH-DECISIONS.md). This document consolidates key research findings.

## 1. FastAPI + Jinja2 SSR

**Decision**: Server-side rendering with FastAPI and Jinja2 templates

**Research Findings**:
- FastAPI supports Jinja2 templates natively
- No build pipeline required (compared to React/Vue)
- Python consistency across all Atrium Grounds services
- HTMX can add interactivity without full SPA complexity
- Successful pattern in Django, Flask applications

**Alternatives Evaluated**:
1. **React SPA**: Rejected due to build complexity, state management overhead, API serialization layer
2. **Vue.js**: Rejected for same reasons as React, plus framework lock-in
3. **Static site (Jekyll/Hugo)**: Rejected because requires dynamic API proxy functionality

**Rationale**: Minimal code, fast development, scalable when needed (can add React layer later)

## 2. Caching Strategy

**Decision**: Static JSON files for curated demo results

**Research Findings**:
- 10-15 examples = ~100KB total (trivial storage)
- File read <1ms (faster than any database)
- No cache invalidation complexity
- Curator control via manual generation script
- Works with any deployment (no Redis/Memcached dependency)

**Alternatives Evaluated**:
1. **Redis**: Rejected—over-engineering for static data
2. **SQLite**: Rejected—adds query complexity for simple reads
3. **Live API every time**: Rejected—puts load on Observatory, slower UX

**Rationale**: Simplest solution that meets performance goals (<100ms for demos)

## 3. Authentication Strategy

**Decision**: Passthrough to Observatory API (no auth logic in web interface)

**Research Findings**:
- Observatory already has API key system (public/api-key/partner tiers)
- Browser localStorage can store API keys safely (user responsibility)
- No session management needed (stateless)
- Security logic stays in one place (Observatory)

**Alternatives Evaluated**:
1. **OAuth in web interface**: Rejected—unnecessary complexity, duplicates auth
2. **JWT tokens**: Rejected—adds token management, refresh logic
3. **Cookie sessions**: Rejected—violates stateless principle

**Rationale**: Zero duplication, security boundary clear, web interface stays simple

## 4. Health Monitoring

**Decision**: Direct /health call to Observatory on page load

**Research Findings**:
- Observatory has /health endpoint (returns 200 + status JSON)
- Page load is infrequent enough (not constant polling)
- User sees live status, not stale cache
- No background processes needed

**Alternatives Evaluated**:
1. **Separate monitoring service**: Rejected—over-engineering for MVP
2. **Cached status (1-min TTL)**: Rejected—adds state, complexity
3. **Real-time WebSocket**: Rejected—unnecessary for occasional checks

**Rationale**: Simplest approach, no added complexity

## 5. Observatory Client

**Decision**: httpx library for async HTTP calls

**Research Findings**:
- httpx used in Observatory tests (proven, familiar)
- Async support (FastAPI is async-first)
- Same API as requests (easy to learn)
- Built-in connection pooling

**Alternatives Evaluated**:
1. **requests**: Rejected—no async support
2. **aiohttp**: Rejected—different API, less familiar
3. **Custom client class**: Rejected—unnecessary abstraction

**Rationale**: Consistency with Observatory testing patterns, async-compatible

## Key Performance Benchmarks

**From Observatory service**:
- /analyze endpoint: ~2s average
- /health endpoint: <50ms
- Rate limits: 100/1000/5000 req/min per tier

**Web interface targets**:
- Cached demos: <100ms (file read + template render)
- Live demos: <3s (Observatory /analyze + rendering)
- Page loads: <500ms (template render + static assets)

## Technology Stack Summary

**Backend**:
- FastAPI 0.115+ (web framework)
- Jinja2 3.1+ (templating)
- httpx 0.28+ (Observatory client)
- uvicorn 0.34+ (ASGI server)

**Frontend**:
- Server-rendered HTML
- Minimal CSS (no framework)
- Optional: HTMX for interactivity (via CDN)

**Storage**:
- Static JSON files (curated examples)
- No database

**Deployment**:
- Docker container
- Port 8080
- Independent from Observatory (port 8000)

## Risks & Mitigations

**Risk**: SSR limits interactivity
**Mitigation**: HTMX provides dynamic updates without full page reload. Can add React layer later if needed.

**Risk**: Static JSON requires manual updates
**Mitigation**: Admin script to regenerate from Observatory. Curator control ensures quality.

**Risk**: No auth means API keys in browser
**Mitigation**: User responsibility model (like API key headers in Postman). Document security best practices.

**Risk**: Direct Observatory calls could overload service
**Mitigation**: Rate limiting at Observatory level. Cached demos reduce load. Scale Observatory if needed.

## Constitution Compliance

All research decisions align with constitution v1.3.1:

- **I. Language & Tone**: Technical docs are clear, user-facing content is accessible ✓
- **II. Ethical Boundaries**: No private data access, Observatory boundary maintained ✓
- **III. Progressive Disclosure**: Three-tier architecture (cached → live → custom) ✓
- **IV. Multi-Interface**: Web for humans, API passthrough for developers ✓
- **V. Invitation**: "Try it now" demos, no barriers ✓
- **VI. Service Independence**: Separate service, clean boundaries ✓
- **VII. Stewardship**: Quality over quantity, curator-controlled ✓
- **VIII. Pragmatism**: Minimal code, justified choices ✓

## Next Steps

Phase 1: Create data models, API contracts, quickstart guide

---

**Research conducted by**: Claude Code (Sonnet 4.5)
**Sources**: TECH-DECISIONS.md, Observatory service, constitution v1.3.1
