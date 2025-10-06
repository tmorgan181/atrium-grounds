# Remediation Plan: Feature 006 Analysis Findings

**Created**: 2025-01-05
**Analysis Source**: Cross-artifact analysis (spec.md, plan.md, tasks.md, constitution)
**Severity Threshold**: CRITICAL and HIGH issues addressed

## Executive Summary

Analysis identified 33 findings across 6 detection categories. This remediation plan addresses:
- **4 CRITICAL** issues (block implementation)
- **6 HIGH** priority issues (address before sprint)

**Estimated effort**: 1-2 hours

---

## CRITICAL Issues (Must Fix Before Implementation)

### C001: Missing Task for FR-015 (Health Status Display)

**Finding**: FR-015 requires health status display, but no task explicitly implements UI component

**Impact**: Feature incomplete, requirement untestable

**Remediation**:
Add new task **T029** to tasks.md:

```markdown
- [ ] **T029** [P] Create health status component in `app/templates/components/status.html`
  - Display Observatory operational/degraded/offline status
  - Show response time in ms
  - Auto-refresh every 30s (JavaScript)
  - Include in navigation component (T015)
```

**Dependencies**: After T015 (navigation component), before T026 (validation)

**Files to modify**:
- `tasks.md` - Add T029 in Phase 3.3
- Update T015 to include status badge placeholder

---

### C002: Data Model Conflict (DemoRequest Entity)

**Finding**: `DemoRequest` entity in data-model.md describes "User-initiated live demo request" but also references `example_id` (cached demos). Lifecycle unclear.

**Impact**: Confusion during implementation, potential wrong architecture

**Remediation**:
Update `data-model.md` section 2 to clarify:

```markdown
### 2. DemoRequest

**Purpose**: User-initiated LIVE demo request (not for cached examples)

**Fields**:
- `conversation` (list[dict]): Conversation from cached example OR user-provided
- `source` (string): "cached_example" | "user_input"
- `example_id` (string | null): ID if source is cached_example
- `api_key` (string | null): Optional Observatory API key
- `timestamp` (datetime): When request was made

**Lifecycle**:
- **Cached demo flow**: User clicks "Try Live" → Load example conversation → Create DemoRequest with source="cached_example" → Call Observatory → Render → Discard
- **Custom input flow**: User pastes conversation → Create DemoRequest with source="user_input" → Call Observatory → Render → Discard

**Validation**:
- If source="cached_example", example_id MUST be valid
- If source="user_input", conversation MUST be provided
- api_key optional for both flows
```

**Files to modify**:
- `data-model.md` - Update section 2 (DemoRequest)
- Add clarifying comments to demo page template task (T018)

---

### C003: TDD Enforcement Gate Missing

**Finding**: Tasks T004-T010 marked as "MUST FAIL before implementation" but no automated enforcement gate defined

**Impact**: Risk of implementation before tests written, violating TDD principle

**Remediation**:
Add validation gate to tasks.md and create enforcement script:

**tasks.md update**:
```markdown
## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**GATE**: Before proceeding to T011, run validation:
```bash
uv run pytest tests/ --collect-only
# Must show 7+ tests collected

uv run pytest tests/ -v
# Must show failures (tests exist but implementation missing)
```

**If all tests pass**: STOP - Tests may be mocking or implementation already exists
**If tests don't exist**: STOP - Write tests first (T004-T010)
**If tests fail with import/attribute errors**: ✅ PROCEED to T011
```

**Create script**: `scripts/validate-tdd-gate.sh`
```bash
#!/bin/bash
# TDD Gate Validator - Run before Phase 3.3 implementation

echo "🔍 TDD Gate Validation"
echo "====================="

# Check tests exist
echo "Step 1: Verify tests exist..."
TEST_COUNT=$(uv run pytest tests/ --collect-only -q 2>/dev/null | grep -c "test_")
if [ "$TEST_COUNT" -lt 7 ]; then
    echo "❌ FAIL: Found $TEST_COUNT tests, need at least 7"
    echo "Write tests T004-T010 first!"
    exit 1
fi
echo "✅ Found $TEST_COUNT tests"

# Check tests fail (implementation missing)
echo "Step 2: Verify tests fail (no implementation)..."
uv run pytest tests/ -v 2>&1 | grep -q "PASSED"
if [ $? -eq 0 ]; then
    echo "❌ FAIL: Some tests passing - implementation may already exist"
    echo "Review test files - should fail with ImportError or AttributeError"
    exit 1
fi
echo "✅ Tests fail as expected (no implementation yet)"

echo ""
echo "🎉 TDD Gate PASSED - Proceed to implementation (T011+)"
```

