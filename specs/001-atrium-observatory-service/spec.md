# Feature Specification: Atrium Observatory Service

**Feature Branch**: `001-atrium-observatory-service`
**Created**: 2025-10-04
**Status**: Planning Complete
**Input**: User description: "Observatory service for conversation analysis with API endpoints (no direct private archive access; curated/public or user-provided data)."

## Execution Flow (main)
```
1. Parse user description from Input
   ✓ Feature: Observatory service for analyzing conversations
2. Extract key concepts from description
   ✓ Actors: API consumers (humans, AI systems)
   ✓ Actions: Analyze conversations, detect patterns, extract insights
   ✓ Data: Conversation transcripts (curated public examples or user-provided data)
   ✓ Constraints: Must not expose private archives directly (ethical boundaries principle)
3. For each unclear aspect:
   ✓ Pattern types: dialectic, sentiment, topic clustering, interaction dynamics
   ✓ Authentication: Public tier → API keys → OAuth/JWT for partners
   ✓ Rate limits: 10/60/600 req/min for public/API/partner tiers
   ✓ Data retention: 30-day results, 90-day metadata, indefinite aggregated insights
   ✓ Batch processing: Up to 1,000 conversations, async with webhooks
4. Fill User Scenarios & Testing section
   ✓ Primary scenarios identified
5. Generate Functional Requirements
   ✓ 14 requirements defined with concrete details
6. Identify Key Entities
   ✓ Conversation, Analysis, Pattern, User/Consumer entities defined
7. Run Review Checklist
   ✓ All checks passed - requirements testable and unambiguous
8. Constitution Audit
   ✓ 100% compliance across all seven principles
   ✓ Added FR-014 for data export
   ✓ Groundskeeper curation workflow documented
9. Return: SUCCESS (spec and plan ready for implementation)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
A researcher wants to understand patterns in their AI conversations without manually re-reading hundreds of transcripts. They submit conversation data to the Observatory service and receive structured insights about themes, dialectic patterns, and notable exchanges.

An AI system (an advanced AI agent capable of autonomous reasoning and learning) needs to analyze conversation history to understand context before engaging in dialogue. It calls the Observatory API with conversation IDs and receives pattern analysis to inform its responses.

### Acceptance Scenarios
1. **Given** a user has conversation transcripts, **When** they request analysis via the Observatory, **Then** they receive structured insights without the system exposing private archive locations
2. **Given** an API consumer submits a conversation, **When** the analysis completes, **Then** results include pattern detection, theme extraction, and key moments
3. **Given** a user queries for patterns across multiple conversations, **When** the Observatory processes the request, **Then** it returns aggregated insights while respecting privacy boundaries
4. **Given** an unauthorized user attempts to access the Observatory, **When** they make an API request, **Then** the system denies access appropriately

### Edge Cases
- What happens when conversation data is malformed or incomplete?
- How does the system handle very large conversations (10K+ messages)?
- What if analysis requests exceed rate limits?
- How are results handled when analysis fails or times out?
- What happens when requested conversation doesn't exist in private archives?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST accept conversation data for analysis without requiring direct access to private Atrium archives
- **FR-002**: System MUST provide API endpoints accessible to both human users and AI systems (progressive disclosure principle)
- **FR-003**: System MUST detect patterns in conversations including:
  - **Dialectic patterns**: Question-answer flows, thesis-antithesis-synthesis progressions, Socratic exchanges
  - **Sentiment analysis**: Emotional tone shifts, engagement levels, collaborative vs adversarial dynamics
  - **Topic clustering**: Thematic groupings, subject transitions, concept relationships
  - **Interaction dynamics**: Turn-taking patterns, response latencies, conversational reciprocity
- **FR-004**: System MUST extract key themes and insights from conversation transcripts
- **FR-005**: System MUST return structured analysis results in machine-readable format
- **FR-006**: System MUST authenticate API consumers via public tier (no auth), API keys, or OAuth/JWT for partners
- **FR-007**: System MUST respect ethical boundaries by never exposing private archive file paths or locations
- **FR-008**: System MUST handle requests using curated example conversations without private archive dependencies (examples managed via groundskeeper curation workflow)
- **FR-009**: System MUST enforce rate limiting at 10/60/600 requests per minute for public/API key/partner tiers respectively
- **FR-010**: System MUST log all analysis requests for transparency and debugging
- **FR-011**: System MUST support both real-time and batch analysis modes with async processing and webhook notifications
- **FR-012**: System MUST provide analysis confidence scores (0.0-1.0) or quality indicators based on conversation length, pattern clarity, and model certainty
- **FR-013**: System MUST retain analysis results for 30 days after last access, metadata for 90 days, with indefinite aggregated insights
- **FR-014**: System MUST provide analysis result export in standard formats (JSON, CSV, Markdown) enabling users to retain insights independently of the service

### Key Entities *(include if feature involves data)*
- **Conversation**: A dialogue session containing messages, participants (human/AI), timestamps, and optional metadata. Represents the raw material for analysis.
- **Analysis**: The output of processing a conversation, including detected patterns, themes, insights, and confidence scores. Links to the source conversation but contains derived data.
- **Pattern**: A recognized structure or trend within conversations (e.g., dialectic progression, topic shift, question-answer pairs). Can span single or multiple conversations.
- **User/Consumer**: API consumer (human or AI system) requesting analysis. Has access permissions and usage quotas.

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed
- [x] Clarifications addressed
- [x] Spec ready for planning

---

## Next Steps

**Clarifications Addressed**:

1. **Pattern types**: Dialectic patterns, sentiment analysis, topic clustering, interaction dynamics (recursive patterns deferred to future enhancement)
2. **Authentication**: Public tier (strict limits) → API keys (higher limits) → OAuth/JWT for partners
3. **Rate limits**: Public (10/min, 500/day), API key (60/min, 5K/day), Partner (600/min, 50K/day)
4. **Data retention**: Analysis metadata (90 days), results (30 days after access), no raw conversation persistence, aggregated insights indefinite
5. **Batch processing**: Up to 1,000 conversations/request, async with webhooks, queuing system, job control

**Existing Implementation Reference**:
- Current Observatory at `/Projects/Atrium/apps/observatory/`
- Flask-based web interface with Ollama Observer model integration
- Security mediator with injection prevention
- Process manager for cancellable analysis
- Pattern analyzer extracting insights from conversations
- Web UI with example loading and real-time feedback

**Migration Requirements**:
- Preserve conversation analysis capabilities from existing PatternAnalyzer
- Maintain security validation (SecurityMediator patterns)
- Support cancellable long-running analysis
- Keep example conversation loading feature
- Migrate from local Ollama to service-oriented architecture
