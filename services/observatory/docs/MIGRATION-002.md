# Migration Guide: Feature 002 - Developer Experience Upgrades

**From**: Feature 001 (Basic Observatory Service)
**To**: Feature 002 (Enhanced Developer Experience)
**Branch**: `002-developer-experience-upgrades`

---

## Overview

Feature 002 introduces significant improvements to the Observatory developer experience:
- **Verbosity control** - Minimal output by default, `-Detail` for diagnostics
- **Test filtering** - Run specific test types for faster feedback
- **Code quality integration** - Built-in linting, formatting, and type checking
- **Clean logging** - ANSI-free output for Windows PowerShell 5.1

---

## What Changed

### 1. Default Output Behavior

**BEFORE (Feature 001)**:
```powershell
PS> .\quick-start.ps1 setup
# Outputs ~100+ lines of verbose installation logs
→ Creating virtual environment with uv...
+ Created virtual environment .venv
→ Installing dependencies...
+ pip install -e . [... hundreds of lines ...]
→ Installing development dependencies...
+ pip install pytest pytest-asyncio [... more output ...]
```

**AFTER (Feature 002)**:
```powershell
PS> .\quick-start.ps1 setup
# Outputs ~8 lines - scannable in <5 seconds
[OK] Virtual environment created
[OK] Dependencies installed
[OK] Development dependencies installed
[OK] API keys already exist
[OK] Setup complete!
```

**Migration**: No action required - new behavior is default. Use `-Detail` to get old behavior.

---

### 2. Test Action Behavior

**BEFORE (Feature 001)**:
```powershell
# Only option: run all tests (slow, ~2 minutes)
.\quick-start.ps1 test
```

**AFTER (Feature 002)**:
```powershell
# Run specific test types (fast iteration)
.\quick-start.ps1 test -Unit          # ~2 seconds (60x faster!)
.\quick-start.ps1 test -Contract      # Contract tests only
.\quick-start.ps1 test -Integration   # Integration tests only
.\quick-start.ps1 test -Validation    # Validation suite only

# Combine multiple types
.\quick-start.ps1 test -Unit -Contract

# Add coverage to any test type
.\quick-start.ps1 test -Unit -Coverage
```

**Migration**: Old behavior (`.\quick-start.ps1 test`) still works - runs all test types.

---

### 3. New Actions

**BEFORE**: No code quality actions

**AFTER**: Built-in quality checks
```powershell
.\quick-start.ps1 lint      # Check code style (fast, read-only)
.\quick-start.ps1 format    # Auto-format code with ruff
.\quick-start.ps1 check     # Lint + type check (pre-commit)
```

**Migration**: Add these to your workflow for better code quality.

---

### 4. Validate Action (DEPRECATED)

**BEFORE**:
```powershell
.\quick-start.ps1 validate  # Standalone validation action
```

**AFTER** (Deprecated):
```powershell
# Still works, but shows deprecation warning:
.\quick-start.ps1 validate
# [WARN] The 'validate' action is deprecated. Use 'test -Validation' instead.

# New recommended way:
.\quick-start.ps1 test -Validation
```

**Migration**: Update scripts to use `test -Validation` instead of `validate`.

---

### 5. Clean Logging for Windows

**NEW** in Feature 002:
```powershell
# Start server with ANSI-free logs (Windows PowerShell 5.1 compatible)
.\quick-start.ps1 serve -Clean
```

**When to use `-Clean`:**
- Windows PowerShell 5.1 (no ANSI support)
- CI/CD pipelines that don't support ANSI
- Log file capture
- Screen readers

---

## How to Get Old Behavior

If you prefer the verbose output from Feature 001:

### Use `-Detail` Flag

```powershell
# Verbose setup (like Feature 001)
.\quick-start.ps1 setup -Detail

# Verbose tests (like Feature 001)
.\quick-start.ps1 test -Detail

# Verbose code quality checks
.\quick-start.ps1 lint -Detail
```

The `-Detail` flag restores full diagnostic output for any action.

---

## Breaking Changes

### None! 🎉

Feature 002 is **fully backward compatible**:
- All Feature 001 commands still work
- Default output is minimal (new), but `-Detail` restores old behavior
- No changes to API, database, or core functionality

---

## Recommended Migration Path

### 1. Update Your Scripts (Optional)

