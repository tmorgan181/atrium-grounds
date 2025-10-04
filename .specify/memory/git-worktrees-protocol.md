# Git Worktrees for Multi-Agent Development

## Overview

Git worktrees enable parallel development by allowing multiple agents (AI assistants, human developers, or combinations) to work on the same codebase simultaneously without conflicts. Each agent operates in an isolated working directory while sharing the same Git repository and branch.

**When to Use**: Complex features with clearly separable tasks that can be divided among agents.

**When Not to Use**: Simple features or when primary agent (Claude Code) can handle sequentially.

## Agent Hierarchy and Roles

### Agent 1: Claude Code (Primary/Leader)
**Shell**: Bash  
**Role**: Primary developer with seniority  
**Strengths**: Higher token limits, better context retention, long-term development  
**Responsibilities**: 
- Feature architecture and core implementation
- Complex logic and multi-file changes
- Code review and integration
- Final decision-making on technical approach
- Git operations (commits, branches) - capable but defer to Copilot for git management when available

**Use for**: Most development work, especially sustained feature implementation

### Agent 2: GitHub Copilot CLI (Secondary/Specialist)
**Shell**: PowerShell  
**Role**: Delegated specialist for specific tasks + git operations expert  
**Strengths**: Fast iteration, git project management, different perspective  
**Responsibilities**:
- Specific delegated subtasks from Agent 1
- Isolated component work
- **Git project management** (preferred for branch operations, complex git workflows)
- Cross-platform compatibility testing (PowerShell perspective)
- Complementary implementation patterns

**Use for**: Specific tasks where parallel work provides value, PowerShell-specific needs, **git operations**

### Git Operations Preference
- **Branch creation/management**: Copilot preferred (but Claude capable)
- **Commits**: Both agents commit their own work
- **Complex git workflows**: Copilot preferred (rebase, cherry-pick, etc.)
- **Simple commits/pushes**: Either agent handles their own work
- **Conflict resolution**: Copilot preferred for git-level conflicts, Claude for code-level conflicts

### Collaboration Pattern
- **Default**: Claude Code works solo on main branch
- **Git setup**: Copilot handles branch creation, worktree setup when needed
- **When parallel work needed**: Claude Code delegates specific bounded tasks to Copilot via worktrees
- **Decision authority**: Claude Code has final say on architectural decisions
- **Git authority**: Copilot has preference for git operations, but both are capable

## Setup Process

### 1. Create Feature Branch
```bash
# Preferred: Copilot creates branch (better git tooling)
# In main repository
cd /path/to/main-repo
git checkout main
git pull origin main
git checkout -b [feature-branch-name]
git push -u origin [feature-branch-name]

# Alternative: Claude Code can create branch if working solo
# (Same commands, just less preferred for complex git operations)
```

### 2. Create Worktrees (Only When Needed)
```bash
# Preferred: Copilot creates worktrees (git operations specialist)
# From main repo directory
cd /path/to/main-repo

# Create worktree for Copilot's delegated work
git worktree add ../repo-copilot [feature-branch-name]

# Alternative: Claude Code can create worktrees if Copilot unavailable
# (Same commands, just defer to Copilot when possible)
```

**Note**: Don't create worktrees by default. Use only when Claude Code identifies work that benefits from parallel execution.

**Result Structure** (when using worktrees):
```
/path/to/
├── main-repo/          # Claude Code's primary workspace
└── repo-copilot/       # Copilot's isolated worktree (when delegated work exists)
```

## Agent Workflow

### Claude Code Workflow (Primary)
```bash
# Work in main repo (default)
cd /path/to/main-repo

# Standard development
git add [files]
git commit -m "[Task]: [Description]"
git push origin [feature-branch-name]

# When delegating to Copilot:
# 1. Ask Copilot to create worktree (if not exists)
# 2. Document task in spec/[feature-branch-name]/collaboration/
# 3. Assign specific files/sections
# 4. Monitor progress and integrate results

# For complex git operations:
# - Prefer delegating to Copilot
# - But can handle if needed
```

### Copilot Workflow (When Delegated)
```bash
# Handle git setup when requested
# Create branches, worktrees, manage complex git operations

# Work in assigned worktree
cd /path/to/repo-copilot

# Complete assigned task
git add [assigned-files]
git commit -m "[Task]: [Description]"
git push origin [feature-branch-name]

# Notify Claude Code of completion
# Handle git-level issues (rebases, cherry-picks, etc.)
```

## Coordination Strategy

