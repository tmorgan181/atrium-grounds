# Pull Request Workflow Guide

**Project**: atrium-grounds  
**Last Updated**: 2025-01-05  
**Audience**: AI coding agents, human developers  

## Overview

This guide defines when and how to create Pull Requests (PRs) in the atrium-grounds repository, especially for AI coding agents working on features autonomously or in multi-agent collaboration scenarios.

## Core Principle

**PRs are manual decision points, not automatic events.** They represent a conscious choice to request review before merging code into a protected branch.

## When AI Agents MUST Create PRs

### 1. Feature Completion
When a feature specification (from `specs/`) is fully implemented:
```bash
# Agent completes Feature 001
git checkout 001-atrium-observatory-service
# ... implementation work ...
git push origin 001-atrium-observatory-service

# Create PR for human review
gh pr create \
  --base main \
  --head 001-atrium-observatory-service \
  --title "Feature 001 Complete: Atrium Observatory Service" \
  --body "$(cat specs/001-atrium-observatory-service/COMPLETION.md)"
```

**Why**: Feature completion represents a major milestone requiring review and documentation.

**Trigger**: When all acceptance criteria in feature spec are met and all tests pass.

### 2. Breaking Changes
Any change that:
- Modifies public APIs
- Changes configuration formats
- Alters database schemas
- Affects existing integrations

```bash
gh pr create \
  --base main \
  --head feature-branch \
  --title "BREAKING: API v2 with new authentication model" \
  --label "breaking-change"
```

**Why**: Breaking changes require explicit approval and migration planning.

**Trigger**: Agent detects API/schema changes during implementation.

### 3. Multi-Agent Handoffs
When one agent completes work and another agent will continue:
```bash
# Agent A completes Phase 1
gh pr create \
  --base main \
  --head 001-phase-1 \
  --title "Feature 001 Phase 1: Core Service" \
  --body "Phase 1 complete. Ready for Agent B to implement Phase 2."
  --assignee agent-b-github-handle
```

**Why**: PRs create clear handoff documentation and prevent work conflicts.

**Trigger**: Agent reaches predetermined handoff checkpoint in feature plan.

### 4. Constitution Compliance Questions
When agent is uncertain if changes comply with project constitution:
```bash
gh pr create \
  --base main \
  --head feature-branch \
  --title "Review Needed: Potential constitution concern" \
  --label "needs-review" \
  --body "Implemented caching layer. Need human review for 'progressive disclosure' principle compliance."
```

**Why**: Constitutional compliance requires human judgment.

**Trigger**: Agent detects potential principle violation or ambiguity.

## When AI Agents Should NOT Create PRs

### 1. Iterative Work-in-Progress Commits
```bash
# Just push to feature branch - no PR yet
git push origin 001-atrium-observatory-service
```

**Reason**: In-progress work doesn't need review until complete.

### 2. Documentation-Only Changes
```bash
# Push directly to branch or main (if allowed)
git checkout main
git add docs/
git commit -m "docs: update API examples"
git push origin main
```

**Reason**: Docs have low risk and benefit from rapid iteration.

**Exception**: Create PR if docs change project architecture decisions.

### 3. Test Additions (No Code Changes)
```bash
# Add tests to feature branch without PR
git push origin 001-atrium-observatory-service
```

**Reason**: More tests = better. No review bottleneck needed.

**Exception**: Create PR if tests reveal design flaws requiring discussion.

### 4. Dependency Updates (Minor Versions)
```bash
# Push dependency updates directly
git commit -m "chore: update pytest 8.0.0 -> 8.0.1"
git push origin main
```

**Reason**: Patch/minor updates are low-risk maintenance.

**Exception**: Create PR for major version bumps (e.g., pytest 8.x -> 9.x).

## PR Creation Workflow for AI Agents

### Step 1: Verify Prerequisites
```bash
# Ensure all tests pass
cd services/observatory
.\quick-start.ps1 test

# Ensure code is formatted
.\quick-start.ps1 format

# Ensure no linting errors
.\quick-start.ps1 lint
```

### Step 2: Push Branch
```bash
git push origin <feature-branch-name>
```

### Step 3: Create PR with Context
```bash
gh pr create \
  --base main \
  --head <feature-branch-name> \
  --title "<type>: <concise description>" \
  --body "$(cat PR_BODY.md)"
```

### Step 4: Add Labels
```bash
gh pr edit <pr-number> --add-label "ai-generated,feature,needs-review"
```

### Step 5: Document in Collaboration Directory
```bash
# Create handoff document
cat > specs/<feature>/collaboration/PR-<number>-handoff.md <<EOF
# PR #<number>: <title>

**Created**: $(date)
**Agent**: <agent-name>
**Status**: Awaiting review

## Summary
<brief summary>

## Testing
<test results>

## Next Steps
<what reviewer should check>
EOF
```

## PR Title Conventions

Format: `<type>(<scope>): <description>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code restructuring
- `test`: Test additions
- `chore`: Maintenance
- `perf`: Performance improvement

**Examples**:
```
feat(001): complete Observatory service implementation
fix(api): resolve rate limiting edge case
docs(readme): add quick-start guide
refactor(004): modularize PowerShell scripts
```

## PR Body Template

```markdown
## What Changed
Brief description of changes.

