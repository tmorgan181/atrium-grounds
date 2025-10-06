# Feature Proposal: Spec-Kit Enhancements

**Status**: 💭 Ideation (TODO)  
**Feature ID**: 003  
**Created**: 2025-01-04  
**Priority**: Medium

---

## Overview

Enhance the spec-kit tooling (`.github/prompts/`) and development experience to incorporate custom collaboration protocols and improve developer ergonomics based on learnings from Feature 002.

**This is a proposal only. No planning or implementation should occur at this time.**

---

## Problem Statement

Current gaps identified:

1. **Spec-kit prompts don't reference collaboration protocols** - The `/specify`, `/plan`, `/tasks` prompts don't guide agents to set up collaboration structures or explain multi-agent workflows

2. **Developer experience improvements needed** - Feature 002 revealed several UX patterns that could be standardized:
   - Parameter validation patterns
   - Help text organization
   - Clean/minimal output modes
   - Consistent error handling
   - Progress indicators

3. **Collaboration setup is manual** - Each feature requires manually creating collaboration directory structure and documentation

4. **Missing coordination guidance** - Agents need better prompts for when/how to create handoffs, session logs, and coordination documents

---

## Proposed Scope (High-Level Ideas)

### 1. Update Spec-Kit Prompts

**Goal**: Integrate collaboration protocols into specification workflow

Potential updates to `.github/prompts/`:
- **specify.prompt.md**: Add section for multi-agent considerations
- **plan.prompt.md**: Include collaboration directory setup in planning
- **tasks.prompt.md**: Reference delegation and handoff patterns
- **implement.prompt.md**: Guide session logging and coordination
- New prompt: **collaborate.prompt.md** for coordination workflows

### 2. Collaboration Directory Scaffolding

**Goal**: Automate collaboration structure creation

Could include:
- Script or prompt to generate collaboration subdirectories
- Template files for handoffs, proposals, decisions
- Automatic README generation
- Integration with `/specify` workflow

### 3. Developer Experience Standardization

**Goal**: Extract and generalize Feature 002 patterns

Patterns to consider standardizing:
- **Parameter validation framework** (reusable validation patterns)
- **Output modes** (minimal, detail, clean/ANSI-free)
- **Help text templates** (consistent formatting)
- **Progress indicators** (spinners, status lines)
- **Error message formatting** (actionable, scannable)
- **Prerequisites checking** (common validation patterns)

Could manifest as:
- PowerShell module with common functions
- Python utilities library
- Style guide for CLI tools
- Template scripts
- Best practices documentation

### 4. Multi-Agent Coordination Enhancements

**Goal**: Better support for parallel agent workflows

