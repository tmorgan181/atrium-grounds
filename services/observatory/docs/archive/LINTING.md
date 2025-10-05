# Code Quality & Linting Guide

**Tools**: Ruff (linting + formatting), MyPy (type checking)  
**Status**: 📋 Planned quick-start.ps1 integration

---

## Quick Commands

```powershell
# Check code quality
.\quick-start.ps1 lint

# Auto-fix and format
.\quick-start.ps1 format

# Type check
.\quick-start.ps1 typecheck

# All checks
.\quick-start.ps1 check
```

---

## Manual Commands (Current)

```powershell
# Lint
uv run ruff check .
uv run ruff check --fix .

# Format
uv run ruff format .

# Type check
uv run mypy app
```

---

## Benefits

- ⚡ 10-100x faster than traditional tools
- 🔧 Auto-fixes most issues  
- 🐛 Catches bugs before runtime
- 📚 Better IDE support with type hints

---

**See full guide for configuration, CI/CD integration, and best practices.**
