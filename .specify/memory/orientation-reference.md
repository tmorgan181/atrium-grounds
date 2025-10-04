# Agent Orientation Reference

## For Copilot Instructions

Add this section to project-specific `.github/copilot-instructions.md`:

```markdown
## Orientation Protocol

**Before starting work**: Run `/orient` or manually review:
1. This file (copilot-instructions.md) - **PRIMARY SOURCE** (both template and living document)
2. `.specify/memory/constitution.md` - project philosophy and principles
3. Current git state - branch, recent work, existing specs
4. Coordination needs - other agents, territories, blockers

**Token efficiency required**:
- Output essentials only (~150-200 words)
- Combine steps where possible
- Brief summaries not quotes
- Direct answers no preambles
- State conclusions first, details after

**Development voice**:
- Precise, brief, direct, practical, efficient
- No verbosity, apologies, hedging, or ceremony
- Ask clarifying questions before lengthy work
- Optimize for minimal cognitive load

**See**: `.github/prompts/orient.prompt.md` for detailed protocol.
```

---

## For Project README

Add this section to project `README.md`:

```markdown
## Getting Started

### Orientation (Required First Step)

**Command**: `/orient`  
**Manual**: See `.github/prompts/orient.prompt.md`

Orientation helps you understand:
- Project purpose and principles
- Technical stack and conventions
- Current state and existing work
- Coordination with other agents

**Keep it brief**: ~150-200 word output. Token efficiency matters.

**Primary source**: `.github/copilot-instructions.md` (both template and living document)
```

---

## For Onboarding Documents

```markdown
## Onboarding Checklist

- [ ] **Run `/orient`** (REQUIRED - keep output brief, ~150-200 words)
- [ ] Understand token efficiency requirements (essentials only)
- [ ] Learn development voice (precise, brief, direct)
- [ ] Install dependencies
- [ ] Choose first task

**Development Guidelines**:
- Token conservation: Combine steps, minimize output, be concise
- Voice: Direct and practical, no verbosity or ceremony
- Features: Minimal viable, single-purpose, obviously named
- Docs: Scannable, front-loaded, example-driven, brief
```

---

## Key Changes from Previous Version

**Copilot-instructions.md is PRIMARY**:
- No separate template file
- File itself is both template (with placeholders) and living document
- Read this FIRST before other orientation steps

**Token Efficiency Added**:
- ~150-200 word orientation outputs
- Combine steps where possible
- Brief summaries not full quotes
- No preambles or ceremony

**Development Voice Defined**:
- Precise, brief, direct, practical, efficient
- No verbosity, apologies, hedging
- State conclusions first
- Ask before lengthy work

**Cognitive Load Optimization**:
- Features: minimal, self-contained, obviously named
- Docs: scannable, front-loaded, example-driven
- Specs: one page ideally, concrete, testable
