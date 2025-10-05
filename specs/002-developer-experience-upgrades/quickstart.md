# Quick Reference: Developer Experience Upgrades

**Feature**: 002 - Developer Experience Upgrades
**Quick Start**: Enhanced CLI workflow with verbosity control and code quality tools

---

## New Capabilities at a Glance

### Verbosity Control
```powershell
# Clean, minimal output (NEW default)
.\quick-start.ps1 setup

# Full diagnostic output
.\quick-start.ps1 setup -Detail
```

### Test Filtering
```powershell
.\quick-start.ps1 test                # All tests (pytest + validation)
.\quick-start.ps1 test -Unit          # Unit tests only
.\quick-start.ps1 test -Unit -Coverage # Unit tests with coverage
```

### Code Quality
```powershell
.\quick-start.ps1 lint      # Check code quality
.\quick-start.ps1 format    # Auto-format code
.\quick-start.ps1 check     # Lint + type check
```

### Clean Logging (Windows)
```powershell
.\quick-start.ps1 serve -Clean        # No ANSI codes
.\quick-start.ps1 serve -Clean -NewWindow  # Clean logs in new window
```

---

## Common Workflows

### First-Time Setup
```powershell
# 1. Install dependencies (minimal output)
.\quick-start.ps1 setup

# 2. Run quick validation
.\quick-start.ps1 test -Unit

# 3. Start clean server
.\quick-start.ps1 serve -Clean -NewWindow
```

### Development Cycle
```powershell
# Make changes...

# Check code quality
.\quick-start.ps1 lint

# Auto-format if needed
.\quick-start.ps1 format

# Run relevant tests
.\quick-start.ps1 test -Unit -Detail

# Restart server
.\quick-start.ps1 serve -Clean
```

### Pre-Commit
```powershell
.\quick-start.ps1 check          # Quality checks
.\quick-start.ps1 test -Coverage # Tests with coverage
```

### Troubleshooting
```powershell
# Full diagnostic output for any action
.\quick-start.ps1 setup -Detail
.\quick-start.ps1 test -Unit -Detail
.\quick-start.ps1 serve -Detail
```

---

## All Flags Summary

| Flag | Actions | Purpose |
|------|---------|---------|
| `-Detail` | All | Verbose output with full diagnostics |
| `-Clean` | serve | ANSI-free logging (Windows-friendly) |
| `-Unit` | test | Run only unit tests |
| `-Contract` | test | Run only contract tests |
| `-Integration` | test | Run only integration tests |
| `-Validation` | test | Run only validation suite |
| `-Coverage` | test | Generate coverage reports |
| `-NewWindow` | serve | Start server in new window |
| `-Reload` | serve | Enable auto-reload |
| `-Port` | serve | Custom port (default: 8000) |

---

## Migration from Feature 001

### What Changed
- **Default output**: Now minimal (was verbose) → Add `-Detail` for old behavior
- **test action**: Now includes validation suite → Use `-Unit` for unit-only
- **validate action**: Now deprecated → Use `test -Validation`

### What Stayed the Same
- All existing commands still work
- No flags required (defaults are sensible)
- Server behavior unchanged (unless using `-Clean`)

---

## Validation Checklist

After implementing this feature, verify:

- [ ] `setup` shows minimal output by default
- [ ] `setup -Detail` shows all steps and external tool output
- [ ] `test` runs all test types (pytest + validation)
- [ ] `test -Unit` runs only unit tests
- [ ] `test -Coverage` generates coverage report
- [ ] `lint` checks code without modifying
- [ ] `format` auto-formats code
- [ ] `check` runs lint + type check
- [ ] `serve -Clean` uses clean logging
- [ ] `validate` shows deprecation warning
- [ ] All errors visible regardless of verbosity
- [ ] Backward compatibility: existing commands work unchanged

---

**Status**: ✅ Ready for implementation (Phase 2 tasks)