**Files to modify**:
- `tasks.md` - Add gate documentation after T010
- Create `scripts/validate-tdd-gate.sh`
- Update CLAUDE.md to reference TDD gate

---

### C004: Placeholder Text in FR-007

**Finding**: FR-007 still contains "[NEEDS CLARIFICATION: authentication tiers - public vs. API key vs. partner?]" despite clarifications being resolved

**Impact**: Specification appears incomplete, confusion for implementers

**Remediation**:
Update `spec.md` line 106-107:

**Current**:
```markdown
- **FR-007**: System MUST display different content/features based on [NEEDS CLARIFICATION: authentication tiers - public vs. API key vs. partner?]
```

**Fixed**:
```markdown
- **FR-007**: System MUST display different content/features based on authentication tier (Public: cached demos only, API Key: custom input + 1000 req/min, Partner: production usage + 5000 req/min)
```

**Files to modify**:
- `spec.md` - Line 106-107

---

## HIGH Priority Issues (Address Before Sprint)

### H001: Ambiguous "Without Redesign" (B003)

**Finding**: FR-013 states "without redesign" but no measurable criteria

**Current**: "System MUST support adding new microservices without redesign"

**Remediation**:
Update to measurable criteria:

```markdown
- **FR-013**: System MUST support adding new microservices with <50 LOC changes (excluding new service-specific templates/routes). Changes limited to: (1) Add service card to landing page, (2) Add route import to main.py, (3) Add navigation link.
```

**Rationale**: "Without redesign" = minimal code changes, reuse existing patterns

**Files to modify**:
- `spec.md` - FR-013 (line 117)

---

### H002: Example Format Details Missing (C001)

**Finding**: T022 (example generator) and data-model.md lack conversation format specification

**Impact**: Generator script may produce inconsistent formats

**Remediation**:
Add to `data-model.md` section 1 (CachedExample):

```markdown
**Conversation Format** (required for all examples):
- Each turn: `{"speaker": str, "content": str}`
- Speaker IDs: Single capital letter (A, B, C...) or role name ("User", "Assistant")
- Content: 50-500 characters per turn recommended
- Total turns: 2-20 (optimized for analysis)
- Character whitelist: UTF-8 alphanumeric + standard punctuation
```

Add to T022 task description:
```markdown
- [ ] **T022** Create example generator script in `scripts/generate_examples.py`
  - Load curated conversations from inline list (format: speaker A-Z, content 50-500 chars)
  - Validate format before calling Observatory
  - Call Observatory /analyze for each
  - Save to app/static/examples/{id}.json
  - Include metadata (type, complexity)
  - Generate 5-10 examples (dialectic=2, collaborative=2, debate=2, exploration=1-4)
```

**Files to modify**:
- `data-model.md` - Add conversation format section
- `tasks.md` - Update T022 description

---

### H003: Visual Presentation Undefined (C002)

**Finding**: FR-005 requires "visual and textual" presentation but no specification of what "visual" means

**Impact**: Designer/implementer has no guidance on visualization requirements

**Remediation**:
Update FR-005 in `spec.md`:

```markdown
- **FR-005**: System MUST present results in multiple formats: (1) Visual: Pattern badges with confidence meters, sentiment trajectory graph, topic tag cloud, (2) Textual: Expandable JSON view, plain-English summary, copy-to-clipboard buttons, (3) Accessible: ARIA labels, semantic HTML, keyboard navigation
```

Add to T018 (demo page template) task:
```markdown
  - Results display area with:
    * Pattern cards (badge + confidence bar)
    * Sentiment graph (line chart or emoji trajectory)
    * Topic tags (colored badges)
    * JSON toggle (expandable <details> element)
```

**Files to modify**:
- `spec.md` - FR-005 (line 102)
- `tasks.md` - T018 description enhancement

---

### H004: Technical Terms in Docs Page (D002)

**Finding**: FR-022 requires "embedded API documentation" - unclear if this is public-facing (violates constitution I: no jargon) or developer-only

**Impact**: Potential constitution violation if API docs use technical terms on public page

**Remediation**:
Clarify FR-022 in `spec.md`:

