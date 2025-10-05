
# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code, or `AGENTS.md` for all other agents).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Add comprehensive verbosity controls and developer experience enhancements to the Observatory service quick-start script, providing clean minimal output by default while preserving detailed diagnostics on demand. Integrates with existing clean logging solution for Windows-friendly server output.

**Primary Requirement**: Enable developers to work efficiently with scannable output while having full diagnostic capability when troubleshooting
**Technical Approach**: PowerShell parameter-based verbosity control with output redirection and integration with existing Python clean logging implementation

## Technical Context
**Language/Version**: PowerShell 5.1+ (Windows PowerShell) / PowerShell Core 7+ (cross-platform)
**Primary Dependencies**: uv (Python package manager), pytest (testing), ruff (linting/formatting), FastAPI/uvicorn (existing service)
**Storage**: N/A (tooling feature - no persistent data)
**Testing**: Manual validation via test matrix, existing pytest test suite
**Target Platform**: Windows (primary), macOS/Linux (secondary via PowerShell Core)
**Project Type**: Single project (PowerShell scripting - modifications to existing quick-start.ps1)
**Performance Goals**: <100ms overhead for verbosity control, efficient output streaming (no full buffering)
**Constraints**: Backward compatibility required (existing commands must work unchanged), Windows terminal compatibility
**Scale/Scope**: 29 functional requirements, 6 new CLI flags, 3 new actions (lint/format/check), integration with existing clean logging

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I - Language & Tone Standards
✅ **PASS** - Technical documentation uses precise terms (PowerShell, pytest, verbosity control)
- Avoids mystical language, uses clear developer-focused terminology
- Terms like "clean output", "diagnostic mode", "verbosity control" are industry-standard

### Principle II - Ethical Boundaries
✅ **PASS** - No privacy concerns (tooling feature only)
- No access to private data or conversation archives
- No data storage or transmission beyond local development workflow

### Principle III - Progressive Disclosure
✅ **PASS** - Default experience serves beginners, advanced flags for power users
- Minimal output by default (clean, scannable for new developers)
- `-Detail` flag provides full diagnostics (experienced developers troubleshooting)
- `-Clean` flag for platform-specific needs (Windows compatibility)

### Principle IV - Multi-Interface Access
✅ **PASS** - Serves both human developers and AI agents
- CLI tool enables both manual and automated workflows
- Structured output (status indicators: [OK], [FAIL], [WARN]) parseable by AI agents
- Clear help text and examples for both human and AI collaborators

### Principle V - Invitation Over Intrusion
✅ **PASS** - Respectful, optional enhancements
- All new flags are optional with sensible defaults
- No breaking changes to existing workflows
- Help text provides clear usage examples and guidance

### Principle VI - Service Independence
✅ **PASS** - Tooling enhancement maintains clean boundaries
- Modifies only quick-start.ps1 and integrates with existing clean logging
- No cross-service dependencies introduced
- Clean integration with existing Python clean logging implementation

### Principle VII - Groundskeeper Stewardship
✅ **PASS** - Quality-focused, thoughtful enhancement
- Improves developer experience without rushing
- Integrates cleanly with Copilot's prior work (clean logging)
- Maintains code quality and documentation standards

### Principle VIII - Technical Pragmatism
✅ **PASS** - Technical choices serve constitutional principles
- PowerShell parameters enable multi-agent collaboration (Principle IV)
- Clean logging serves Windows developers (Principle V - invitation)
- Centralized verbosity logic avoids duplication (maintainability)
- Leverages existing pytest/ruff capabilities (no reinvention)

**Initial Assessment**: ✅ NO VIOLATIONS - All principles satisfied, ready for Phase 0 research

**Style Note**: Spec.md uses RFC 2119 keywords (MUST, SHOULD) for requirements precision. Plan.md uses conversational style for readability.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
services/observatory/
├── quick-start.ps1          # PRIMARY: Modified for verbosity control
├── run_clean_server.py      # EXISTING: Copilot's clean logging (integration point)
├── app/
│   └── core/
│       └── log_config.py    # EXISTING: Copilot's clean logging formatter
├── tests/
│   ├── unit/                # EXISTING: Unit tests (pytest -q vs -v)
│   ├── contract/            # EXISTING: Contract tests
│   └── integration/         # EXISTING: Integration tests
└── docs/
    └── CLEAN-LOGGING.md     # EXISTING: Copilot's clean logging docs

.specify/
└── scripts/
    └── powershell/
        └── update-agent-context.ps1  # EXISTING: Script to update Copilot instructions
```

**Structure Decision**: Single project enhancement - modifies existing `quick-start.ps1` with new parameters and helper functions. No new services or packages created. Clean integration with existing Copilot clean logging implementation (run_clean_server.py, log_config.py). All functionality implemented as PowerShell parameters and functions within the existing script structure.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) ✅
- [x] Phase 1: Design complete (/plan command) ✅
- [x] Phase 2: Task planning complete (/plan command - describe approach only) ✅
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅
- [x] All NEEDS CLARIFICATION resolved ✅
- [x] Complexity deviations documented (N/A - no violations) ✅

**Artifacts Generated**:
- [x] research.md (Phase 0)
- [x] contracts/parameters.md (Phase 1)
- [x] contracts/ directory (auto-generated contracts)
- [x] quickstart.md (Phase 1)
- [ ] tasks.md (awaiting /tasks command)

---
*Based on Constitution v1.3.0 - See `.specify/memory/constitution.md`*