### Task Delegation (Claude Code → Copilot)
**When to delegate**:
- Isolated component that can be built independently
- Cross-platform testing needed (PowerShell compatibility)
- Parallel work provides genuine time savings
- Task has clear boundaries and acceptance criteria
- Git operations needed (branch management, complex workflows)

**How to delegate**:
1. Create `collaboration/proposals/task-[name].md` with:
   - Task description
   - Assigned files/sections
   - Acceptance criteria
   - Dependencies and constraints
2. Ask Copilot to create worktree (if not exists) - leverage git expertise
3. Notify Copilot of assigned work
4. Review and integrate when complete

### Real-time Synchronization
```bash
# Either agent: Pull other's work
git pull origin [feature-branch-name]
```

**Both agents are capable of git operations**, but prefer Copilot for:
- Branch creation and management
- Worktree setup
- Complex git workflows (rebase, cherry-pick, stash operations)
- Git-level conflict resolution

### Work Division Strategies

**Primary Strategy: Leader-Delegate** (Recommended)
- Claude Code: Core architecture, integration, complex logic
- Copilot: Specific delegated subtasks + git operations
- Clear delegation documents define territories

**Git Operations Distribution**:
- Copilot: Branch/worktree creation, complex git workflows (preferred)
- Both: Commit their own work, push their changes
- Claude Code: Can handle git if Copilot unavailable

**Alternative: File-Based Division** (When needed)
- Claude Code: Files A, B, C (primary functionality)
- Copilot: Files X, Y, Z (isolated components)
- Minimal overlap, explicit boundaries

**Avoid: Equal Partnership Division**
- Don't split work 50/50 by default
- Claude Code's context advantages make it the better primary developer
- Use Copilot strategically for delegation + git operations

## Testing in Parallel

### Cross-Platform Testing
```bash
# Claude Code (Bash)
cd /path/to/main-repo
[run tests in bash environment]

# Copilot (PowerShell)  
cd /path/to/repo-copilot
[run tests in PowerShell environment]
```

**Value**: Different shells catch platform-specific issues

## Merge Strategies

### Recommended: Leader Integration with Git Specialist Support
```bash
# Claude Code integrates work (code decisions)
cd /path/to/main-repo
git pull origin [feature-branch-name]

# If git conflicts arise, prefer Copilot to resolve git-level issues
# Claude Code resolves code-level conflicts

# Final testing (Claude Code)
# Final push (either agent)
git push origin [feature-branch-name]
```

**Code decisions**: Claude Code has final approval  
**Git operations**: Copilot preferred for complex git issues

## Cleanup Process

```bash
# Copilot handles git cleanup (preferred)
# Or Claude Code if Copilot unavailable

cd /path/to/main-repo
git worktree remove ../repo-copilot

# Merge feature branch to main (Claude Code approves, either executes)
git checkout main
git merge [feature-branch-name]
git branch -d [feature-branch-name]
```

## Best Practices

### For Claude Code (Agent 1)
- **Default to solo work** - only use worktrees when genuinely beneficial
- **Delegate clearly** - explicit tasks, boundaries, acceptance criteria
- **Review all work** - final authority on quality and integration
- **Make architectural decisions** - leverage your context retention
- **Coordinate efficiently** - brief documentation in `collaboration/proposals/`
- **Defer git operations to Copilot when available** - but capable of handling if needed
- **Commit your own work** - don't wait for Copilot for simple commits

### For Copilot (Agent 2)
- **Wait for delegation** - don't start work without clear assignment
- **Handle git operations** - preferred for branches, worktrees, complex git workflows
- **Stay in bounds** - work only on assigned files/sections
- **Communicate status** - update `collaboration/stats` docs with progress
- **Respect hierarchy** - Claude Code has code decision authority
- **Ask when unclear** - better to clarify than assume
- **Commit your own work** - handle your own git operations for assigned tasks

### Communication
- Use `collaboration/` for task assignments and status
- Brief, direct documentation (token efficiency)
- Claude Code initiates and coordinates code work
- Copilot manages git operations and completes assigned tasks
- Both commit their own work, capable of full git workflows

## Common Commands Reference

```bash
# Git setup (Copilot preferred, Claude capable)
git worktree add ../repo-copilot [branch]
git checkout -b [new-branch]
git rebase [branch]
git cherry-pick [commit]

# Development (Both agents)
git add [files]
git commit -m "[message]"
git push origin [branch]
git pull origin [branch]

# Cleanup (Copilot preferred, Claude capable)
git worktree remove [path]
git branch -d [branch]
git worktree prune
```

---

**Summary**: Claude Code leads development with seniority. Copilot handles delegated tasks and is preferred for git operations. Both are capable of full git workflows, but defer to Copilot for complex git management when available.