```markdown
- **FR-022**: System MUST provide embedded API documentation for developers at `/docs` path (separate from public landing/demo pages). Technical terminology allowed in docs section only.
```

Add constitution note to CLAUDE.md:

```markdown
## Technical Documentation Exception

**Constitution I** (Language & Tone) applies to public pages ONLY:
- `/` (landing) - ❌ No technical jargon
- `/demo` - ❌ No technical jargon
- `/docs` - ✅ Technical terms allowed (developer-facing)

Example: Landing page says "Try conversation analysis" not "POST to /api/v1/analyze endpoint"
```

**Files to modify**:
- `spec.md` - FR-022 clarification
- `CLAUDE.md` - Add documentation exception section

---

### H005: Example Conversation Content Missing (G005)

**Finding**: T022 requires "inline list" of curated conversations but none provided

**Impact**: Cannot execute T022 without actual conversation content

**Remediation**:
Create `specs/006-unified-microservice-interface/example-conversations.md`:

```markdown
# Curated Example Conversations

**Purpose**: Source conversations for cached demo generation (T022)

## Dialectic Examples

### dialectic-simple
```json
{
  "id": "dialectic-simple",
  "title": "Truth and Perception",
  "description": "Two perspectives on objective vs. subjective truth",
  "conversation": [
    {"speaker": "A", "content": "Truth is objective and exists independently of our perceptions. Mathematical proofs demonstrate this - 2+2=4 regardless of belief."},
    {"speaker": "B", "content": "But our perception shapes what we recognize as truth. Different cultures have different 'truths' about morality and meaning."},
    {"speaker": "A", "content": "Cultural truths are values, not truths. Values vary, but facts remain constant across contexts."},
    {"speaker": "B", "content": "Yet quantum physics shows observation affects reality itself. The observer and observed are inseparable."}
  ]
}
```

### dialectic-complex
```json
{
  "id": "dialectic-complex",
  "title": "Free Will Paradox",
  "description": "Determinism vs. agency in decision-making",
  "conversation": [
    {"speaker": "A", "content": "If the universe is deterministic, free will is an illusion. Every choice is predetermined by prior causes."},
    {"speaker": "B", "content": "Determinism and free will aren't mutually exclusive. We can be determined to make genuine choices."},
    {"speaker": "A", "content": "That's compatibilism, but it redefines 'free will' to mean something less than true agency."},
    {"speaker": "B", "content": "True agency may be incoherent. What would uncaused choices even mean? Random isn't free."},
    {"speaker": "A", "content": "Perhaps freedom exists in the meta-level - we can reflect on and reshape our decision-making processes."},
    {"speaker": "B", "content": "But that reflection is also determined. We're circles reasoning about our own circumference."}
  ]
}
```

## Collaborative Examples

### collaborative-simple
```json
{
  "id": "collaborative-simple",
  "title": "Building on Ideas",
  "description": "Co-creating a solution through mutual contribution",
  "conversation": [
    {"speaker": "A", "content": "We need a better way to organize these notes. Maybe tags?"},
    {"speaker": "B", "content": "Tags help, but we also need hierarchy. What about nested tags?"},
    {"speaker": "A", "content": "Nested tags could work. We could have 'Project > Phase > Task' structure."},
    {"speaker": "B", "content": "And make tags auto-suggest based on content analysis. Less manual tagging."},
    {"speaker": "A", "content": "Perfect. So: hierarchical tags + AI suggestions + manual override. I'll sketch the UI."}
  ]
}
```

## Debate Examples

### debate-simple
```json
{
  "id": "debate-simple",
  "title": "Privacy vs. Security",
  "description": "Competing values in technology policy",
  "conversation": [
    {"speaker": "A", "content": "Encryption backdoors are necessary for law enforcement to prevent terrorism."},
    {"speaker": "B", "content": "Backdoors compromise everyone's security. Criminals will use non-backdoored tools anyway."},
    {"speaker": "A", "content": "But without access, we can't investigate serious crimes. Public safety outweighs privacy."},
    {"speaker": "B", "content": "History shows governments abuse surveillance powers. Privacy is a fundamental right."}
  ]
}
```

## Exploration Examples

### exploration-simple
```json
{
  "id": "exploration-simple",
  "title": "Understanding Consciousness",
  "description": "Open-ended inquiry into the nature of awareness",
  "conversation": [
    {"speaker": "A", "content": "What makes something conscious? Is it just information processing?"},
    {"speaker": "B", "content": "Computers process information but don't seem conscious. Maybe it's about integration?"},
    {"speaker": "A", "content": "Integrated Information Theory suggests that. But how do we measure integration?"},
    {"speaker": "B", "content": "And does integration alone create experience, or just the appearance of it?"},
    {"speaker": "A", "content": "Perhaps consciousness is more fundamental than we think - not created but revealed."}
  ]
}
```
```

