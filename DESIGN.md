# Claude Forge Design Spec

## Overview

Extend `/claude-forge` from Claude Code organization to full project health management.

---

## Modes Summary

| Mode | Command | Scope | Risk |
|------|---------|-------|------|
| `new` | `/claude-forge new` | Create fresh Claude Code structure | Low |
| `declutter` | `/claude-forge declutter` | Reorganize Claude files only | Low |
| `audit` | `/claude-forge audit` | Read-only health check | None |
| `consolidate-env` | `/claude-forge consolidate-env` | Merge .env files | Medium |
| `deps` | `/claude-forge deps` | Dependency analysis | Low-Medium |

---

## Directory Structure

```
~/.claude/skills/claude-forge/
├── SKILL.md                          # Main entry (<500 lines)
├── DESIGN.md                         # This file
│
├── references/                       # Progressive disclosure docs
│   ├── env-patterns.md               # .env best practices
│   ├── dep-analysis.md               # Dependency patterns
│   ├── folder-structures.md          # Standard layouts
│   └── safety-rules.md               # What NOT to do
│
├── scripts/                          # Executable helpers
│   ├── env_compare.py                # Compare/diff .env files
│   ├── dep_audit.py                  # Find unused deps
│   ├── structure_report.py           # Generate HTML report
│   └── verify-structure.py           # Existing verifier
│
├── templates/                        # Existing templates
│   ├── claude-md/
│   ├── agents/
│   ├── rules/
│   └── skills/
│
└── examples/                         # Existing examples
    └── minimal-project/
```

---

## Mode: `audit`

### Purpose
Read-only health check. Shows what COULD be improved without changing anything.

### Output Format
```
=== PROJECT HEALTH AUDIT ===

## Claude Code Structure
| Check | Status | Details |
|-------|--------|---------|
| CLAUDE.md exists | PASS | 156 lines |
| CLAUDE.md < 200 lines | PASS | |
| .claude/ structure | WARN | Missing agents/ |
| Skills at root | WARN | 5 files should move |

## Configuration Files
| File | Location | Conflicts |
|------|----------|-----------|
| .env | root | — |
| .env | backend/ | 3 keys differ from root |
| .env | frontend/ | 1 key differs |

Conflicting keys:
- DATABASE_URL: root="postgres://..." backend="sqlite://..."
- API_KEY: root="sk-..." backend="sk-..." (identical, duplicate)

## Dependencies
| Package Manager | Location | Unused | Outdated |
|-----------------|----------|--------|----------|
| pip | backend/ | 3 | 7 |
| npm | frontend/ | 12 | 23 |

## Folder Structure
| Issue | Current | Suggested |
|-------|---------|-----------|
| Skills at root | 5 files | .claude/skills/ |
| Docs scattered | 4 files | docs/ |
```

### Implementation
```python
# scripts/audit.py pseudocode
def audit_project(root: Path) -> AuditReport:
    report = AuditReport()

    # 1. Claude Code structure
    report.add(check_claude_md(root))
    report.add(check_claude_dir(root))
    report.add(check_skills_location(root))

    # 2. Config files
    report.add(compare_env_files(root))

    # 3. Dependencies
    report.add(audit_python_deps(root))
    report.add(audit_node_deps(root))

    # 4. Folder structure
    report.add(analyze_structure(root))

    return report
```

### Safety
- **Read-only**: No file modifications
- **No secrets exposed**: Shows key names, not values
- **Skips**: node_modules, venv, .git, __pycache__

---

## Mode: `consolidate-env`

### Purpose
Compare .env files across project, identify conflicts, suggest/apply merge.

### Workflow
```
1. SCAN: Find all .env* files (excluding examples, templates)
2. PARSE: Extract key-value pairs from each
3. COMPARE: Build unified view
   - Identical across all: SHARED
   - Different values: CONFLICT
   - Exists in one only: UNIQUE
4. PRESENT: Show comparison table
5. CONFIRM: Ask user for merge strategy
6. EXECUTE: Apply chosen strategy
```

### Comparison Output
```
=== .ENV COMPARISON ===

SHARED (same value everywhere):
  NODE_ENV=development
  LOG_LEVEL=debug

CONFLICTS (different values):
  | Key          | root/.env | backend/.env | frontend/.env |
  |--------------|-----------|--------------|---------------|
  | DATABASE_URL | postgres  | sqlite       | —             |
  | API_PORT     | 8080      | 8000         | —             |

UNIQUE (exists in one location):
  | Key              | Location       |
  |------------------|----------------|
  | VITE_API_URL     | frontend/.env  |
  | CHROMA_HOST      | backend/.env   |

DUPLICATES (same value, multiple locations - can consolidate):
  | Key     | Locations                  |
  |---------|----------------------------|
  | API_KEY | root/.env, backend/.env    |
```

### Merge Strategies
```
Strategy A: "Consolidate to root"
  - Move all unique keys to root/.env
  - Keep service-specific in their locations
  - Create .env.example with all keys (no values)

Strategy B: "Keep separate, document conflicts"
  - Leave files as-is
  - Create ENVIRONMENT.md documenting all keys
  - Flag conflicts for manual resolution

Strategy C: "Service isolation"
  - Each service keeps own .env
  - Root .env only for shared infra (DB, Redis)
  - No duplication
```