## Why
Rationale for the change.

## Testing
- [ ] Unit tests pass (X/X)
- [ ] Contract tests pass (X/X)
- [ ] Integration tests pass (X/X)
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented if necessary)
- [ ] Constitution compliance verified

## Agent Attribution
via <model-name> @ <interface>

## Related
- Closes #<issue>
- Related to Feature <number>
- Depends on PR #<number>
```

## Multi-Agent PR Workflow

### Scenario: Agent A implements, Agent B reviews

**Agent A (Implementation)**:
```bash
# Complete feature work
git push origin 001-atrium-observatory-service

# Create PR
gh pr create \
  --base main \
  --head 001-atrium-observatory-service \
  --title "feat(001): implement Observatory service" \
  --reviewer human-groundskeeper

# Document handoff
echo "Feature 001 ready for review. All tests passing." > \
  specs/001-atrium-observatory-service/collaboration/READY_FOR_REVIEW.md
```

**Agent B (Review)** - If applicable:
```bash
# Check out PR branch
gh pr checkout 123

# Run tests
cd services/observatory
.\quick-start.ps1 test -Verbose

# Review code
# ...

# Approve or request changes
gh pr review 123 --approve --body "LGTM. All tests pass, code quality excellent."

# Or request changes
gh pr review 123 --request-changes --body "Need error handling in webhook module."
```

**Human Groundskeeper (Final Merge)**:
- Reviews agent feedback
- Verifies constitutional compliance
- Merges if approved

## Branch Protection & PR Requirements

### Current Settings
- **main**: No protection yet (direct pushes allowed)
- **Feature branches**: No protection

### Recommended Settings (Future)
Enable on main branch:
- ✅ Require PR before merging
- ✅ Require status checks (CI must pass)
- ✅ Require 1 approval (human groundskeeper)
- ❌ Require approvals from code owners (too restrictive for now)
- ✅ Dismiss stale reviews on new commits

## GitHub CLI Commands Reference

### Install gh CLI
```bash
# Windows (if not installed)
winget install GitHub.cli

# Verify
gh --version
```

### Authenticate
```bash
gh auth login
```

### Create PR
```bash
# Interactive
gh pr create

# With all options
gh pr create \
  --base main \
  --head feature-branch \
  --title "feat: add new feature" \
  --body "Description" \
  --label "enhancement" \
  --assignee username \
  --reviewer username
```

### List PRs
```bash
gh pr list
gh pr list --state all
gh pr list --author @me
```

### View PR
```bash
gh pr view 123
gh pr view 123 --web  # Open in browser
```

### Check Out PR
```bash
gh pr checkout 123
```

### Review PR
```bash
gh pr review 123 --approve
gh pr review 123 --request-changes --body "Comments"
gh pr review 123 --comment --body "Question about line 42"
```

### Merge PR
```bash
gh pr merge 123 --squash
gh pr merge 123 --merge
gh pr merge 123 --rebase
```

### Close PR Without Merging
```bash
gh pr close 123 --comment "Superseded by PR #124"
```

## Agent Decision Tree

```
┌─────────────────────────────┐
│ Code changes complete?      │
└────────────┬────────────────┘
             │
             ├─ NO ──► Push to branch, continue working
             │
             └─ YES
                │
                ▼
┌─────────────────────────────┐
│ Tests passing?              │
└────────────┬────────────────┘
             │
             ├─ NO ──► Fix tests first
             │
             └─ YES
                │
                ▼
┌─────────────────────────────┐
│ Is this a feature           │
│ completion, breaking        │
│ change, or handoff?         │
└────────────┬────────────────┘
             │
             ├─ YES ──► Create PR ──► Document handoff ──► Notify
             │
             └─ NO
                │
                ▼
┌─────────────────────────────┐
│ Is main branch protected?   │
└────────────┬────────────────┘
             │
             ├─ YES ──► Create PR (required)
             │
             └─ NO ──► Merge directly OR create PR if you want review
```

## Common Scenarios

### Scenario 1: Feature 001 Implementation
```bash
# Week 1-3: Active development
git checkout 001-atrium-observatory-service
git commit -m "feat: add analyzer"
git push origin 001-atrium-observatory-service  # No PR

git commit -m "feat: add rate limiter"
git push origin 001-atrium-observatory-service  # No PR

git commit -m "test: add integration tests"
git push origin 001-atrium-observatory-service  # No PR

# Week 4: Feature complete
.\quick-start.ps1 test  # All pass
gh pr create --base main --head 001-atrium-observatory-service \
  --title "feat(001): Atrium Observatory Service - Complete" \
  --body-file specs/001-atrium-observatory-service/COMPLETION.md
```

### Scenario 2: Quick Bugfix on Main
```bash
# Bug discovered in production
git checkout main
git pull origin main

# Fix bug
git checkout -b hotfix-rate-limit-bug
git commit -m "fix: rate limiter off-by-one error"
git push origin hotfix-rate-limit-bug

