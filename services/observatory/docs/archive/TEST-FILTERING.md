# Test Filtering Implementation Guide

**Status**: 📋 Planned  
**Priority**: HIGH  
**Effort**: ~30 minutes  
**Impact**: Significantly faster development workflow

---

## Problem Statement

Currently, running `.\quick-start.ps1 test` executes all tests including:
- 58 fast unit tests (~2 seconds)
- 20 skipped tests (Redis/async timing issues)
- Contract tests requiring server
- Slow integration paths

**Result**: Slow feedback loop during active development (2+ minutes)

**Desired**: Granular control to run only relevant test subsets

---

## Proposed Commands

```powershell
# Fast unit tests only (default for development)
.\quick-start.ps1 test -Unit              # ~2 seconds

# Quick smoke tests (fastest, stops on first fail)
.\quick-start.ps1 test -Quick             # ~5 seconds

# Contract tests (API validation, requires server)
.\quick-start.ps1 test -Contract          # ~30 seconds

# Integration tests (all services)  
.\quick-start.ps1 test -Integration       # ~5 minutes

# With coverage report
.\quick-start.ps1 test -Unit -Coverage    # Opens HTML report

# Watch mode (auto-rerun on changes)
.\quick-start.ps1 test -Unit -Watch       # TDD workflow
```

---

## Implementation Details

See full implementation in this file. Key features:
- Auto-detect missing services for integration tests
- Generate and open HTML coverage reports
- Progress feedback during test runs
- Clear error messages for missing dependencies

---

## Performance Targets

| Test Suite | Duration | When to Run |
|------------|----------|-------------|
| Quick      | < 5 seconds | Every save (watch mode) |
| Unit       | < 10 seconds | Before each commit |
| Contract   | < 30 seconds | Before push |
| Integration | < 5 minutes | Before PR / CI/CD |

---

**See full guide for implementation details and code examples.**