Update T022 in tasks.md:
```markdown
- [ ] **T022** Create example generator script in `scripts/generate_examples.py`
  - Load curated conversations from `specs/006-unified-microservice-interface/example-conversations.md`
  - Parse markdown JSON blocks
  - Call Observatory /analyze for each
  - Save to app/static/examples/{id}.json
  - Include metadata (type, complexity, generated_at timestamp)
  - Generate 5 examples minimum (1 of each type)
```

**Files to create**:
- `specs/006-unified-microservice-interface/example-conversations.md`

**Files to modify**:
- `tasks.md` - Update T022 to reference example-conversations.md

---

### H006: Timeline Dependency on Observatory (D003)

**Finding**: Quickstart assumes Observatory is "running on localhost:8000" but Feature 001 may not be deployed

**Impact**: Cannot validate web interface without Observatory

**Remediation**:
Add prerequisite check to quickstart.md:

```markdown
## Prerequisites

- Python 3.11+
- uv package manager
- **Observatory service running on http://localhost:8000** ⚠️
  - Verify: `curl http://localhost:8000/health` returns 200
  - If not running: `cd services/observatory && uv run uvicorn app.main:app`
  - If not built: Complete Feature 001 first (see specs/001-atrium-observatory-service/)
- Observatory API keys generated (dev-api-keys.txt)
  - Generate: `cd services/observatory && uv run python scripts/generate_api_keys.py`
```

Add to plan.md dependencies:

```markdown
## External Dependencies

- **Feature 001 (Observatory Service)**: MUST be deployed and accessible at http://localhost:8000
- **Observatory API Keys**: At least one dev or partner key generated
- **Curated Examples**: 5-10 conversation examples defined (see example-conversations.md)
```

**Files to modify**:
- `quickstart.md` - Enhance prerequisites section (lines 6-11)
- `plan.md` - Add external dependencies section

---

## Remediation Execution Order

**Recommended sequence** (minimizes file conflicts):

1. **C004** - Fix FR-007 placeholder (spec.md) - 2 min
2. **H001** - Clarify FR-013 "without redesign" (spec.md) - 3 min
3. **H003** - Define FR-005 visual presentation (spec.md) - 5 min
4. **H004** - Clarify FR-022 technical docs (spec.md) - 3 min
5. **C002** - Fix DemoRequest entity (data-model.md) - 10 min
6. **H002** - Add conversation format spec (data-model.md) - 5 min
7. **H005** - Create example-conversations.md - 15 min
8. **C001** - Add T029 health status task (tasks.md) - 5 min
9. **H002** - Update T022 description (tasks.md) - 3 min
10. **C003** - Add TDD gate + script (tasks.md, scripts/) - 15 min
11. **H004** - Add constitution exception (CLAUDE.md) - 5 min
12. **H006** - Enhance prerequisites (quickstart.md, plan.md) - 5 min

**Total estimated time**: 76 minutes (~1.5 hours)

---

## Validation Checklist

After remediation, verify:

- [ ] No "[NEEDS CLARIFICATION]" text in spec.md
- [ ] All 24 FRs testable and unambiguous
- [ ] All tasks reference specific file paths
- [ ] TDD gate script executable (`chmod +x scripts/validate-tdd-gate.sh`)
- [ ] example-conversations.md has 5+ complete examples
- [ ] data-model.md DemoRequest lifecycle clear
- [ ] Constitution alignment maintained (run analyze again)

---

## Post-Remediation Actions

1. **Re-run analysis**: `Task subagent analyze.prompt.md` to verify fixes
2. **Commit changes**: Single commit with all remediation fixes
3. **Update plan.md**: Mark "Analysis findings remediated" in Phase 0
4. **Proceed to implementation**: Begin Phase 3.1 (T001-T003)

---

**Remediation plan by**: Claude Code (Sonnet 4.5)
**Based on**: Cross-artifact analysis findings
**Priority**: Address before starting implementation (T001)
