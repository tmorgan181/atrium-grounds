# Collaboration Add-On Guide for Spec-Kit Workflow

**Purpose**: Enforce multi-agent collaboration structure within the specify workflow
**Applies To**: All features using multi-agent development (Claude Code, Copilot CLI, Human)

---

## Overview

The **collaboration add-on** extends the spec-kit protocol (`/orient`, `/specify`, `/plan`, `/tasks`, `/implement`) with real-time coordination mechanisms for parallel multi-agent development.

### Spec-Kit Provides:
- Feature specifications (`spec.md`, `plan.md`, `tasks.md`)
- Implementation guidance (`/implement`)
- Single-agent workflow

### Collaboration Add-On Provides:
- **Real-time coordination** between agents
- **Session tracking** for work history
- **Handoff mechanisms** for parallel work
- **Validation protocols** for quality assurance
- **Decision logging** for rationale preservation

---

## Required Directory Structure

For every feature using multi-agent development, create:

```
specs/[feature-name]/
├── spec.md                      # Feature specification (spec-kit)
├── plan.md                      # Implementation plan (spec-kit)
├── tasks.md                     # Task breakdown (spec-kit)
└── collaboration/               # Collaboration add-on
    ├── README.md                # Collaboration guide (copy from template)
    ├── [AGENT]-HANDOFF.md       # Active handoff docs (at root, not in status/)
    ├── HUMAN-VALIDATION-GUIDE.md # Manual testing reference
    ├── planning/                # Planning docs (archived after implementation)
    │   └── README.md            # Planning index
    ├── proposals/               # Change proposals & suggestions
    ├── results/                 # Analysis, reviews, validation reports
    ├── reviews/                 # Code reviews & task reviews
    ├── sessions/                # Session logs from agent work
    │   └── archive/             # Archived/completed sessions
    └── status/                  # DEPRECATED - use root for handoffs
```

---

## Enforcement Rules for AI Agents

### 1. Session Logging (MANDATORY)

**When**: After completing significant work (3+ tasks or major milestone)

**What**: Create session log in `collaboration/sessions/`

**Format**: `YYYY-MM-DD-[agent]-[tasks].md`

**Must Include**:
- Date and agent identifier
- Tasks completed (with IDs from tasks.md)
- Changes made (files modified)
- Next steps or handoff information
- Any blockers or decisions

**Example**:
```markdown
# Session: 2025-10-05 - Claude Code - T023-T027

## Tasks Completed
- T023: Code refactoring (remove duplication)
- T022: Performance validation (<100ms overhead)
- T025: Update CLEAN-LOGGING.md
- T026: Create MIGRATION-002.md
- T027: Run validation checklist

## Changes Made
- `quick-start.ps1`: Added Get-PythonExePath, Invoke-TestSuite helpers
- `docs/CLEAN-LOGGING.md`: Updated integration section
- `docs/MIGRATION-002.md`: Created migration guide
- `scripts/performance-validation.ps1`: Created validation script
- `docs/VALIDATION-CHECKLIST-002.md`: Created validation results

## Next Steps
- Waiting for Copilot to complete T019-T021, T028
- Ready for merge after Copilot tasks

## Status
Progress: 24/28 tasks complete (86%)
```

### 2. Handoff Documents (REQUIRED for delegation)

**When**: Delegating work to another agent

**Where**: `collaboration/[AGENT]-HANDOFF.md` (at root, NOT in status/)

**Format**: Clear, actionable instructions