**Old script**:
```powershell
# Feature 001 workflow
.\quick-start.ps1 setup
.\quick-start.ps1 test
.\quick-start.ps1 validate
.\quick-start.ps1 serve
```

**New script** (recommended):
```powershell
# Feature 002 workflow - faster iteration
.\quick-start.ps1 setup

# Quick validation during development
.\quick-start.ps1 test -Unit          # Fast feedback (~2s)

# Pre-commit checks
.\quick-start.ps1 check               # Lint + type check

# Full test suite before push
.\quick-start.ps1 test -Coverage

# Start server
.\quick-start.ps1 serve -NewWindow
```

### 2. Update CI/CD Pipelines (Optional)

**Feature 001 CI**:
```yaml
- name: Run Tests
  run: .\quick-start.ps1 test
```

**Feature 002 CI** (recommended):
```yaml
- name: Run Unit Tests
  run: .\quick-start.ps1 test -Unit

- name: Run Contract Tests
  run: .\quick-start.ps1 test -Contract

- name: Code Quality Checks
  run: .\quick-start.ps1 check

- name: Full Test Suite with Coverage
  run: .\quick-start.ps1 test -Coverage
```

Benefits:
- Faster feedback (unit tests run first)
- Better failure isolation
- Code quality checks before tests

---

## New Workflows Enabled

### Fast Development Cycle

```powershell
# 1. Make code changes
# ... edit files ...

# 2. Quick validation (2 seconds)
.\quick-start.ps1 test -Unit

# 3. Check code quality
.\quick-start.ps1 format    # Auto-format
.\quick-start.ps1 check     # Lint + type check

# 4. Full validation before commit
.\quick-start.ps1 test -Coverage
```

### Pre-Commit Hook Example

```powershell
# .git/hooks/pre-commit (PowerShell)
.\quick-start.ps1 check
if ($LASTEXITCODE -ne 0) {
    Write-Error "Pre-commit checks failed!"
    exit 1
}
```

---

## Performance Improvements

| Action | Feature 001 | Feature 002 | Speedup |
|--------|-------------|-------------|---------|
| `test` (all) | ~2 minutes | ~2 minutes | Same |
| `test -Unit` | N/A | ~2 seconds | **60x faster** |
| `setup` | ~100+ lines | ~8 lines | **Scannable in <5s** |
| Overhead | N/A | <100ms | **Minimal** |

---

## Troubleshooting

### Issue: "I don't see any output!"

**Cause**: Default mode suppresses verbose output.

**Solution**: Use `-Detail` flag:
```powershell
.\quick-start.ps1 setup -Detail
```

### Issue: "Validate action shows warning"

**Cause**: `validate` action is deprecated in Feature 002.

**Solution**: Use new recommended command:
```powershell
# Old (deprecated)
.\quick-start.ps1 validate

# New (recommended)
.\quick-start.ps1 test -Validation
```

### Issue: "ANSI codes in Windows PowerShell 5.1"

**Cause**: Windows PowerShell 5.1 doesn't support ANSI escape codes.

**Solution**: Use `-Clean` flag for serve action:
```powershell
.\quick-start.ps1 serve -Clean
```

---

## Rollback Instructions

If you need to roll back to Feature 001:

```powershell
# Checkout Feature 001 branch (if it exists)
git checkout 001-atrium-observatory-service

# Or checkout main before Feature 002 merge
git checkout main
```

**Note**: Feature 002 has no database migrations or breaking changes, so rollback is safe.

---

## Questions & Support

**Documentation**:
- `WORKFLOW.md` - Updated with Feature 002 examples
- `README.md` - Quick reference for new features

**Testing**:
- `scripts/performance-validation.ps1` - Validate overhead measurements
- `HUMAN-VALIDATION-GUIDE.md` - Manual testing checklist

**Issues**: Create GitHub issue with `feature-002` label

---

## Summary

Feature 002 is a **non-breaking enhancement** that:
- ✅ Improves developer experience (faster feedback, cleaner output)
- ✅ Maintains full backward compatibility (all Feature 001 commands work)
- ✅ Adds new capabilities (test filtering, code quality, clean logging)
- ✅ Minimal performance overhead (<100ms per action)

**Recommended Action**: Update workflows to use new features for faster development, but no migration is required.