Possible improvements:
- Handoff templates with checklists
- Status dashboard (markdown-based)
- Task assignment tracking
- Conflict detection (who's working on what)
- Session log standardization
- Validation report templates

---

## Success Criteria (If Implemented)

This feature would be successful if:

- [ ] New features automatically get collaboration structure
- [ ] Agents follow consistent coordination patterns
- [ ] Developer experience patterns are reusable across services
- [ ] Spec-kit prompts guide multi-agent workflows
- [ ] Less manual setup required for new features
- [ ] Coordination overhead is reduced

---

## Open Questions

- Should collaboration setup be part of `/specify` or a separate `/collaborate` command?
- How much to standardize vs. letting patterns emerge organically?
- PowerShell-specific vs. language-agnostic tooling?
- Should this be one feature or split into multiple?
- Priority relative to other work (Observatory features, new services)?

---

## Related Work

- **Feature 002**: Developer Experience Upgrades (in progress) - Source of DX patterns
- **Spec-kit prompts**: `.github/prompts/*.prompt.md` - Current specification workflow
- **Constitution**: `.specify/memory/constitution.md` - Multi-agent collaboration principles
- **Orientation protocol**: `.github/prompts/orient.prompt.md` - Agent coordination basics

---

## Non-Goals (Explicit Exclusions)

This feature should **NOT**:
- Replace existing spec-kit workflows (enhance, don't replace)
- Add complex tooling dependencies (keep it simple)
- Enforce rigid processes (enable, don't constrain)
- Create coordination overhead (reduce friction, don't add it)
- Implement without user validation (this is exploratory)

---

## Next Steps (When Ready)

When/if this moves forward:

1. **Validate need** - Confirm pain points with user
2. **Scope refinement** - Break into smaller features if needed
3. **Run /specify** - Create formal spec with examples
4. **Run /plan** - Architecture and implementation approach
5. **Run /tasks** - Detailed task breakdown
6. **Implement incrementally** - Start with highest-value items

---

## Notes

- This emerged from Feature 002 retrospective
- Keep it lightweight - don't over-engineer
- Focus on reducing friction for multi-agent work
- User preferences matter (ask before implementing)
- Some items may belong in different features

---

## Addendum: GitHub Branch Protection & PR Workflow

**Added**: 2025-01-05

### Current Repository State

The main branch has a ruleset (`main-branch-protection`) with:
- ✅ PR required for all changes
- ✅ No force pushes
- ✅ No branch deletion
- ⚠️ **Bypass enabled for repository admins** (including AI agents)

### Observed Behavior

When pushing to main, GitHub shows:
```
remote: Bypassed rule violations for refs/heads/main:
remote: - Changes must be made through a pull request.
```

**Why**: AI agents with admin access can bypass the PR requirement automatically.

### Self-Enforcement Required

Since admins can bypass the ruleset, **we must self-enforce PR discipline** according to `.specify/memory/pr-workflow-guide.md`:

**Create PRs for:**
- ✅ Feature completion (all acceptance criteria met)
- ✅ Breaking changes (API, schema, config changes)
- ✅ Multi-agent handoffs
- ✅ Constitution compliance questions

**Direct push allowed for:**
- ✅ Documentation-only changes (non-architectural)
- ✅ Test additions (no code changes)
- ✅ Minor dependency updates
- ✅ Infrastructure fixes (CI, tooling)
- ✅ Work-in-progress on feature branches

### Integration with Feature 003

If Feature 003 is implemented, consider:
- Adding PR workflow reminders to spec-kit prompts
- Creating decision tree helper for "Should I create a PR?"
- Automating PR creation at feature completion checkpoints
- Adding PR checklist generation to collaboration scaffolding

**Reference**: `.specify/memory/pr-workflow-guide.md` for complete decision tree and examples.

---

**Status**: 💭 **Ideation Phase - Do Not Implement**

This is a feature proposal capturing ideas and possibilities. No specification, planning, or implementation work should occur without explicit user direction.

**Captured**: 2025-01-04 by Copilot CLI after Feature 002 collaboration experience  
**Updated**: 2025-01-05 with PR workflow clarification  
**Updated**: 2025-01-05 with OOB setup audit

---

## Addendum: OOB vs Custom Setup Analysis (2025-01-05)

**Important Clarification**: This audit distinguishes between:
- **OOB Spec-Kit**: What comes with the base spec-kit framework
- **Custom Additions**: What we've added for multi-agent/git workflows

**Audit Scope**: Assess what we've customized, what gaps those fill, and how to make them replicable as a modular add-on.

### Breakdown: OOB vs Custom

#### OOB Spec-Kit (Base Framework)
```
.github/prompts/
├── analyze.prompt.md         # ✅ OOB
├── clarify.prompt.md         # ✅ OOB
├── constitution.prompt.md    # ✅ OOB
├── implement.prompt.md       # ✅ OOB
├── plan.prompt.md            # ✅ OOB
├── specify.prompt.md         # ✅ OOB
└── tasks.prompt.md           # ✅ OOB

.specify/
├── scripts/                  # ✅ OOB (automation)
└── templates/                # ✅ OOB (spec/plan/tasks)
    ├── spec-template.md
    ├── plan-template.md
    └── tasks-template.md
```

#### Custom Additions (Our Enhancements)
```
.github/prompts/
└── orient.prompt.md          # 🔧 CUSTOM - Multi-agent coordination

.specify/memory/              # 🔧 CUSTOM - Entire directory
├── agent-meta-commands.md    # 🔧 CUSTOM - Slash command reference
├── collaboration-addon-guide.md  # 🔧 CUSTOM - Multi-agent protocols
├── constitution.md           # ✅ OOB but customized
├── git-worktrees-protocol.md # 🔧 CUSTOM - Parallel development
├── key-web-dev-principles.md # 🔧 CUSTOM - Web dev reference
├── orientation-reference.md  # 🔧 CUSTOM - Agent onboarding
└── pr-workflow-guide.md      # 🔧 CUSTOM - PR decision tree

.github/workflows/            # 🔧 CUSTOM - Entire directory
├── ci.yml                    # 🔧 CUSTOM - Project CI
├── claude-code-review.yml    # 🔧 CUSTOM - Disabled
└── claude.yml                # 🔧 CUSTOM - Disabled

specs/[feature]/collaboration/  # 🔧 CUSTOM - Entire structure
├── README.md
├── sessions/
├── proposals/
├── results/
├── reviews/
└── planning/
```

**Key Insight**: The OOB spec-kit provides single-agent specification workflow. We've added an entire multi-agent collaboration layer on top.

#### ✅ Strengths
1. **Complete spec-kit prompt set** - All core workflow prompts present (`/specify`, `/plan`, `/tasks`, `/implement`)
2. **Constitution integration** - Dedicated `/constitution` prompt for compliance checking
3. **Clarification workflow** - `/clarify` prompt for ambiguity resolution
4. **Analysis capability** - `/analyze` prompt for technical analysis
5. **Orientation protocol** - `/orient` prompt for agent coordination basics

#### ❌ Gaps Identified (Aligns with Proposal)
1. **No collaboration references in prompts** - Prompts don't mention:
   - Multi-agent coordination
   - Session logging requirements
   - Handoff document creation
   - Collaboration directory structure
   - Delegation patterns
   
2. **Missing `/collaborate` command** - No dedicated prompt for collaboration setup/coordination

3. **No PR workflow integration** - Prompts don't guide:
   - When to create PRs
   - PR creation process
   - Review workflow
   
4. **No collaboration scaffolding** - `create-new-feature.ps1` doesn't auto-create collaboration structure

5. **Workflow file issues**:
   - CI workflow needs `--system` flag fix (active bug)
   - Two workflows disabled (unused)

#### 📊 Prompt Analysis

**`specify.prompt.md`**:
- ✅ Calls `create-new-feature.ps1` (good)
- ❌ No mention of collaboration setup
- ❌ Doesn't prompt for multi-agent considerations
- **Gap**: Should mention collaboration directory creation for multi-agent features

**`plan.prompt.md`**:
- ✅ Calls `setup-plan.ps1` for structure
- ✅ References constitution
- ❌ No collaboration directory initialization
- ❌ No guidance on multi-agent task delegation
- **Gap**: Should prompt agent to assess if multi-agent work is needed and set up accordingly

**`implement.prompt.md`**:
- ✅ Respects task dependencies
- ✅ Tracks progress
- ❌ No session logging requirement
- ❌ No handoff document creation
- ❌ No mention of coordination files
- **Gap**: Critical - agents don't know to create session logs or handoffs during implementation

**`tasks.prompt.md`**:
- ❌ Doesn't exist as separate workflow (tasks generated during `/plan`)
- **Gap**: Could be enhanced with delegation patterns

### Current State: `.specify/` Directory

**Structure**:
```
.specify/
├── memory/                           # Persistent agent knowledge
│   ├── agent-meta-commands.md        # Slash command reference
│   ├── collaboration-addon-guide.md  # ⭐ Multi-agent protocols
│   ├── constitution.md               # Project principles
│   ├── git-worktrees-protocol.md     # Parallel development
│   ├── key-web-dev-principles.md     # Web dev reference
│   ├── orientation-reference.md      # Agent onboarding
│   └── pr-workflow-guide.md          # ⭐ PR decision tree (NEW)
├── scripts/powershell/               # Automation scripts
│   ├── check-prerequisites.ps1
│   ├── common.ps1
│   ├── create-new-feature.ps1        # Feature scaffolding
│   ├── setup-plan.ps1
│   └── update-agent-context.ps1
└── templates/                        # Document templates
    ├── agent-file-template.md
    ├── plan-template.md
    ├── spec-template.md
    └── tasks-template.md
```

**Findings**:

#### ✅ Strengths
1. **Comprehensive memory directory** - 7 reference docs including:
   - ⭐ `collaboration-addon-guide.md` - Detailed multi-agent protocols
   - ⭐ `pr-workflow-guide.md` - NEW: Complete PR workflow (added today)
   - `constitution.md` - Project principles
   - `git-worktrees-protocol.md` - Parallel development strategy
   
2. **Automation scripts** - PowerShell scripts for feature scaffolding and setup

3. **Template system** - Structured templates for specs, plans, tasks

4. **Well-documented protocols** - Collaboration guide is thorough with:
   - Directory structure requirements
   - Session logging format
   - Handoff document patterns
   - Review protocols

#### ❌ Gaps Identified (Aligns with Proposal)

1. **Disconnected from prompts** - Memory docs exist but prompts don't reference them:
   - `/implement` doesn't mention `collaboration-addon-guide.md`
   - `/plan` doesn't reference multi-agent patterns
   - `/specify` doesn't check if multi-agent setup needed
   
2. **Manual collaboration setup** - `create-new-feature.ps1` creates:
   - ✅ Feature directory
   - ✅ Branch
   - ✅ spec.md
   - ❌ No `collaboration/` directory
   - ❌ No collaboration README
   - ❌ No session logs directory
   
3. **No collaboration template** - Templates exist for specs/plans/tasks but not for:
   - Session log format
   - Handoff document structure
   - Review document format
   - Proposal document format
   
4. **Missing scaffolding script** - No `setup-collaboration.ps1` to auto-create:
   ```
   collaboration/
   ├── README.md
   ├── sessions/
   ├── proposals/
   ├── results/
   ├── reviews/
   └── planning/
   ```

5. **No validation helper** - No script to check if collaboration structure exists/complete

### Gap Analysis: Proposal vs Reality

| Proposed Enhancement | Current State | Gap Severity |
|---------------------|---------------|--------------|
| Update spec-kit prompts with collaboration refs | Prompts have no collaboration mentions | 🔴 HIGH |
| Create `/collaborate` command | Doesn't exist | 🟡 MEDIUM |
| Automate collaboration scaffolding | Manual setup required | 🔴 HIGH |
| Session logging templates | Documented format but no template | 🟡 MEDIUM |
| Handoff document templates | Documented format but no template | 🟡 MEDIUM |
| PR workflow integration | Guide exists but not in prompts | 🟡 MEDIUM |
| DX pattern standardization | Ad-hoc per feature | 🟢 LOW |
| Multi-agent coordination helpers | Protocols exist, not automated | 🟡 MEDIUM |

### Key Insights

#### What's Working Well
1. **Foundation is strong** - `collaboration-addon-guide.md` and `pr-workflow-guide.md` provide excellent protocols
2. **Feature scaffolding exists** - `create-new-feature.ps1` handles basic setup
3. **Memory system is rich** - 7 reference docs cover most scenarios
4. **Template system works** - Specs, plans, tasks have good templates

#### Critical Disconnects
1. **Prompts ↔ Memory** - Prompts don't reference memory docs (biggest issue)
2. **Automation ↔ Protocols** - Protocols documented but not automated
3. **Templates ↔ Collaboration** - Templates for specs but not collaboration artifacts
4. **Scripts ↔ Multi-Agent** - Scripts assume single-agent workflow

### Recommended Priority Fixes

If Feature 003 moves forward, prioritize:

#### P0 - Critical (Do First)
1. **Update `/implement` prompt** to require session logging
   - Reference `collaboration-addon-guide.md`
   - Mandate session logs after 3+ tasks or milestones
   - Check for collaboration/ directory
   
2. **Fix `create-new-feature.ps1`** to create collaboration structure
   - Add `-MultiAgent` flag (default: false)
   - Auto-create collaboration/ subdirectories
   - Copy collaboration README template
   
3. **Create collaboration templates** in `.specify/templates/`:
   - `session-log-template.md`
   - `handoff-template.md`
   - `review-template.md`
   - `collaboration-readme-template.md`

#### P1 - High (Do Next)
4. **Update `/specify` prompt** to detect multi-agent features
   - Ask: "Is this a multi-agent feature?"
   - If yes: Call `setup-collaboration.ps1` script
   - Link to `collaboration-addon-guide.md`
   
5. **Create `/collaborate` command** for mid-feature coordination
   - Check collaboration structure
   - Generate handoff from current work
   - Validate session logs
   - Create proposals/reviews
   
6. **Update `/plan` prompt** to include collaboration planning
   - Reference multi-agent delegation patterns
   - Prompt for handoff checkpoints
   - Link to `pr-workflow-guide.md` for PR strategy

#### P2 - Medium (Enhancement)
7. **Create `setup-collaboration.ps1` script**
   - Auto-create directory structure
   - Copy templates
   - Initialize README with feature context
   
8. **Add PR workflow to prompts**
   - `/implement`: Check if PR needed at checkpoints
   - `/plan`: Include PR creation in phase planning
   - Reference `.specify/memory/pr-workflow-guide.md`
   
9. **Create validation helpers**
   - `validate-collaboration-setup.ps1`
   - `check-session-logs.ps1`
   - `verify-handoffs.ps1`

#### P3 - Low (Nice to Have)
10. **DX pattern library** (separate feature?)
11. **Status dashboard generator**
12. **Automated handoff generator**

### Implementation Strategy

If proceeding with Feature 003:

**Phase 1: Connect Existing Assets** (Quick wins, no new code)
- Update prompts to reference memory docs
- Add collaboration checks to existing scripts
- Document current gaps

**Phase 2: Template & Automation** (Core functionality)
- Create collaboration templates
- Add collaboration scaffolding to scripts
- Create `/collaborate` command

**Phase 3: Integration** (Polish)
- PR workflow integration
- Validation helpers
- Status tracking

**Phase 4: Advanced** (Future)
- DX pattern standardization
- Advanced coordination tools
- Metrics and dashboards

### Files That Would Change

**Must Edit** (P0-P1):
- `.github/prompts/implement.prompt.md` ← Add session logging requirement
- `.github/prompts/specify.prompt.md` ← Add multi-agent detection
- `.github/prompts/plan.prompt.md` ← Add collaboration planning
- `.specify/scripts/powershell/create-new-feature.ps1` ← Add collab scaffolding
- `.github/copilot-instructions.md` ← Reference collaboration addon

**Must Create** (P0-P1):
- `.specify/templates/session-log-template.md`
- `.specify/templates/handoff-template.md`
- `.specify/templates/collaboration-readme-template.md`
- `.github/prompts/collaborate.prompt.md`
- `.specify/scripts/powershell/setup-collaboration.ps1`

**Should Consider** (P2-P3):
- `.specify/scripts/powershell/validate-collaboration.ps1`
- DX pattern library location (new directory?)
- Status tracking mechanism

### Risks & Considerations

1. **Over-automation risk** - Too much scaffolding can be rigid
   - Mitigation: Make collaboration setup opt-in or detectable
   
2. **Prompt bloat** - Adding too much to prompts makes them hard to follow
   - Mitigation: Link to memory docs, don't duplicate content
   
3. **Single-agent workflows** - Not all features need multi-agent setup
   - Mitigation: Only scaffold collaboration when needed
   
4. **Template maintenance** - More templates = more to keep updated
   - Mitigation: Keep templates minimal and flexible

### What Our Custom Additions Solve

| Gap in OOB Spec-Kit | Our Custom Solution | Status |
|---------------------|---------------------|--------|
| No multi-agent coordination | `collaboration-addon-guide.md` | ✅ Documented |
| No git workflow guidance | `git-worktrees-protocol.md` | ✅ Documented |
| No PR decision tree | `pr-workflow-guide.md` | ✅ Documented |
| No agent orientation | `orient.prompt.md` + `orientation-reference.md` | ✅ Documented |
| No collaboration structure | `specs/[feature]/collaboration/` pattern | ⚠️ Manual per feature |
| No session logging | Documented in collaboration guide | ⚠️ Manual enforcement |
| No handoff templates | Documented format only | ❌ Not templated |
| No CI integration | `workflows/ci.yml` | ✅ Present (needs fix) |
| Prompts don't reference customs | N/A | ❌ Disconnected |

### The Real Insight: This Should Be Its Own Project

**What We've Actually Built**: A **multi-agent, git-integrated add-on** to spec-kit

**Current Problem**: Our enhancements are:
- ✅ Well-documented
- ✅ Proven in Feature 001 & 002
- ❌ Not modular/reusable
- ❌ Not integrated with OOB prompts
- ❌ Not automatable for new projects

**Proposed Solution**: Create **"spec-kit-multiagent"** - a minimal, modular extension

### New Project Proposal: `spec-kit-multiagent`

**Purpose**: Git-aware, multi-agent collaboration add-on for spec-kit

**What It Would Provide**:
1. **Drop-in memory docs** (installable to any spec-kit repo)
2. **Enhanced prompts** (modified OOB prompts with multi-agent awareness)
3. **Collaboration scaffolding** (automated directory creation)
4. **Templates** (session logs, handoffs, reviews)
5. **Git workflow integration** (worktrees, PRs, branch strategies)
6. **Installation script** (one command to add to existing spec-kit project)

**Repository Structure**:
```
spec-kit-multiagent/
├── README.md                         # Installation & usage guide
├── install.ps1                       # One-command installation
├── memory/                           # Drop-in memory docs
│   ├── collaboration-addon-guide.md
│   ├── git-worktrees-protocol.md
│   ├── pr-workflow-guide.md
│   ├── orientation-reference.md
│   └── agent-meta-commands.md
├── prompts/                          # Enhanced spec-kit prompts
│   ├── orient.prompt.md              # NEW: Agent coordination
│   ├── collaborate.prompt.md         # NEW: Mid-feature coordination
│   ├── specify.prompt.md             # ENHANCED: Multi-agent detection
│   ├── plan.prompt.md                # ENHANCED: Collaboration planning
│   └── implement.prompt.md           # ENHANCED: Session logging
├── templates/                        # Collaboration templates
│   ├── collaboration-readme.md
│   ├── session-log.md
│   ├── handoff.md
│   └── review.md
├── scripts/                          # Automation helpers
│   ├── setup-collaboration.ps1       # Create collaboration structure
│   ├── validate-collaboration.ps1    # Check completeness
│   └── enhance-prompts.ps1           # Add multi-agent to OOB prompts
└── docs/
    ├── installation.md               # How to install
    ├── customization.md              # How to adapt
    └── examples.md                   # Real-world usage
```

**Installation Flow**:
```powershell
# In any spec-kit repository
.\install-multiagent.ps1

# This would:
# 1. Copy memory docs to .specify/memory/
# 2. Add enhanced prompts to .github/prompts/
# 3. Add collaboration templates to .specify/templates/
# 4. Add automation scripts to .specify/scripts/
# 5. Update .github/copilot-instructions.md with multi-agent section
# 6. Create .github/workflows/ci-template.yml (optional)
```

**Key Features**:
- ✅ **Non-invasive**: Doesn't replace OOB spec-kit, enhances it
- ✅ **Modular**: Can pick which enhancements to install
- ✅ **Documented**: Each enhancement explains what it adds
- ✅ **Tested**: Proven on atrium-grounds Features 001 & 002
- ✅ **Minimal**: Small, focused additions

**What Makes It Replicable**:
1. **Install script** handles integration with existing spec-kit
2. **Templates** are copy-paste ready
3. **Documentation** explains each addition's purpose
4. **Examples** show real usage from atrium-grounds
5. **Customization guide** helps adapt to other projects

### Revised Recommendation

**Don't implement as Feature 003** - Instead:

1. **Extract atrium-grounds customs** into standalone project
2. **Package as `spec-kit-multiagent`**
3. **Make installation automated** 
4. **Document what each piece adds**
5. **Test installation on fresh spec-kit repo**
6. **Publish as reusable module**

**Then** apply back to atrium-grounds via the install script.

**Benefits**:
- ✅ Helps other spec-kit users with multi-agent needs
- ✅ Forces us to modularize properly
- ✅ Makes our enhancements portable
- ✅ Easier to maintain (one source of truth)
- ✅ Can be versioned independently

**Scope Boundary**:
```
spec-kit                 (base framework)
└── spec-kit-multiagent  (our addition)
    ├── Multi-agent coordination
    ├── Git workflow integration  
    ├── Collaboration scaffolding
    └── Enhanced prompts
```

### Files to Extract from atrium-grounds

**Source → Destination**:
```
atrium-grounds/.specify/memory/
├── collaboration-addon-guide.md    → spec-kit-multiagent/memory/
├── git-worktrees-protocol.md       → spec-kit-multiagent/memory/
├── pr-workflow-guide.md            → spec-kit-multiagent/memory/
├── orientation-reference.md        → spec-kit-multiagent/memory/
└── agent-meta-commands.md          → spec-kit-multiagent/memory/

atrium-grounds/.github/prompts/
└── orient.prompt.md                → spec-kit-multiagent/prompts/

New files to create:
├── spec-kit-multiagent/prompts/collaborate.prompt.md  # NEW
├── spec-kit-multiagent/templates/session-log.md       # NEW
├── spec-kit-multiagent/templates/handoff.md           # NEW
├── spec-kit-multiagent/scripts/setup-collaboration.ps1 # NEW
└── spec-kit-multiagent/install.ps1                    # NEW
```

### Next Steps (If Approved)

1. **Create new repo**: `spec-kit-multiagent`
2. **Extract & refine**: Pull customs from atrium-grounds, generalize
3. **Create installer**: One-command setup script
4. **Document**: Clear README explaining each enhancement
5. **Test**: Install on fresh spec-kit repo, validate workflow
6. **Publish**: Make available for other projects
7. **Apply back**: Use installer on atrium-grounds for dogfooding

### Conclusion

**Revised Assessment**: 
- OOB spec-kit: ✅ Works as designed (single-agent)
- Our customs: ✅ Proven multi-agent additions
- Integration: ❌ Not packaged for reuse
- Automation: ❌ Not installable elsewhere

**New Proposal**: Build `spec-kit-multiagent` as standalone project that:
- Extends spec-kit without replacing it
- Automates our proven multi-agent patterns
- Makes git workflow integration easy
- Can be installed in any spec-kit repository
- Benefits broader spec-kit community

**Feature 003 Pivot**: From "enhance this repo" to "build reusable extension"

---

**Audit Conducted By**: Copilot CLI  
**Date**: 2025-01-05  
**Method**: File structure analysis, prompt content review, gap identification  
**Files Reviewed**: 27 files across `.github/` and `.specify/`

---

**Status**: 💭 **Ideation Phase - Do Not Implement**

This is a feature proposal capturing ideas and possibilities. No specification, planning, or implementation work should occur without explicit user direction.

**Captured**: 2025-01-04 by Copilot CLI after Feature 002 collaboration experience  
**Updated**: 2025-01-05 with PR workflow clarification  
**Audited**: 2025-01-05 - OOB setup reviewed, gaps confirmed, priorities established
