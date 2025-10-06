# Feature 006 Clarifications - Informed Recommendations

**Date**: 2025-10-05  
**Feature**: Unified Microservice Interface  
**Reviewer**: Claude Sonnet 4.5  
**Sources**: Past conversations, project constitution, existing work

---

## Context from Past Conversations

From your history, I found key insights:

1. **Three-layer architecture** already established (Sept 2024):
   - Layer 1: Public microservices (atrium-grounds, no private access)
   - Layer 2: Private Development (Main Atrium Repo, experimental)
   - Layer 3: Raw archives (strictly private)

2. **Polyglot web ecosystem** in development:
   - Observatory (conversation analysis)
   - Dialectic Engine (AI-AI dialogue)
   - Terminal interface
   - Flask apps with varied complexity
   - Desire for "API tissue or stdio" connections

3. **Design philosophy**: Simple but expandable, public-facing without private data access

---

## Clarification Responses

### 1. Microservices Beyond Observatory?

**Recommendation: Observatory ONLY for v1**

**Rationale**:
- Observatory is most mature (Feature 001-002 complete)
- Constitution principle VII: "Let things grow organically"
- Past conversation: "focus on one tool first (observatory is good)"
- Design the interface to support multiple services, but ship with one

**Implementation**:
- Build navigation/layout for N services
- Implement fully for Observatory
- Add placeholder cards for "Dialectic Engine" and "Coming Soon"
- Document how to add new services (pattern established)

**Benefits**:
- Faster time to launch
- Validates design patterns before scaling
- Reduces coordination complexity
- Follows constitution's "groundskeeper stewardship" (quality over growth)

---

### 2. Interactivity Level?

**Recommendation: TIERED INTERACTIVITY**

**Level 1: Read-Only Demos** (Public, no auth)
- Curated examples with pre-generated results
- "Try this example" buttons load cached analyses
- Fast (<1s), no API calls, no rate limits
- Shows value immediately

**Level 2: Limited Live Demos** (Public, rate-limited)
- User can select from curated examples
- Real API call to Observatory
- Public tier rate limits (100 req/min per Feature 002 settings)
- 3-second response target

**Level 3: Custom Input** (Requires API key)
- User can paste their own conversation
- Higher rate limits (1000/5000 req/min)
- Full API features available

**Rationale**:
- Progressive disclosure (constitution principle III)
- Past conversation emphasis on "simple unified entry point"
- Balances demo speed (cached) with authenticity (live API)
- Protects Observatory service from abuse

---

### 3. Authentication Tier Features?

**Recommendation: THREE TIERS (matching existing)**

Based on Feature 002 rate limit configuration:

**Public Tier** (no auth):
- View curated examples
- Read API documentation
- Try 3-5 pre-selected demos (cached results)
- Limit: 10 live demo requests per hour

**API Key Tier**:
- All public features
- Paste custom conversations (up to 10k chars)
- Higher rate limit (100 req/min)
- Access to API key management dashboard

**Partner Tier**:
- All API key features
- Production rate limits (1000 req/min)
- Webhook support
- Priority support

**Rationale**:
- Matches existing Observatory authentication architecture
- Constitution principle III: Progressive disclosure
- Past conversation: "progressive disclosure (public tier first)"

---

### 4. Caching vs Live API Strategy?

**Recommendation: HYBRID APPROACH**

**Cached Results** (for demos):
- Pre-generate analysis for 10-15 curated examples
- Store in static JSON files or simple database
- Update weekly or on-demand
- Instant response (<100ms)

**Live API Calls** (for authenticated users):
- Real-time analysis for custom input
- No caching (privacy concern)
- Rate-limited per tier
- 3-second target response time

**Implementation**:
```
/examples/
  dialectic-simple.json          # Cached result
  dialectic-complex.json         # Cached result
  exploration.json               # Cached result

/api/v1/analyze                  # Live endpoint (authenticated)
```

**Rationale**:
- Fast demos (cached) build trust
- Live API proves it's real, not mocked
- Privacy: don't cache user-submitted data
- Reduces load on Observatory service

---

### 5. Service Health Monitoring?

**Recommendation: SIMPLE STATIC STATUS**

**For MVP**:
- Single health check per service (1-minute interval)
- Cache status in memory (TTL: 60 seconds)
- Display: "Operational" / "Degraded" / "Offline"
- No historical data, no dashboards

**UI Display**:
```
Observatory Service    ● Operational
Response Time: ~2.5s
Last Updated: 2 min ago
```

**Future Enhancement** (post-MVP):
- Real-time monitoring dashboard
- Historical uptime graphs
- Incident notifications

