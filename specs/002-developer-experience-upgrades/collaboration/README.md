# Collaboration Directory

**Feature**: 002 Developer Experience Upgrades  
**Purpose**: Multi-agent coordination and communication

---

## Overview

This directory is an **add-on to the spec-kit protocol** for multi-agent collaboration. It facilitates coordination between AI agents (Claude Code, Copilot CLI) and human developers working on the same feature.

The spec-kit provides feature specifications (`spec.md`, `plan.md`, `tasks.md`). This collaboration layer adds real-time coordination mechanisms for parallel development.

---

## Directory Structure

```
collaboration/
├── README.md                    # This file
├── HUMAN-VALIDATION-GUIDE.md    # Reference guide for manual testing
├── decisions/                   # Implementation decisions & tradeoffs
├── proposals/                   # Change proposals & suggestions
├── results/                     # Analysis, reviews, validation reports
├── reviews/                     # Code reviews & task reviews
├── sessions/                    # Session logs from agent work
│   └── archive/                 # Archived/completed sessions
└── status/                      # Active handoffs & delegation docs
```

---

## When to Use Each Directory

### `decisions/`
Log implementation decisions when:
- Deviating from original spec
- Choosing between multiple approaches
- Making architectural tradeoffs
- Encountering ambiguity requiring clarification

**Format**: `DECISION-[topic].md` with rationale and alternatives considered

### `proposals/`
Submit proposals for:
- Task breakdown changes
- Scope adjustments
- Process improvements
- Architecture modifications

**Format**: `PROPOSAL-[topic].md` with problem statement and proposed solution

### `results/`
Document outcomes including:
- Validation reports
- Analysis results
- Feature reviews
- Performance benchmarks

**Format**: `[TOPIC]-[date].md` or task-specific like `T016-T024-VALIDATION.md`

### `reviews/`
Provide reviews of:
- Code changes
- Task implementations
- Pull requests
- Design decisions

**Format**: `REVIEW-[topic].md` with findings and recommendations

### `sessions/`
Record session logs showing:
- Agent work sessions
- Tasks completed
- Changes made
- Handoff information

**Format**: `YYYY-MM-DD-[agent]-[tasks].md` or `SESSION-[number]-[agent].md`

**Archive**: Move completed sessions to `archive/` to reduce clutter

### `status/`
Maintain active coordination docs:
- Handoff documents (delegation between agents)
- Current work assignments
- Blocking issues
- Coordination state

**Format**: `[AGENT]-HANDOFF.md` for delegations, `STATUS-[date].md` for snapshots

---

## Multi-Agent Workflow

### Typical Coordination Flow

1. **Agent 1 (Claude Code)** completes tasks, documents in `sessions/`
2. Agent 1 creates handoff in `status/` delegating work to Agent 2
3. **Agent 2 (Copilot CLI)** reads handoff, completes assigned tasks
4. Agent 2 logs session, creates validation report in `results/`
5. Agent 2 updates or removes handoff when complete
6. Cycle continues with new delegations as needed

### Communication Patterns

**Synchronous**: Via `status/` handoff documents (primary)  
**Asynchronous**: Via `proposals/` and `reviews/`  
**Historical**: Via `sessions/` logs and `results/` reports  
**Decisional**: Via `decisions/` records

---

## Integration with Spec-Kit

The spec-kit (`.github/prompts/`) provides:
- `/orient` - Project orientation
- `/specify` - Feature specification
- `/plan` - Implementation planning
- `/tasks` - Task breakdown
- `/implement` - Implementation execution

This collaboration layer adds:
- **Real-time coordination** between agents
- **Session tracking** for work history
- **Handoff mechanisms** for parallel work
- **Validation protocols** for quality assurance
- **Decision logging** for rationale preservation

Together they enable effective multi-agent feature development with clear boundaries, communication channels, and historical context.

---

## Best Practices

### For AI Agents

**Do**:
- Update `status/` when delegating or receiving work
- Log sessions in `sessions/` after significant work
- Document decisions in `decisions/` when deviating from plan
- Create validation reports in `results/` after testing
- Archive old sessions to keep workspace clean

**Don't**:
- Leave stale handoffs in `status/` after completion
- Mix different types of documents (keep categories distinct)
- Create redundant documentation (check existing files first)
- Commit sensitive data or test artifacts

### For Humans

**Do**:
- Use HUMAN-VALIDATION-GUIDE.md for manual testing
- Review `status/` to understand current agent assignments
- Check `sessions/` for historical context
- Read `decisions/` when questioning implementation choices
- Provide feedback via `reviews/` directory

**Don't**:
- Modify agent handoffs without coordination
- Delete session logs (archive instead)
- Expect real-time updates (agents work asynchronously)

---

## File Naming Conventions

- **Dates**: `YYYY-MM-DD` format (e.g., `2025-01-04`)
- **Agents**: `claude`, `copilot`, `human`
- **Tasks**: Reference task IDs when applicable (e.g., `T016-T024`)
- **Topics**: Descriptive kebab-case (e.g., `task-split-proposal`)
- **Uppercase**: Use for document types (HANDOFF, PROPOSAL, DECISION, etc.)

---

## Maintenance

### Regular Cleanup

- Archive completed session logs monthly
- Remove resolved handoffs from `status/`
- Consolidate related proposals/decisions when feature completes
- Update HUMAN-VALIDATION-GUIDE.md as features change

### Feature Completion

When feature is complete:
- Consolidate key decisions into feature retrospective
- Archive all sessions
- Clear `status/` directory
- Keep validation guides if feature is extensible
- Summarize learnings for future features

---

## Questions?

This is an evolving protocol. Improvements welcome via:
- Proposals in `proposals/` directory
- Discussion in feature issues
- Updates to `.github/copilot-instructions.md`

**Remember**: This collaboration structure enables parallel multi-agent development. Use it to coordinate, not to create bureaucracy.

---

**Version**: 1.0  
**Last Updated**: 2025-01-04  
**Applies To**: All features using multi-agent development
