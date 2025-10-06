# CI Issues Analysis

## Issue 1: CI Failing - `uv sync` Missing Virtual Environment

**Status**: ❌ All recent main branch pushes failing  
**Cause**: CI workflow tries to run `uv sync` without creating a virtual environment first  
**Impact**: Every push to main fails CI checks

### Error Message
```
error: No virtual environment found; run `uv venv` to create an environment, 
or pass `--system` to install into a non-virtual environment
Process completed with exit code 2.
```

### Root Cause
The CI workflow at `.github/workflows/ci.yml` (lines 32-39) attempts to install dependencies using `uv sync --dev`, but `uv` requires either:
1. A virtual environment to be created first with `uv venv`, OR
2. The `--system` flag to install into the system Python

The workflow doesn't create a venv, and doesn't use `--system` flag.

### Fix
**Option A**: Create virtual environment (recommended)
```yaml
- name: Install dependencies
  if: steps.check-python.outputs.has_python == 'true'
  run: |
    if [ -f pyproject.toml ] || [ -f requirements.txt ]; then
      uv venv  # ADD THIS LINE
      uv sync --dev
    else
      uv venv  # ADD THIS LINE
      uv pip install ruff pytest mypy
    fi
```

**Option B**: Use system-wide installation (simpler for CI)
```yaml
- name: Install dependencies
  if: steps.check-python.outputs.has_python == 'true'
  run: |
    if [ -f pyproject.toml ] || [ -f requirements.txt ]; then
      uv sync --dev --system
    else
      uv pip install --system ruff pytest mypy
    fi
```

**Recommendation**: Use Option B (`--system` flag) for simplicity in CI environment.

---

## Issue 2: Pushes to Main Don't Trigger PRs

**Status**: ⚠️ Misunderstanding of GitHub workflow  
**Cause**: Not an issue - pushes to `main` should NOT trigger PRs  
**Impact**: None - this is expected behavior

### Explanation

Looking at your workflow history:
- **Run #10** (Oct 4, 20:51): ✅ **From PR #3** - passed
- **Run #9** (Oct 4, 20:42): ✅ **From PR branch** - passed  
- **Run #8** (Oct 4, 20:42): ✅ **From PR branch** - passed
- **Runs #11-15**: ❌ **Direct pushes to main** - all failing

### How GitHub PR Workflow Works

1. **Feature branches** → Create PR → CI runs on PR
2. **PR approved** → Merge to main → CI runs on main
3. **Direct push to main** → CI runs on main (no PR involved)

### Your Current Workflow

You're pushing directly to `main` without creating PRs first. This is why:
- Pushes to main don't create PRs (they shouldn't)
- CI runs on main and fails (Issue #1 above)

### Recommended Git Workflow

```bash
# Work on feature branch
git checkout -b feature-branch
git commit -m "feat: my changes"
git push origin feature-branch

# Create PR on GitHub
# PR triggers CI checks
# If CI passes, merge PR to main
# Merged code then has CI run on main
```

### Your Current Branch State

From earlier check:
```
main:                         54 commits ahead of origin/main
001-atrium-observatory-service: 56 commits ahead of origin/001
002-developer-experience-upgrades: 1 commit ahead of origin/002
```

**All branches are ahead** - you have 54+ unpushed commits on main!

---

## Summary & Action Items

### Immediate Fixes

1. **Fix CI workflow** (5 minutes)
   - Add `--system` flag to `uv` commands in `.github/workflows/ci.yml`
   - Lines 36 and 38 need updates
   
2. **Push pending work** (2 minutes)
   ```bash
   git push origin main
   git push origin 001-atrium-observatory-service
   git push origin 002-developer-experience-upgrades
   ```

3. **Verify CI passes** (1 minute)
   - Next push to main should pass CI checks
   - Verify on GitHub Actions page

### Long-term Workflow Improvement

Consider adopting a branch protection + PR workflow:

1. **Enable branch protection** on main
   - Require PR reviews before merging
   - Require status checks (CI) to pass
   
2. **Use feature branches** for all work
   - Create branch for each feature/fix
   - Push branch and create PR
   - Merge only after CI passes

3. **Keep main stable**
   - Main always has passing CI
   - Main represents deployable code
   - Direct pushes to main are rare/emergency only

### Quick Fix Script

```bash
# Fix CI workflow
cd .github/workflows
# Edit ci.yml to add --system flags

# Commit fix
git add ci.yml
git commit -m "fix(ci): add --system flag to uv commands for CI environment"

# Push to main (will fail CI one more time)
git push origin main

# Future pushes will pass
```

---

## Files to Modify

### `.github/workflows/ci.yml`

**Line 36** (change):
```yaml
uv sync --dev
```
to:
```yaml
uv sync --dev --system
```

**Line 38** (change):
```yaml
uv pip install ruff pytest mypy
```
to:
```yaml
uv pip install --system ruff pytest mypy
```

**Line 43** (change):
```yaml
uv run ruff check .
```
to:
```yaml
uv run --system ruff check .
```

**Line 47** (change):
```yaml
uv run mypy . --ignore-missing-imports
```
to:
```yaml
uv run --system mypy . --ignore-missing-imports
```

**Line 53** (change):
```yaml
uv run pytest tests/ -v
```
to:
```yaml
uv run --system pytest tests/ -v
```

---

## Testing the Fix

After modifying the workflow:

1. Commit and push:
   ```bash
   git add .github/workflows/ci.yml
   git commit -m "fix(ci): use system-wide Python packages in CI"
   git push origin main
   ```

2. Watch GitHub Actions run at:
   https://github.com/tmorgan181/atrium-grounds/actions

3. Verify all three jobs pass:
   - ✅ lint-and-test
   - ✅ commit-attribution
   - ✅ docker-build

---

## Why This Happens

**uv's design philosophy**:
- Encourages virtual environments for isolation
- Requires explicit `--system` flag to install globally
- CI environments often don't need venvs (ephemeral containers)

**Your CI setup**:
- Installs `uv` ✅
- Installs Python 3.11 ✅
- Tries to sync deps ❌ (no venv, no --system flag)

**Solution**: Tell `uv` to use system Python in CI (ephemeral environment, no isolation needed).
