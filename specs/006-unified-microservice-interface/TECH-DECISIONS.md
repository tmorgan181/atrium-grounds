# Technical Decisions for Feature 006

**Feature**: Unified Microservice Interface
**Date**: 2025-01-05
**Decision Maker**: Claude Code (Sonnet 4.5)
**Principle**: Minimal code, maximum scalability

---

## Stack Decision: FastAPI + Jinja2 (SSR)

**Chosen**: Server-Side Rendered web app with FastAPI + Jinja2 templates

**Rejected Alternatives**:
- ❌ React/Vue/Svelte SPA (frontend framework)
- ❌ Next.js/Nuxt (SSR framework)
- ❌ Static site generator (Jekyll, Hugo)

**Rationale**:
1. **Minimal code**: No build pipeline, no bundlers, no state management
2. **Python consistency**: Same stack as Observatory (reuse patterns, knowledge)
3. **Fast development**: Templates are simple, HTMX for interactivity
4. **Constitution VIII**: Pragmatic - ship fast, enhance later if needed
5. **Scales when needed**: Can add React layer later without rewrite

**Trade-offs**:
- ✅ Simple deployment (single Docker container)
- ✅ No JavaScript framework learning curve
- ✅ Server owns rendering (SEO-friendly)
- ⚠️ Limited client-side interactivity (HTMX mitigates)
- ⚠️ Full page reloads for some interactions (acceptable for MVP)

---

## Architecture: Stateless Proxy Service

**Pattern**: Web interface as transparent proxy to Observatory API

**Key Decisions**:

### 1. No Authentication Logic
- Web interface does NOT manage auth
- Uses Observatory's existing API key system
- Public tier: No key required
- API key tier: User provides key (stored in localStorage)
- Partner tier: Same, just different key

**Benefit**: Zero auth code in web interface

### 2. No Database
- Curated examples: Static JSON files
- No user data storage
- No session persistence needed
- Health status: Live call to Observatory `/health`

**Benefit**: Stateless service, simple deployment

### 3. Service Independence
- Location: `services/web-interface/`
- Own Dockerfile
- Independent deployment from Observatory
- Calls Observatory via HTTP (clean boundary)

**Benefit**: Follows constitution principle VI (service independence)

---

## Caching Strategy

### Static File Caching (Curated Demos)
```
services/web-interface/
├── static/
│   └── examples/
│       ├── dialectic-simple.json      # Pre-generated analysis
│       ├── dialectic-complex.json
│       ├── exploration.json
│       └── collaborative.json
```

**Generation**: Manual script (curator control)
**Update**: On-demand via admin command
**Benefit**: Instant load (<100ms), no Observatory calls for demos

### No User Data Caching
- Custom user input → Live API call
- No caching of results (privacy)
- Rate-limited per tier
- 3-second target response

**Benefit**: Privacy protection, no sensitive data storage

---

## Health Monitoring: Direct Call

**Implementation**: Web interface calls Observatory `/health` on page load

**Display**:
```
Observatory Service    ● Operational
Response Time: ~2.5s
```

**No separate monitoring**:
- ❌ No background health check process
- ❌ No status caching
- ❌ No historical data

**Rationale**: Reduces moving parts, user sees live status

---

## Interactivity Tiers (Implementation)

### Tier 1: Cached Demos (Public)
- Load static JSON files
- Render analysis instantly
- No API calls
- No auth required

**Code complexity**: Minimal (file read + template render)

### Tier 2: Live Demos (Public, Rate-Limited)
- Call Observatory API with curated example
- Public rate limit (100 req/min)
- Show real-time response

**Code complexity**: Low (HTTP call + error handling)

### Tier 3: Custom Input (Authenticated)
- User provides API key
- User pastes conversation
- Call Observatory with user key
- Higher rate limits (1000/5000 req/min)

**Code complexity**: Medium (input validation + key management in browser)

---

## Scalability Design

### Current Target
- **Comfortable**: 10 simultaneous users
- **Graceful**: Up to 100 users
- **Degradation**: Clear messaging if exceeded

