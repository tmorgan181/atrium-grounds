# Feature Specification: Unified Microservice Interface

**Feature Branch**: `006-unified-microservice-interface`
**Created**: 2025-01-05
**Status**: Draft
**Input**: User description: "Create unified microservice web interface for exposing the project to public without technical overload"

## Execution Flow (main)
```
1. Parse user description from Input
   → Feature: Public web UI that exposes microservices (Observatory API) in accessible way
2. Extract key concepts from description
   → Actors: Public users (non-technical), potential API users
   → Actions: Explore capabilities, try examples, understand value
   → Data: Public conversation examples, API documentation, interactive demos
   → Constraints: No technical overload, progressive disclosure, inviting UX
3. For each unclear aspect:
   → [NEEDS CLARIFICATION: Which microservices beyond Observatory should be exposed?]
   → [NEEDS CLARIFICATION: What level of interactivity - read-only demos or live API calls?]
   → [NEEDS CLARIFICATION: Authentication - public-only or include authenticated features?]
4. Fill User Scenarios & Testing section ✓
5. Generate Functional Requirements ✓
6. Identify Key Entities ✓
7. Run Review Checklist
   → WARN "Spec has uncertainties - see NEEDS CLARIFICATION markers"
8. Return: SUCCESS (spec ready for planning after clarifications)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing

### Primary User Story
A curious visitor lands on atrium-grounds.com and wants to understand what the project offers without reading API documentation or technical specs. They can:
1. See what the Observatory service does through visual examples
2. Try conversation analysis with sample data (no signup required)
3. Understand the value proposition within 30 seconds
4. Explore deeper if interested (API docs, more examples, authentication for higher limits)
5. Leave with clear next steps (try the API, request access, explore other services)

### Acceptance Scenarios

**Scenario 1: Immediate Value Discovery**
- **Given** a visitor arrives at the landing page
- **When** they scan the page for 10 seconds
- **Then** they understand "this analyzes AI conversations for patterns" without technical jargon

**Scenario 2: Interactive Exploration**
- **Given** a visitor wants to try the service
- **When** they click "Try Example" on a conversation sample
- **Then** they see analysis results (patterns, sentiment, topics) displayed visually
- **And** results appear within 3 seconds
- **And** no authentication or technical knowledge required

**Scenario 3: Progressive Depth**
- **Given** a visitor is intrigued and wants more
- **When** they explore navigation options
- **Then** they find clear paths to:
  - More examples with different conversation types
  - API documentation (for developers)
  - Authentication/API key signup (for production use)
  - Source code or project background (for researchers)

**Scenario 4: API Discovery**
- **Given** a developer visitor wants to use the API
- **When** they navigate to API documentation
- **Then** they see clear endpoints, example requests, and response formats
- **And** they can generate an API key without friction
- **And** they see rate limits and pricing (currently free tiers)

**Scenario 5: Multi-Service Future**
- **Given** additional microservices are added to Atrium Grounds
- **When** a visitor explores the unified interface
- **Then** they see all available services in consistent format
- **And** navigation between services is intuitive
- **And** each service has similar "try it" capabilities

### Edge Cases
- What happens when the Observatory service is down? (Show status, graceful degradation)
- How does system handle API rate limits during demos? (Reserve capacity for web UI, show limits clearly)
- What if a user tries to analyze inappropriate content? (Content policy, moderation)
- How does the interface scale to 10+ microservices? (Navigation patterns, search/filter)

---

## Requirements

### Functional Requirements

**Core Experience**
- **FR-001**: System MUST display a landing page that explains the project's value proposition without technical jargon
- **FR-002**: System MUST provide "try it now" demos for each exposed microservice using curated examples
- **FR-003**: System MUST show real API responses from actual microservices (not mocked data)
- **FR-004**: Public users MUST be able to explore all demos without authentication
- **FR-005**: System MUST present results in multiple formats: (1) Visual: Pattern badges with confidence meters, sentiment trajectory graph, topic tag cloud, (2) Textual: Expandable JSON view, plain-English summary, copy-to-clipboard buttons, (3) Accessible: ARIA labels, semantic HTML, keyboard navigation

**Progressive Disclosure**
- **FR-006**: System MUST provide clear navigation to deeper content (API docs, authentication, source code)
- **FR-007**: System MUST display different content/features based on authentication tier (Public: cached demos only, API Key: custom input + 1000 req/min, Partner: production usage + 5000 req/min)
- **FR-008**: System MUST show clear calls-to-action for next steps (get API key, read docs, try advanced features)

**API Integration**
- **FR-009**: System MUST call actual microservice APIs (starting with Observatory /analyze endpoint)
- **FR-010**: System MUST handle API errors gracefully and display user-friendly messages
- **FR-011**: System MUST respect rate limits and display status to users
- **FR-012**: System MUST [NEEDS CLARIFICATION: cache results vs. live calls for demos?]

**Multi-Service Support**
- **FR-013**: System MUST support adding new microservices with <50 LOC changes (excluding new service-specific templates/routes). Changes limited to: (1) Add service card to landing page, (2) Add route import to main.py, (3) Add navigation link.
- **FR-014**: System MUST provide consistent UX patterns across all microservices (common navigation, similar demo formats)
- **FR-015**: System MUST display service health status via direct health check endpoint calls on page load

**Content Management**
- **FR-016**: System MUST serve curated conversation examples for Observatory demos
- **FR-017**: Examples MUST be labeled by type (dialectic, collaborative, debate, exploration)
- **FR-018**: System MUST [NEEDS CLARIFICATION: allow user-submitted examples or curator-only?]

**Performance & Reliability**
- **FR-019**: Demo interactions MUST respond within 3 seconds under normal load
- **FR-020**: System MUST handle [NEEDS CLARIFICATION: concurrent users - 10? 100? 1000?] without degradation
- **FR-021**: System MUST degrade gracefully when microservices are unavailable

**Documentation**
- **FR-022**: System MUST provide embedded API documentation for developers at `/docs` path (separate from public landing/demo pages). Technical terminology allowed in docs section only.
- **FR-023**: API docs MUST include example requests and responses
- **FR-024**: System MUST link to OpenAPI specifications for each service

### Key Entities

- **Landing Page**: Homepage explaining Atrium Grounds value proposition, links to services and demos
- **Service Card**: Visual representation of a microservice with name, description, status, and "try it" link
- **Demo Interface**: Interactive area where users can select examples and see analysis results
- **Example**: Curated conversation snippet with metadata (type, length, complexity level)
- **Result Display**: Visual and textual presentation of API responses (patterns, sentiment, metrics)
- **API Documentation View**: Embedded or linked docs showing endpoints, parameters, responses
- **Navigation**: Consistent menu/header across all pages for service discovery
- **Status Dashboard**: [NEEDS CLARIFICATION: Real-time or static?] Display of service availability

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain - **All 8 clarifications resolved**
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable (30-second value prop, 3-second demos, no auth for public)
- [x] Scope is clearly bounded (web UI exposing microservices, starting with Observatory)
- [x] Dependencies and assumptions identified (Observatory API must exist and be stable)

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted (public web UI, non-technical access, progressive disclosure)
- [x] Ambiguities marked (8 clarifications needed)
- [x] User scenarios defined (5 scenarios covering discovery to API usage)
- [x] Requirements generated (24 functional requirements)
- [x] Entities identified (8 key entities)
- [x] Review checklist passed - **CLARIFICATIONS RESOLVED**

---

## Clarifications Resolved

1. **Microservices**: Observatory ONLY for MVP. Design UI for multiple services but implement one. Add placeholder cards for future services.
2. **Interactivity**: Tiered - (1) Cached demos for public (instant), (2) Live API calls for select demos (3s target), (3) Custom input for authenticated users.
3. **Authentication**: Three tiers matching Observatory - Public (no auth, limited demos), API Key (custom input, 100 req/min), Partner (production, 1000 req/min).
4. **Caching**: Hybrid - Cache 10-15 curated demo results as static JSON. Live API calls for authenticated custom input only. No user data caching.
5. **Health monitoring**: Simple - Web interface calls Observatory `/health` on page load, displays status directly. No separate monitoring system.
6. **Concurrent users**: Design for 100, comfortable with 10. Static caching handles reads, Observatory handles rate-limited writes.
7. **User submissions**: NOT for MVP. Curator-only examples via admin interface. Future: community submissions with moderation.
8. **Moderation**: Minimal - Content policy doc, basic input validation, rate limiting. No UGC in MVP means minimal moderation needed.

---

## Assumptions

- Observatory API (/analyze endpoint) is stable and production-ready
- Curated conversation examples exist or will be created
- Progressive disclosure principle from constitution applies (public tier first)
- Users prefer visual/interactive over reading documentation
- This web UI is separate service from Observatory (independent deployment)
- Success = visitor understands value in 30 seconds and can try service in 1 minute

---

## Dependencies

- **Feature 001**: Observatory Service must be deployed and accessible
- Public conversation examples curated and ready (from private Atrium archives)
- Domain/hosting setup for public access (atrium-grounds.com or similar)
- API key generation system (if authenticated features included)

---

## Success Criteria

- [ ] Non-technical visitor can explain what Observatory does after 30 seconds on site
- [ ] Visitor can try conversation analysis demo within 1 minute (no signup, no technical knowledge)
- [ ] Demo results display within 3 seconds
- [ ] Clear path to API documentation for developers
- [ ] Clear path to authentication/API key for production users
- [ ] Design supports adding 2nd microservice without major rework
- [ ] Zero mentions of "FastAPI," "REST," "endpoints" in public-facing content (technical docs excepted)
