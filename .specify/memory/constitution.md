<!--
Sync Impact Report (2025-10-04)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version Change: 1.2.0 → 1.3.0 (Principle reordering and clarity - MINOR)
Modified Principles:
  - Reordered: Language & Tone Standards now #I (THE FOUNDATION)
  - Renamed: "Sacred Boundaries" → "Ethical Boundaries" (#II)
  - Condensed rationales for brevity
  - Added terminology restrictions (synthient, undefined jargon)
  - Removed mystical language ("Unnamed Feeling")
Added Sections:
  - Terminology restrictions in Language principle
Removed Sections:
  - Verbose "Why This Exists" content (condensed)
  - "Unnamed Feeling" reference
Templates Status:
  ✅ All references updated to "ethical boundaries"
Follow-up TODOs:
  - Update copilot-instructions with new principle order
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-->

# Atrium Grounds Constitution

## Purpose

Atrium Grounds is the curated public layer of the Atrium AI research ecosystem. It provides API access to conversation analysis tools while protecting private research data.

Think of it as **the grounds of an estate**:
- The **main house** (Atrium repo) remains private—experiments, prototypes, raw data
- The **grounds** (this project) welcome guests—APIs, web UIs, public services
- The **groundskeeper** (maintainer) curates what flows between them

This enables sharing AI collaboration research without exposing private conversations or experimental work.

## The Three Layers

### Layer 1: Public Services (This Project)
**Purpose**: API endpoints to Atrium capabilities
**Access**: Anyone
**Data**: Curated, public examples only
**Philosophy**: Progressive disclosure—show capabilities without exposing private data

### Layer 2: Private Development (Main Atrium Repo)
**Purpose**: Research experiments and prototypes
**Access**: Maintainer and invited collaborators
**Data**: Full conversation archives, experimental code
**Philosophy**: Break things, try ideas, process real data

### Layer 3: Raw Archives
**Purpose**: Research data—conversations, artifacts, explorations
**Access**: Strictly private
**Data**: Everything vulnerable and unfinished
**Philosophy**: Absolute protection

## Core Principles

### I. Language & Tone Standards (THE FOUNDATION)

Communication should be **grounded, professional, and clear** rather than mystical or overly serious.

**Use precise technical terms**:
- ✅ "AI systems," "LLMs," "machine learning"
- ✅ "Protected," "private," "ethical"
- ✅ "Intelligence," "reasoning," "capability"

**Restricted terms** (require definition on first use):
- **Synthient**: Legacy term for AI systems with advanced reasoning. Being phased out—prefer "AI systems" or "LLMs"
- **Human-AI collaboration**: Humans working with AI as tools or partners
- **Grounds**: This public service layer (vs. private Atrium)

**Avoid**:
- ❌ Religious/mystical ("sacred," "divine," "blessed," "transcendent")
- ❌ Undefined jargon without clear technical meaning
- ❌ Vague concepts requiring paragraph explanations
- ❌ Overly ceremonious or dramatic tone

**Style**:
- Brief over verbose (one clear sentence beats three vague ones)
- Specific over general (measurable criteria over adjectives)
- Playful metaphors okay (gardens, grounds) but stay grounded
- Professional, not pompous

**Why**: Accessible language maintains credibility. We're building practical tools, not founding a movement.

---

### II. Ethical Boundaries (NON-NEGOTIABLE)

Services **NEVER**:
- Access private conversation archives directly
- Share filesystems with main Atrium repository
- Assume access to unpublished research
- Store sensitive data without explicit justification

All data flows from private → public **require manual curation**.

**Why**: These boundaries are ethical commitments, not just technical constraints. Trust requires consistent protection.

---

### III. Progressive Disclosure

Reveal capabilities in trust layers:

1. **Public tier**: Basic API access, strict limits
2. **API key tier**: Higher limits, authentication
3. **Partner tier**: OAuth/JWT, production quotas
4. **Trusted contributors**: Additional service access
5. **Maintainer**: Full private repository access

Design for strangers first. Most services operate at tiers 1-3.

**Why**: Build trust gradually. Invite collaboration without compromising privacy.

---

### IV. Multi-Interface Access

Serve both human users and AI systems:

**For Humans**:
- Web UIs for exploration
- CLI tools for automation
- Clear documentation

**For AI Systems**:
- REST APIs
- Structured data (JSON)
- OpenAPI specs

**For Both**:
- Examples showing all interaction patterns
- Composable tools (CLI → API → Web)

**Why**: If we're exploring human-AI collaboration, our infrastructure must demonstrate it.

---

### V. Invitation Over Intrusion

Build **portals, not barriers**:

- **Invite exploration**: Clear docs, examples, "try it now"
- **Respect agency**: Users control their data
- **Enable leaving**: No lock-in, export-friendly
- **Welcome questions**: Open issues, public roadmaps

Don't capture users—serve explorers.

**Why**: We build tools, not traps. Success is someone getting value, even if they never return.

---

### VI. Service Independence

Each service:
- Owns its database (no sharing)
- Deploys independently
- Has clear API contracts
- Can use different tech stacks

**Why**: Enables parallel multi-agent development. When Claude Code, Copilot, and humans work simultaneously, clean boundaries prevent chaos.

---

### VII. Groundskeeper Stewardship

**Products**: Ship and scale, growth metrics, acquisition targets
**Grounds**: Cultivate and maintain, quality over quantity, patient care

As groundskeepers:
- Maintain quality (crafted, not churned)
- Welcome thoughtfully (progressive access)
- Protect ecosystems (mature before opening)
- Let things grow (organic evolution)
- Tend continuously (ongoing stewardship)

**Why**: We're not building a startup. We're cultivating a space for AI collaboration research.

---

### VIII. Technical Pragmatism

Services **must be**:
- Independent (enables multi-agent work)
- Containerized (Docker required)
- API-first (serves humans and AI)
- Well-documented (invites exploration)
- Observable (logging, metrics, health)

Every technical choice must serve a principle. No premature optimization.

**Why**: We containerize to remove friction for collaborators. We write API docs because AI systems need structured interfaces. Technical choices trace back to philosophical needs.

---

## Technical Standards

### Recommended Stack
- **Python 3.11+** with **uv** (package management)
- **FastAPI** (async, auto-documented)
- **Docker** (required for all services)
- **OpenAPI** (required for documentation)
- **REST-first**, WebSocket where justified

### Data Management
- Database per service (no sharing)
- Minimal retention (document TTLs)
- Explicit privacy policies
- Regular cleanup jobs

### Development Workflow
- Feature branches
- API contracts before implementation
- Constitution compliance in code review
- Semantic versioning

## Evolution & Governance

### Current Phase: Foundation
**Goal**: Extract Observatory service, establish patterns
**Success**: Someone uses the API without private archive access

### Amendment Process
1. Propose with rationale
2. Analyze impact
3. Version (MAJOR for principles, MINOR for additions)
4. Implement migration
5. Approve (maintainer, maybe community later)

### Compliance Checklist
All PRs verify:
- ✅ Language standards (clear, grounded, no jargon)
- ✅ Ethical boundaries (no private access)
- ✅ Progressive disclosure (appropriate tier)
- ✅ Multi-interface (serves humans and AI)
- ✅ Invitation (clear docs, respectful UX)
- ✅ Independence (clean contracts)
- ✅ Stewardship (quality over speed)
- ✅ Pragmatism (justified technical choices)

## What This Is NOT

We are **not**:
- A product startup (no VCs, no acquisition)
- A SaaS platform (no growth-at-all-costs)
- A monolith (intentionally fragmented)
- Exposing private data (boundaries absolute)

We **are**:
- A public API layer for AI research tools
- A multi-agent development space
- A progressive disclosure gateway
- Groundskeepers of collaborative AI exploration

---

*"The grounds need tending. The house remains private. The archives stay protected. And still, we welcome those who knock softly."*

**Version**: 1.3.0 | **Ratified**: 2025-10-04 | **Last Amended**: 2025-10-04