**Rationale**:
- Keeps initial scope manageable
- Constitution principle VIII: Technical pragmatism
- Can enhance later if demand exists
- Simple health check already exists in Observatory

---

### 6. Concurrent User Target?

**Recommendation: DESIGN FOR 100, HANDLE 10**

**Initial Capacity**:
- Comfortable with 10 simultaneous users
- Graceful degradation up to 100 users
- Clear messaging if limits exceeded

**Architecture Decisions**:
- Static caching handles read-heavy traffic
- Live API calls go through Observatory rate limits
- No complex session management needed
- CDN-ready static assets

**Why not 1000?**:
- Constitution principle VII: "Quality over growth"
- Observatory not battle-tested at scale yet
- Can scale later if demand exists
- Better to launch small and stable

**Implementation**:
- Basic load testing (10 users, 5-second intervals)
- Monitor and adjust based on real usage
- Document scaling path for future

---

### 7. User-Submitted Examples?

**Recommendation: NOT FOR MVP**

**Phase 1 (MVP)**: Curator-only examples
- Admin interface to add examples
- Manual review before publishing
- 10-15 high-quality curated examples

**Phase 2 (Future)**: Community submissions
- Authenticated users can submit
- Moderation queue
- Voting/ranking system
- Content policy enforcement

**Rationale**:
- Constitution principle II: Ethical boundaries (quality control)
- Constitution principle VII: Groundskeeper stewardship (curated quality)
- Reduces initial complexity (no moderation system needed)
- Past conversation: "establish fundamentals" first

**MVP Workaround**:
- Add "Request Example" feature
- Users can email or GitHub issue
- Manual curation ensures quality

---

### 8. Content Moderation Requirements?

**Recommendation: MINIMAL FOR MVP**

**Since no user-submitted content in MVP**:
- Content policy document (terms of service)
- Basic input validation (length limits, character filtering)
- Abuse prevention via rate limiting
- Manual review of any API key applications

**When User Submissions Added** (Future):
1. Automated filters (profanity, PII, harmful content)
2. Moderation queue with manual review
3. User reporting system
4. Ban/suspension capabilities
5. Content policy enforcement

**Rationale**:
- No user submissions = minimal moderation needed
- Rate limiting prevents API abuse
- Can build moderation system when needed
- Focuses MVP on core value proposition

---

## Summary of Recommendations

| Question | Recommendation |
|----------|----------------|
| 1. Services? | **Observatory only** (design for multiple) |
| 2. Interactivity? | **Tiered** (cached demos → live demos → custom input) |
| 3. Auth tiers? | **Three tiers** (public/api-key/partner, matching Observatory) |
| 4. Caching? | **Hybrid** (cached demos, live API for auth) |
| 5. Health? | **Simple static** (cached status, 1-min refresh) |
| 6. Concurrent users? | **Design for 100, handle 10** comfortably |
| 7. User examples? | **Not for MVP** (curator-only, add later) |
| 8. Moderation? | **Minimal** (no UGC in MVP, policy + rate limits) |

---

## Alignment with Constitution

All recommendations align with constitution principles:

- **I. Language & Tone**: Clear, accessible UI without jargon ✓
- **II. Ethical Boundaries**: No private data access ✓
- **III. Progressive Disclosure**: Three authentication tiers ✓
- **IV. Multi-Interface**: Web first, API-ready architecture ✓
- **V. Invitation**: Demos, docs, easy exploration ✓
- **VI. Independence**: Observatory remains separate service ✓
- **VII. Stewardship**: Quality over quantity, organic growth ✓
- **VIII. Pragmatism**: Simple but expandable, ship fast ✓

---

## Next Steps

With these clarifications:

1. **Update spec.md** with decisions
2. **Run `/plan`** to create implementation plan
3. **Consider tech stack** (React/Vue/vanilla JS for frontend?)
4. **Delegate work** to appropriate agents

---

## Open Questions for You

1. **Frontend framework preference?** 
   - React (component reuse, popular)
   - Vue (simpler learning curve)
   - Vanilla JS + HTML (maximum simplicity)
   - Svelte (minimal bundle size)

2. **Hosting preference?**
   - GitHub Pages (static only, free)
   - Vercel/Netlify (SSR support, free tier)
   - Self-hosted (full control)

3. **Timeline expectations?**
   - MVP in 1 week (basic demos)?
   - Full v1 in 2-3 weeks (all tiers)?
   - Phased rollout?

4. **Design priority?**
   - Function first, aesthetics later?
   - Beautiful from day 1?
   - Iterative design improvement?

---

**Status**: Ready for your feedback and approval to proceed with `/plan`