# Create PR for quick review
gh pr create --base main --head hotfix-rate-limit-bug \
  --title "fix: critical rate limiter bug" \
  --label "bug,priority-high"

# Human reviews and merges ASAP
```

### Scenario 3: Multi-Phase Feature
```bash
# Phase 1: Foundation (Agent A)
git checkout 001-phase-1-foundation
# ... work ...
gh pr create --base main --head 001-phase-1-foundation \
  --title "feat(001): Phase 1 - Core Service"
# Merge after review

# Phase 2: Authentication (Agent B)
git checkout 001-phase-2-auth
git merge main  # Get Phase 1 changes
# ... work ...
gh pr create --base main --head 001-phase-2-auth \
  --title "feat(001): Phase 2 - Authentication"
# Merge after review

# Phase 3: Polish (Agent C)
# ... similar pattern
```

## Troubleshooting

### PR Creation Fails: "No commits between base and head"
**Cause**: Feature branch is already merged or has no new commits.
**Solution**: Make new commits or check if branch is stale.

### PR Shows Unexpected Commits
**Cause**: Feature branch is not based on latest main.
**Solution**: 
```bash
git checkout feature-branch
git merge main  # Or: git rebase main
git push origin feature-branch --force-with-lease
```

### CI Fails on PR
**Cause**: Tests passing locally but failing in CI.
**Solution**: Check CI logs, fix issues, push new commit.

### Can't Find PR Number
**Solution**:
```bash
gh pr list
# Or check GitHub web UI
```

## Best Practices for AI Agents

1. **Always run tests before creating PR** - CI should never be the first test run
2. **Write descriptive PR titles** - Other agents need to understand at a glance
3. **Include test results in PR body** - Copy from `.\quick-start.ps1 test` output
4. **Reference feature spec** - Link to `specs/<feature>/spec.md`
5. **Use labels generously** - Help humans prioritize reviews
6. **Document in collaboration directory** - PR creation is a handoff event
7. **Assign reviewers explicitly** - Don't assume who will review
8. **Keep PRs focused** - One feature/fix per PR
9. **Update PR body as changes are made** - Keep it accurate
10. **Close PRs that are superseded** - Don't leave abandoned PRs open

## Anti-Patterns to Avoid

❌ **Creating PR for every commit** - Too much review overhead  
✅ Create PR at logical checkpoints (feature done, breaking change, etc.)

❌ **Merge to main without PR for breaking changes** - Breaks other work  
✅ Always PR for breaking changes, even if fast-tracked

❌ **Creating PR with failing tests** - Wastes reviewer time  
✅ Only create PR when all checks pass locally

❌ **Empty or template PR descriptions** - Reviewer has no context  
✅ Write thorough descriptions with testing evidence

❌ **Leaving PRs open indefinitely** - Creates clutter  
✅ Close or merge within 48 hours, or document why it's stalled

## Integration with Existing Workflows

### Feature Specification Process
1. Human creates spec in `specs/<feature>/spec.md`
2. Human or agent creates implementation plan
3. **Agent implements on feature branch** (no PR until done)
4. **Agent creates PR when feature complete** ← PR happens here
5. Human reviews PR and merges

### Git Worktree Workflow
From `.specify/memory/git-worktrees-protocol.md`:
- Each worktree can have its own feature branch
- PRs created when worktree's feature is complete
- Worktrees can be deleted after PR merge

### Multi-Agent Collaboration
From `.github/copilot-instructions.md`:
- Use `specs/<feature>/collaboration/` for coordination
- Create PR at handoff points between agents
- Document PR number in collaboration files

## Metrics & Tracking

Useful for understanding PR workflow health:

```bash
# PRs by state
gh pr list --state open | wc -l
gh pr list --state closed | wc -l
gh pr list --state merged | wc -l

# Average PR age
gh pr list --json number,createdAt,updatedAt

# PRs by author
gh pr list --author @me
```

## Future Enhancements

Potential improvements to PR workflow:

- [ ] Auto-label PRs based on changed files
- [ ] Auto-assign reviewers based on code ownership
- [ ] PR templates for different change types
- [ ] Automated PR description generation from commits
- [ ] PR size warnings (too large → split)
- [ ] Stale PR bot (closes after 30 days)
- [ ] PR merge queue for main branch

---

## Quick Reference Card

**Create PR**: `gh pr create --base main --head feature-branch`  
**List PRs**: `gh pr list`  
**View PR**: `gh pr view 123`  
**Checkout PR**: `gh pr checkout 123`  
**Review PR**: `gh pr review 123 --approve`  
**Merge PR**: `gh pr merge 123 --squash`  

**When to PR**: Feature done, breaking change, agent handoff, constitution question  
**When NOT to PR**: WIP commits, docs-only, tests-only, minor deps  

**Always before PR**: Tests pass, code formatted, lint clean, collaboration docs updated  

---

**Last Review**: 2025-01-05  
**Next Review**: After 10 PRs merged (establish patterns)  
**Maintained By**: Human groundskeeper + AI agents