### How This Scales
1. **Static caching**: CDN-ready, handles unlimited reads
2. **Live API calls**: Rate-limited by Observatory (already handles 1000 req/min)
3. **Stateless service**: Horizontal scaling trivial (add containers)
4. **No database**: No bottleneck, no scaling complexity

### Future Scaling Path
1. Add CDN for static assets (Cloudflare/CloudFront)
2. Add Redis for shared rate limiting (if multi-instance)
3. Add SPA layer if client-side interactivity needed
4. Add load balancer if >100 concurrent users

**Current**: None needed, keep simple

---

## File Structure

```
services/web-interface/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── routers/
│   │   ├── pages.py            # HTML page routes
│   │   └── api.py              # Proxy to Observatory
│   ├── templates/
│   │   ├── base.html           # Layout
│   │   ├── index.html          # Landing page
│   │   ├── demo.html           # Demo interface
│   │   └── docs.html           # API docs
│   └── static/
│       ├── examples/           # Cached demo results
│       ├── css/
│       └── js/                 # Minimal JS (HTMX)
├── Dockerfile
├── pyproject.toml
└── README.md
```

**Estimated lines of code**: ~500 (very minimal)

---

## Dependencies

### Python Packages
```toml
[project]
dependencies = [
    "fastapi>=0.115.6",
    "uvicorn[standard]>=0.34.0",
    "jinja2>=3.1.5",
    "httpx>=0.28.1",          # For Observatory API calls
    "python-multipart>=0.0.20" # For form handling
]
```

### Optional Enhancements (Post-MVP)
- HTMX (via CDN, no install needed)
- Alpine.js (lightweight interactivity)
- Tailwind CSS (styling)

**MVP**: Plain HTML/CSS, minimal JS

---

## Deployment

### Development
```bash
cd services/web-interface
uv sync
uv run uvicorn app.main:app --reload
```

### Production
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install uv && uv sync --frozen
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Port**: 8080 (avoid conflict with Observatory on 8000)

---

## Security Considerations

### Input Validation
- Max conversation length: 10k characters
- Character whitelist (prevent injection)
- Rate limiting via Observatory
- CORS headers (restrict origins)

### No Sensitive Data
- No passwords stored
- API keys in browser localStorage (user responsibility)
- No user accounts (no PII)
- No conversation caching

### Observatory Trust
- Web interface trusts Observatory for:
  - Rate limiting
  - API key validation
  - Content analysis safety

**Benefit**: Security complexity stays in Observatory

---

## MVP Scope (Minimal Features)

### What's In
- ✅ Landing page explaining Observatory
- ✅ 3-5 demo buttons (cached results)
- ✅ 1-2 live demo buttons (real API)
- ✅ API documentation display
- ✅ API key input for custom analysis
- ✅ Health status display
- ✅ Basic error handling

### What's Out (Post-MVP)
- ❌ User accounts
- ❌ Example submissions
- ❌ Historical analysis tracking
- ❌ Advanced visualizations
- ❌ Real-time updates (WebSocket)
- ❌ Multiple service support (design for, implement later)

**Estimated MVP time**: 3-5 days with FastAPI + templates

---

## Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Stack** | FastAPI + Jinja2 | Minimal code, Python consistency |
| **Architecture** | Stateless proxy | No auth logic, no database |
| **Caching** | Static JSON files | Simple, fast, curator-controlled |
| **Health** | Direct API call | No separate monitoring system |
| **Auth** | Observatory passthrough | Zero auth code in web interface |
| **Database** | None | Stateless, simple deployment |
| **Frontend** | Server-rendered HTML | No build pipeline, fast dev |
| **Scaling** | Static + CDN-ready | Handles 100 users, scales horizontally |

**Core Principle**: Ship fast with minimal code, enhance later based on usage

---

## Open Questions

1. **Domain**: Where will this be hosted? (subdomain of existing? new domain?)
2. **Curated examples**: Who creates initial 10-15 examples? (need sample conversations)
3. **Design**: Plain/functional or invest in visual design for MVP?
4. **Timeline**: Target launch date for MVP?

---

**Decision Authority**: Claude Code (technical lead)
**Review Required**: User approval before `/plan` phase
**Next Step**: Create implementation plan once approved