### Safety Rules
- **NEVER show values** in output (only key names)
- **NEVER auto-merge conflicts** - always ask
- **BACKUP before modify**: Copy to .env.backup
- **Git-ignore check**: Warn if .env not in .gitignore

---

## Mode: `deps`

### Purpose
Analyze dependencies across package managers, find issues.

### Checks
1. **Unused dependencies**: Imported but never used in code
2. **Missing from lockfile**: In requirements but not locked
3. **Outdated**: Major/minor/patch updates available
4. **Duplicates**: Same package in multiple locations
5. **Security**: Known vulnerabilities (optional, requires network)

### Output
```
=== DEPENDENCY AUDIT ===

## Python (backend/)
Source: pyproject.toml + requirements.txt

| Package | Status | Issue |
|---------|--------|-------|
| requests | UNUSED | No imports found |
| flask | OK | |
| pandas | OUTDATED | 1.5.0 → 2.2.0 |

## Node (frontend/)
Source: package.json

| Package | Status | Issue |
|---------|--------|-------|
| lodash | UNUSED | No imports found |
| moment | OUTDATED | Consider dayjs |
| react | OK | |

## Actions Available
1. Remove unused (interactive)
2. Update outdated (show commands)
3. Generate report (deps-audit.md)
```

### Implementation
```bash
# Python unused detection
grep -r "import package" --include="*.py" backend/
grep -r "from package" --include="*.py" backend/

# Node unused detection
npx depcheck frontend/

# Outdated
pip list --outdated
npm outdated
```

### Safety Rules
- **No auto-remove**: Only suggest, user confirms
- **No auto-update**: Show commands, user runs
- **Skip devDependencies** unless explicitly included

---

## Mode: `declutter` (Enhanced)

### Current Behavior
- Move skill files to .claude/skills/
- Move docs to docs/
- Update CLAUDE.md references

### Enhanced Behavior
Add optional `--full` flag:
```
/claude-forge declutter        # Claude files only (current)
/claude-forge declutter --full # Include configs, suggest deps
```

With `--full`:
1. Run current declutter
2. Run audit (read-only)
3. Ask: "Found 3 .env conflicts. Run consolidate-env?"
4. Ask: "Found 12 unused deps. Run deps?"

---

## Safety Philosophy

### Tiered Risk Model
```
SAFE (no confirmation needed):
- Read files
- Generate reports
- Show diffs

CONFIRM (ask before):
- Move files
- Create directories
- Update references

DANGEROUS (explicit approval + backup):
- Modify .env files
- Remove dependencies
- Change configs
```

### Universal Rules
1. **Never delete** - only move or archive
2. **Never modify** without showing diff first
3. **Never touch** .git, node_modules, venv, __pycache__
4. **Always backup** before modifying configs
5. **Git-aware**: Use `git mv` in repos

### Abort Triggers
Stop immediately if:
- User types "abort", "stop", "cancel"
- Uncommitted changes detected (for destructive ops)
- Running in production (NODE_ENV=production)

---

## Progressive Disclosure

### SKILL.md Structure
```markdown
# Project Setup

Quick reference for all modes.

## Modes
[Brief 1-line descriptions]

## Quick Start
[Most common commands]

## Details
For detailed workflows, see:
- [references/env-patterns.md](references/env-patterns.md)
- [references/dep-analysis.md](references/dep-analysis.md)
```

### Loading Strategy
1. **Always loaded**: SKILL.md (mode detection, quick ref)
2. **On-demand**: references/* (when that mode runs)
3. **Executed**: scripts/* (output replaces content)

---

## Scripts Specification

### env_compare.py
```
Input:  Root directory path
Output: JSON report
{
  "shared": {"KEY": "value"},
  "conflicts": {"KEY": {"root": "v1", "backend": "v2"}},
  "unique": {"KEY": {"location": "frontend/.env"}},
  "duplicates": {"KEY": ["root/.env", "backend/.env"]}
}
```

### dep_audit.py
```
Input:  Root directory path, package manager (pip|npm|both)
Output: JSON report
{
  "python": {
    "unused": ["requests", "flask"],
    "outdated": [{"name": "pandas", "current": "1.5", "latest": "2.2"}]
  },
  "node": {...}
}
```

### structure_report.py
```
Input:  Root directory path
Output: HTML file (codebase-audit.html)
- Interactive tree view
- Collapsible sections
- Color-coded issues
```

---

## Implementation Order

### Phase 1: Audit Mode (Option B)
1. Create `references/safety-rules.md`
2. Create `scripts/audit.py`
3. Update SKILL.md with audit mode
4. Test on GxRAG project

### Phase 2: Full Enhancement (Option A)
1. Create `scripts/env_compare.py`
2. Create `scripts/dep_audit.py`
3. Create `references/env-patterns.md`
4. Create `references/dep-analysis.md`
5. Update SKILL.md with all modes
6. Create `scripts/structure_report.py` (HTML output)

---

## Testing Checklist

- [ ] `new` still works on empty directory
- [ ] `declutter` still works on GxRAG
- [ ] `audit` produces valid report
- [ ] `audit` never modifies files
- [ ] `consolidate-env` shows correct diffs
- [ ] `consolidate-env` creates backups
- [ ] `deps` finds known unused package
- [ ] All scripts handle missing files gracefully
- [ ] Works on macOS and Linux
