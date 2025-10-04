# Project Development Guidelines Template

**Project**: [PROJECT_NAME]
**Last Updated**: [DATE]

## Technology Stack

### Core Technologies
- **[Technology 1]**: [Version/Details]
- **[Technology 2]**: [Version/Details]
- **[Technology 3]**: [Version/Details]

### Dependencies/Extensions
List key dependencies, plugins, or frameworks used in the project.

### Required Features/APIs
List browser features, system capabilities, or external APIs the project depends on.

## Project Structure

```
project-root/
├── [source-directory]/       # Main source code
│   ├── [config-file]         # Configuration
│   ├── [module-1]/           # Feature/module 1
│   ├── [module-2]/           # Feature/module 2
│   └── [module-n]/           # Feature/module N
├── specs/                    # Feature specifications
│   └── [feature-name]/       # Individual feature docs
│       ├── spec.md           # Feature specification
│       ├── plan.md           # Implementation plan
│       ├── tasks.md          # Task breakdown
│       └── collaboration/    # Multi-agent coordination
└── .github/
    ├── copilot-instructions.md # This file
    └── prompts/              # Spec-kit slash commands
```

**Adaptation Note**: Replace bracketed placeholders with your actual project structure.

## Development Commands

### Setup
```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies for a service
cd services/<service-name>
uv sync --dev
```

### Local Development
```bash
# Run a service
uv run python main.py

# Run FastAPI service with auto-reload
uv run fastapi dev main.py

# Run with environment variables
uv run --env-file .env python main.py
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Lint with ruff
uv run ruff check .

# Type check with mypy
uv run mypy .
```

**Note**: Each service manages dependencies via `pyproject.toml` and uses `uv` for environment management.

## Code Style Guidelines

### [Language/Framework 1]
- Style guideline 1
- Style guideline 2
- Organization pattern
- Naming conventions

### [Language/Framework 2]
- Style guideline 1
- Style guideline 2
- Organization pattern
- Naming conventions

### General Principles
- Accessibility standards (if applicable)
- Performance considerations
- Security best practices
- Documentation requirements

**Adaptation Note**: Add language/framework-specific style guides relevant to your project.

## Design System (if applicable)

### Architecture
Describe how your design system is organized (themes, tokens, components, etc.)

### Key Patterns
Document reusable patterns, naming conventions, or organizational structures.

**Adaptation Note**: Remove this section if not applicable, or adapt to your project's design needs.

## Accessibility Requirements (if applicable)

### Minimum Standards
- Compliance level (WCAG AA/AAA, etc.)
- Platform-specific accessibility features
- Required support (keyboard nav, screen readers, etc.)

### Testing Checklist
- [ ] Accessibility requirement 1
- [ ] Accessibility requirement 2
- [ ] Accessibility requirement 3

**Adaptation Note**: Adjust or remove based on your project's accessibility needs.

## Multi-Agent Collaboration

When working with other AI agents or human collaborators:

### Coordination Protocol
**Location**: Use project-specific collaboration directories:
- `.collaboration/` for project-wide coordination
- `specs/[feature]/collaboration/` for feature-specific work

**Contents**:
- Task delegation documents
- Status updates and progress reports
- Completion confirmations
- Testing results and validation
- Inter-agent communication logs

### Shared File Etiquette
When multiple agents edit the same files:

**Before Editing**:
- Pull latest changes from shared branch
- Review recent commits to understand others' work
- Check collaboration docs for territory assignments

**During Work**:
- Commit frequently with descriptive messages
- Use targeted commits for specific sections
- Respect assigned file territories
- Document significant decisions

**After Editing**:
- Pull before push to detect conflicts early
- Test changes locally before pushing
- Update collaboration docs with status
- Notify other agents of major changes

### Git Workflow
**Reference**: See `.specify/memory/git-worktrees-protocol.md` for parallel development strategies using Git worktrees.

**Key Principles**:
- Feature branches for all work
- Clear commit messages with task identifiers
- Regular synchronization between agents
- Documented work division and territories

### Communication Channels
- **Collaboration Documents**: Primary written communication
- **Commit Messages**: Technical change descriptions
- **Project Issues**: For questions, blockers, or decisions
- **[Other channels]**: Add project-specific communication methods

## Project-Specific Conventions

### [Convention Category 1]
Document conventions specific to this project (e.g., file naming, directory structure, etc.)

### [Convention Category 2]
Document additional project-specific patterns or requirements.

### [Convention Category N]
Continue documenting as needed.

**Adaptation Note**: This section should capture project-specific patterns that don't fit other sections.

## Recent Feature Implementations

Track completed features for context:

- **[feature-id]**: Brief description
- **[feature-id]**: Brief description
- **[feature-id]**: Brief description

**Purpose**: Helps agents understand project evolution and existing patterns.

## Agent-Specific Notes

### For AI Assistants
- Preferred coding patterns for this project
- Common pitfalls to avoid
- Project-specific terminology or abbreviations
- References to key documentation

### For Human Developers
- Onboarding resources
- Key contacts or maintainers
- Project roadmap or priorities
- Development environment tips

**Adaptation Note**: Customize based on your team composition (all AI, all human, mixed).

## Manual Additions

<!-- MANUAL ADDITIONS START -->
<!-- 
Add runtime notes, preferences, or shortcuts here.
This section is preserved across automated updates.

Examples:
- Quick commands you use frequently
- Reminders about edge cases
- Links to external resources
- Temporary notes during active development
-->

<!-- MANUAL ADDITIONS END -->

---

## How to Use This Template

### Initial Setup
1. Copy this file to your project's `.github/` directory
2. Replace all `[BRACKETED_PLACEHOLDERS]` with your actual values
3. Remove sections that don't apply to your project
4. Add project-specific sections as needed

### Maintenance
- Update when adding new technologies or dependencies
- Keep command examples current with your tooling
- Document new patterns as they emerge
- Revise based on team feedback

### For Multi-Agent Projects
- Ensure all agents have access to this file
- Reference it in onboarding documentation
- Keep coordination protocols consistent
- Update collaboration patterns as you learn

---

**This template provides structure. Your project provides the specifics.**