**Must Include**:
- What tasks to complete
- Context needed (what's already done)
- Specific files/code to modify
- Acceptance criteria
- Testing instructions
- Commit template

**Remove/Update**: Immediately after handoff is complete

**Example**: See `collaboration/COPILOT-HANDOFF.md` in Feature 002

### 3. Planning Documents (Optional, archive after implementation)

**When**: Creating design/planning docs during development

**Where**: `collaboration/planning/[TOPIC].md`

**After Implementation**: Add README.md explaining what was implemented

**Example**:
```
collaboration/planning/
├── README.md           # "LINTING.md implemented in T013-T015"
├── LINTING.md          # Planning doc
├── TEST-FILTERING.md   # Planning doc
└── NEXT-STEPS.md       # Roadmap
```

### 4. Decision Logging (REQUIRED for deviations)

**When**: Deviating from spec or making architectural choices

**Where**: `collaboration/decisions/DECISION-[topic].md`

**Must Include**:
- Problem statement
- Options considered
- Decision made
- Rationale
- Tradeoffs

### 5. Validation Reports (REQUIRED after testing)

**When**: Completing validation or testing tasks

**Where**: `collaboration/results/VALIDATION-[date].md` or `[TOPIC]-RESULTS.md`

**Must Include**:
- What was tested
- Test results (pass/fail counts)
- Known issues
- Sign-off status

---

## Workflow Integration with Spec-Kit

### Phase 1: Specification (`/specify`)
- **Output**: `spec.md`
- **Collaboration**: Not applicable (single-agent)

### Phase 2: Planning (`/plan`)
- **Output**: `plan.md`
- **Collaboration**: Create `collaboration/README.md` if multi-agent

### Phase 3: Task Breakdown (`/tasks`)
- **Output**: `tasks.md`
- **Collaboration**: Identify parallel tasks, plan agent assignments

### Phase 4: Implementation (`/implement`)
- **Agents Start**: Create `collaboration/sessions/` for tracking
- **Parallel Work**: Use `[AGENT]-HANDOFF.md` for delegation
- **Decisions**: Log in `collaboration/decisions/` when needed
- **Results**: Document in `collaboration/results/`

### Phase 5: Validation
- **Validation**: Create validation report in `collaboration/results/`
- **Manual Testing**: Use `collaboration/HUMAN-VALIDATION-GUIDE.md`
- **Sign-off**: Update validation report with approval

### Phase 6: Completion
- **Archive Sessions**: Move to `collaboration/sessions/archive/`
- **Remove Handoffs**: Clear completed handoffs
- **Summarize**: Create feature retrospective in `collaboration/results/`

---

## File Naming Standards (ENFORCE STRICTLY)

### Dates
- **Format**: `YYYY-MM-DD` (e.g., `2025-10-05`)
- **Bad**: `10-05-2025`, `2025/10/05`, `Oct-5-2025`

### Agents
- **Valid**: `claude`, `copilot`, `human`
- **Lowercase**: Always lowercase
- **Bad**: `Claude`, `Copilot-CLI`, `HUMAN`

### Tasks
- **Reference**: Use task IDs from `tasks.md` (e.g., `T016-T024`)
- **Range**: Use hyphens for ranges
- **Bad**: `T016,T024`, `Tasks-16-24`

### Topics
- **Format**: `kebab-case` (e.g., `task-split-proposal`)
- **Bad**: `TaskSplitProposal`, `task_split_proposal`, `TASK-SPLIT-PROPOSAL`

### Document Types
- **Format**: `UPPERCASE` prefix (e.g., `HANDOFF`, `PROPOSAL`, `DECISION`, `SESSION`)
- **Location**:
  - Handoffs: `[AGENT]-HANDOFF.md` (root)
  - Proposals: `proposals/PROPOSAL-[topic].md`
  - Decisions: `decisions/DECISION-[topic].md`
  - Sessions: `sessions/YYYY-MM-DD-[agent]-[tasks].md`

---

## Common Violations and Fixes

### ❌ Violation: Session logs missing
**Fix**: Create session log after every work session (3+ tasks)

### ❌ Violation: Stale handoff in `status/`
**Fix**:
1. Move handoff to collaboration root
2. Remove immediately after completion
3. Deprecate `status/` directory

### ❌ Violation: No decision log for spec deviation
**Fix**: Create `collaboration/decisions/DECISION-[topic].md` with rationale

### ❌ Violation: Planning docs scattered in various locations
**Fix**: Move to `collaboration/planning/` with README explaining implementation

### ❌ Violation: Validation results not documented
**Fix**: Create `collaboration/results/VALIDATION-[date].md` with test results

### ❌ Violation: Mixed naming conventions
**Fix**: Enforce standards (dates: YYYY-MM-DD, agents: lowercase, topics: kebab-case)

---

## Template Files

### Session Log Template

```markdown
# Session: [DATE] - [Agent] - [Tasks]

## Tasks Completed
- T###: [Description]
- T###: [Description]

## Changes Made
- `file/path.ext`: [What changed]
- `another/file.ext`: [What changed]

## Decisions Made
- [Decision]: [Rationale]

## Next Steps
- [What's next]
- [Handoff info if applicable]

## Status
Progress: X/Y tasks complete (Z%)
```

### Handoff Template

```markdown
# [Agent] Handoff - [Feature]

**Status**: [Active/Waiting/Complete]
**Your Tasks**: [Task IDs]

## Quick Context
[Brief summary of feature and current state]

## Your Tasks

### Task 1: [Task ID] - [Description]
**File**: [Path]
**What to Do**: [Clear instructions]
**Acceptance**: [How to verify]

### Task 2: [Task ID] - [Description]
[Same format]

## Testing
[How to test your changes]

## Commit Template
[Pre-filled commit message template]

## Questions?
[Where to find more info]
```

### Planning README Template

```markdown
# [Feature] Planning Documents

Planning documents created during [Feature] development, superseded by implementation.

## Documents

### [TOPIC].md
**Status**: ✅ Implemented ([Task IDs])
**Purpose**: [What was planned]
**Implementation**: [What was built]
**See**: [Links to actual implementation]

---

**Maintained By**: [Team]
**Last Updated**: [Date]
```

---

## Checklist for AI Agents

Before claiming a feature is complete, verify:

- [ ] All session logs created in `collaboration/sessions/`
- [ ] Handoff documents removed or marked complete
- [ ] Planning docs moved to `collaboration/planning/` with README
- [ ] Decisions logged in `collaboration/decisions/` (if any deviations)
- [ ] Validation report created in `collaboration/results/`
- [ ] HUMAN-VALIDATION-GUIDE.md updated (if applicable)
- [ ] Old sessions archived to `sessions/archive/`
- [ ] File naming follows standards (dates, agents, tasks, topics)
- [ ] collaboration/README.md updated with current structure

---

## Benefits of Strict Enforcement

1. **Transparency** - Clear record of who did what and when
2. **Coordination** - Agents can work in parallel without conflicts
3. **Context Preservation** - New agents/humans can understand history
4. **Quality Assurance** - Validation is documented and verifiable
5. **Accountability** - Decisions and deviations are logged with rationale
6. **Discoverability** - Consistent structure makes information easy to find
7. **Onboarding** - New contributors understand the process

---

## Questions or Improvements?

This is an evolving protocol. Suggest improvements by:
1. Creating a proposal in `collaboration/proposals/`
2. Discussing in feature issues
3. Updating this guide with consensus

**Remember**: This structure enables effective multi-agent development. Enforce it consistently, but don't let it become bureaucratic. The goal is coordination, not paperwork.

---

**Version**: 2.0
**Last Updated**: 2025-10-05
**Applies To**: All features in atrium-grounds using multi-agent development
**Template Source**: `specs/002-developer-experience-upgrades/collaboration/README.md`
