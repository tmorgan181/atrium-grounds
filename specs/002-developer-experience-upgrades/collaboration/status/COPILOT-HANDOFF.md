# Copilot Handoff - Feature 002 Developer Experience Upgrades

**Status**: Parallel Phase 1 - Your Turn! 🚀
**Branch**: `002-developer-experience-upgrades`
**Your Tasks**: T016 + T024 (both quick wins)

---

## Quick Context

We're implementing **Feature 002: Developer Experience Upgrades** for the Observatory service. The goal is to make `quick-start.ps1` faster and more user-friendly.

**Progress**: 17/28 tasks complete (61%)
**What's Done**: All core features implemented by Claude
**What You Need**: Finish help text + add parameter validation

---

## Your Tasks (Parallel Phase 1)

### Task 1: T016 - Complete Help Text Examples

**File**: `services/observatory/quick-start.ps1` (Show-Help function, lines ~1251-1350)
**Status**: Partially done (new actions added, need examples)
**Time**: ~5 minutes

**What to Add**: Examples section needs more coverage for new features

```powershell
# Add these examples to the EXAMPLES section:

Write-Host "  Code Quality Examples:" -ForegroundColor DarkGray
Write-Host "  .\quick-start.ps1 lint" -ForegroundColor White
Write-Host "    Check code style (fast, read-only)" -ForegroundColor Gray
Write-Host ""
Write-Host "  .\quick-start.ps1 format" -ForegroundColor White
Write-Host "    Auto-format all code with ruff" -ForegroundColor Gray
Write-Host ""
Write-Host "  .\quick-start.ps1 check" -ForegroundColor White
Write-Host "    Pre-commit checks (lint + type check)" -ForegroundColor Gray
Write-Host ""
```

**Location**: Around line 1180-1185 (after existing examples, before MORE INFO section)

**Acceptance**: `.\quick-start.ps1 help` shows examples for lint/format/check

---

### Task 2: T024 - Add Parameter Validation

**File**: `services/observatory/quick-start.ps1` (after param block, before functions)
**Status**: Not started
**Time**: ~10 minutes

**What to Add**: Validate flag combinations and warn about conflicts

**Location**: Right after the param() block ends (around line 67), add this:

```powershell
# ============================================================================
# PARAMETER VALIDATION (Feature 002 - T024)
# ============================================================================

# Rule 1: -Clean only applies to serve action
if ($Clean -and $Action -ne "serve") {
    Write-Warning "-Clean flag only applies to 'serve' action (ignored)"
    $Clean = $false
}

# Rule 2: Test filters only apply to test action
if (($Unit -or $Contract -or $Integration -or $Validation -or $Coverage) -and $Action -ne "test") {
    Write-Warning "Test filtering flags (-Unit, -Contract, -Integration, -Validation, -Coverage) only apply to 'test' action (ignored)"
    $Unit = $false; $Contract = $false; $Integration = $false; $Validation = $false; $Coverage = $false
}

# Rule 3: Multiple test filters selected = run all selected types (informational)
$testFilterCount = @($Unit, $Contract, $Integration, $Validation).Where({$_}).Count
if ($testFilterCount -gt 1) {
    Write-Host "[INFO] Multiple test types selected - running: $(if($Unit){'Unit '})$(if($Contract){'Contract '})$(if($Integration){'Integration '})$(if($Validation){'Validation'})" -ForegroundColor Cyan
}

# Rule 4: -NewWindow only applies to serve action
if ($NewWindow -and $Action -ne "serve") {
    Write-Warning "-NewWindow flag only applies to 'serve' action (ignored)"
    $NewWindow = $false
}

# Rule 5: -Coverage without test action
if ($Coverage -and $Action -ne "test") {
    Write-Warning "-Coverage flag only applies to 'test' action (ignored)"
    $Coverage = $false
}
```

**Acceptance**:
- `.\quick-start.ps1 setup -Clean` shows warning
- `.\quick-start.ps1 lint -Unit` shows warning
- `.\quick-start.ps1 test -Unit -Contract` shows info message

---

## Testing Your Changes

```powershell
# 1. Pull latest changes
git pull

# 2. Test PowerShell parsing
pwsh -Command ". .\quick-start.ps1 -Action help"

# 3. Test help text
.\quick-start.ps1 help | Select-String "lint"

# 4. Test parameter validation
.\quick-start.ps1 setup -Clean          # Should warn
.\quick-start.ps1 test -Unit -Contract  # Should show info
.\quick-start.ps1 lint -Coverage        # Should warn
```

---

## Commit & Push

```powershell
git add quick-start.ps1
git commit -m "feat(002): T016+T024 - help examples + flag validation

T016: Complete help text examples
- Added code quality examples (lint/format/check)
- Clear, concise descriptions for each

T024: Parameter validation
- 5 validation rules for flag conflicts
- Warns when flags used with wrong action
- Informative messages for multi-flag scenarios

Testing:
- PowerShell parsing validated
- All warning scenarios tested
- Help text verified

Progress: 19/28 tasks complete (68%)
"
git push
```

---

## Context You Need

**Key Files**:
- `services/observatory/quick-start.ps1` - Main script (1400+ lines)
- `specs/002-developer-experience-upgrades/tasks.md` - Full task list

**New Features** (already implemented):
- ✅ Test filtering: `-Unit`, `-Contract`, `-Integration`, `-Validation`, `-Coverage`
- ✅ Verbosity control: `-Detail` flag for all actions
- ✅ Code quality: `lint`, `format`, `check` actions
- ✅ Clean logging: `-Clean` flag for serve action

**What You're Doing**:
1. Making help text more helpful (examples for new features)
2. Preventing user confusion (validate flag combinations)

---

## After You're Done

**Next**: Claude picks up with T023 (code refactoring), then you do T019-T021 (testing)

**Questions?** Check:
- `specs/002-developer-experience-upgrades/tasks.md` - Task details
- `specs/002-developer-experience-upgrades/collaboration/sessions/` - Session logs
- `specs/002-developer-experience-upgrades/collaboration/HUMAN-VALIDATION-GUIDE.md` - Testing guide

---

## TL;DR

```powershell
# 1. Add examples to help text (lint/format/check)
# 2. Add parameter validation block after param()
# 3. Test with warnings
# 4. Commit + push
# 5. Done! 🎉
```

**Estimated Time**: 15 minutes total
**Difficulty**: Easy - just adding validation logic
**Impact**: High - prevents user confusion

---

Good luck! Let Claude know when you're done so they can continue with refactoring.

🤖 **Claude is waiting** for you to complete T016+T024 before starting T023.
