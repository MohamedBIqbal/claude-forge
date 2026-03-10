---
name: claude-forge
description: Set up, audit, or reorganize Claude Code projects following Anthropic best practices. Use when creating new AI agent projects, running project health audits, migrating existing projects to Claude Code best practices, or scaffolding agent/skill structures.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
argument-hint: "[new|declutter|audit|scaffold|consolidate-env|deps]"
---

# Claude Forge - Project Setup Skill

Set up new projects or reorganize existing ones following Anthropic's official best practices.

## Quick Start

```
/claude-forge new              # Set up new project with best practices
/claude-forge declutter        # Reorganize Claude Code files to best practices
/claude-forge audit            # Read-only health check (configs, deps, structure)
/claude-forge scaffold         # Create missing app directories (backend/frontend)
/claude-forge consolidate-env  # Compare and merge .env files
/claude-forge deps             # Analyze dependencies (unused, outdated)
/claude-forge                  # Interactive mode (asks which)
```

---

## Mode Detection

**If `$ARGUMENTS` starts with "new"**: Run new project workflow
**If `$ARGUMENTS` starts with "declutter"**: Run declutter workflow
**If `$ARGUMENTS` starts with "audit"**: Run audit workflow (read-only, safe)
**If `$ARGUMENTS` starts with "scaffold"**: Run scaffold workflow (create app dirs)
**If `$ARGUMENTS` starts with "consolidate-env"**: Run env consolidation workflow
**If `$ARGUMENTS` starts with "deps"**: Run dependency analysis workflow
**If `$ARGUMENTS` is empty**: Ask user which mode

---

## Edge Case Handling

### Running `new` on existing project

Before starting, check:
```bash
ls CLAUDE.md .claude/ 2>/dev/null
```

**If CLAUDE.md or .claude/ exists:**
- STOP immediately
- Inform: "This project already has Claude Code structure"
- Show what exists
- Suggest: "Use `/claude-forge declutter` to reorganize existing project"
- Do NOT proceed with `new`

### Running `declutter` on empty/new project

Before starting, check:
```bash
ls *.md .claude/ backend/ frontend/ src/ 2>/dev/null
```

**If no existing structure found:**
- STOP immediately
- Inform: "This appears to be a new/empty project - nothing to declutter"
- Suggest: "Use `/claude-forge new` to set up a fresh project"
- Do NOT proceed with `declutter`

---

## Workflow: New Project Setup

### Step 1: Gather Project Information

Ask the user for:
1. **Project name** (default: current directory name)
2. **Project description** (1-2 sentences)
3. **AI Framework**: LangGraph | CrewAI | MCP | ADK | Generic
4. **Domain** (optional): Check `templates/domains/` for available domain templates

### Step 2: Create Directory Structure

```bash
mkdir -p .claude/{skills,agents,rules,context/active}
```

Target structure:
```
project/
├── CLAUDE.md                 # Main instructions (<200 lines)
├── .claude/
│   ├── skills/               # Custom skills
│   ├── agents/               # Custom subagents
│   ├── rules/                # Path-scoped rules
│   └── context/
│       ├── _index.md         # Context registry
│       └── active/           # Active session context
```

### Step 3: Generate CLAUDE.md

Read the base template from `${CLAUDE_SKILL_DIR}/templates/claude-md/base.md`

Then append framework-specific sections from:
- `${CLAUDE_SKILL_DIR}/templates/claude-md/langgraph.md` (if LangGraph)
- `${CLAUDE_SKILL_DIR}/templates/claude-md/crewai.md` (if CrewAI)
- `${CLAUDE_SKILL_DIR}/templates/claude-md/mcp.md` (if MCP)
- `${CLAUDE_SKILL_DIR}/templates/claude-md/adk.md` (if ADK)

Then append domain-specific sections from `${CLAUDE_SKILL_DIR}/templates/domains/` if selected.

Replace placeholders:
- `[PROJECT_NAME]` -> actual project name
- `[DESCRIPTION]` -> actual description
- `[FRAMEWORK]` -> selected framework
- `[DOMAIN]` -> selected domain

### Step 4: Create Starter Files

1. Create `.claude/context/_index.md` with empty registry
2. Copy relevant agent templates if framework-specific agents exist
3. Create starter rules if requested

### Step 5: Verify and Report

Run verification checklist:
- [ ] CLAUDE.md exists and is readable
- [ ] `.claude/` directory structure is correct
- [ ] Context persistence directories exist

Output summary of created files.

---

## Workflow: Declutter Existing Project

Reorganize an existing project to best practices without breaking functionality.

### Step 1: Safety Scan

**CRITICAL SAFETY RULES:**
- NEVER delete files - only MOVE them
- NEVER overwrite without explicit user confirmation
- ALWAYS show the full migration plan before any action
- ALWAYS check for import/reference breakage before moving

Check existing structure:
```bash
# List root level files
ls -la *.md *.py *.sh 2>/dev/null

# Check existing .claude structure
ls -la .claude/ 2>/dev/null

# Find all skill-related files
find . -maxdepth 1 -name "*skill*.md" -o -name "SKILL.md"

# Find docs that could be consolidated
find . -maxdepth 1 -name "*.md" | grep -v README | grep -v CLAUDE
```

### Step 2: Analyze What Needs Moving

**Skills at root** → Move to `.claude/skills/<name>/SKILL.md`:
```
SKILL.md           → .claude/skills/demo-prep/SKILL.md
agentskill.md      → .claude/skills/agent-design/SKILL.md
contextskill.md    → .claude/skills/context/SKILL.md
judgeskill.md      → .claude/skills/judge/SKILL.md
```

**Docs at root** → Move to `docs/`:
```
CHANGELOG.md       → docs/CHANGELOG.md
LIMITATIONS.md     → docs/LIMITATIONS.md
script*.md         → docs/scripts/
```

**Keep at root**:
- README.md
- CLAUDE.md
- Config files (.env, pyproject.toml, docker-compose.yml, etc.)
- Entry scripts (gxrag.sh, etc.)

### Step 3: Check for Breakage

Before moving any file, check if it's referenced elsewhere:
```bash
# For each file to move, check references
grep -r "filename.md" --include="*.py" --include="*.md" --include="*.ts" .
```

If references found:
- Show user what references exist
- Ask if they want to proceed (references will need manual update)
- Or skip that file

### Step 4: Present Migration Plan

Show user a table:
```
| Current Location      | New Location                        | References | Action    |
|-----------------------|-------------------------------------|------------|-----------|
| SKILL.md              | .claude/skills/demo-prep/SKILL.md   | 0          | Move      |
| agentskill.md         | .claude/skills/agent-design/SKILL.md| 2 refs     | Ask user  |
| CHANGELOG.md          | docs/CHANGELOG.md                   | 0          | Move      |
```

**Ask for confirmation before proceeding.**

### Step 5: Execute Migration

For each approved move:
```bash
# Create target directory
mkdir -p .claude/skills/<skill-name>/

# Move file (git mv if in git repo)
git mv old-location new-location  # or mv if not git

# Update CLAUDE.md references if needed
```

### Step 6: Create Missing Structure

Ensure these exist after migration:
```
.claude/
├── skills/           # Created with migrated skills
├── agents/           # Create if missing
├── rules/            # Keep existing or create
└── context/
    ├── _index.md     # Create if missing
    └── active/       # Create if missing
```

### Step 7: Update CLAUDE.md

If skill files were moved, update CLAUDE.md to reference new locations:
- Update any `@skillname.md` imports to `@.claude/skills/<name>/SKILL.md`
- Update the "Available Skills" table

### Step 8: Generate Report

```markdown
## Declutter Complete

### Files Moved
| From | To |
|------|-----|
| ... | ... |

### Structure Created
- .claude/skills/
- .claude/agents/
- ...

### Manual Actions Needed
- Update X references in Y files
- ...

### Verification
- [ ] Run tests to verify nothing broken
- [ ] Check imports still resolve
- [ ] Verify skills load with /claude-forge
```

---

## Workflow: Audit (Read-Only)

Run a comprehensive health check without modifying anything.

### What It Checks

1. **Claude Code Structure**
   - CLAUDE.md exists and line count
   - .claude/ directory completeness
   - Skills/agents/rules/context directories

2. **Configuration Files**
   - Find all .env files across project
   - Compare keys (NOT values) across locations
   - Identify conflicts, duplicates, unique keys

3. **Structure Issues**
   - Skills at root that should be in .claude/skills/
   - Docs scattered that should be in docs/

4. **Dependencies**
   - Python: requirements.txt/pyproject.toml
   - Node: package.json

5. **Application Structure** (backend/frontend)
   - Backend: api/, skills/, services/, models/, agents/, tests/
   - Frontend: src/, components/, pages/, hooks/, services/
   - Large files (>500 lines backend, >300 lines components)
   - Catch-all directories (utils/ with too many files)
   - Missing __init__.py (Python) or index.ts (TypeScript)

### Running the Audit

Execute the audit script:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/audit.py .
```

For JSON output (for further processing):
```bash
python ${CLAUDE_SKILL_DIR}/scripts/audit.py . --json
```

### Safety
- **Read-only**: No files are modified
- **No secrets exposed**: Shows key names only, values are masked
- **Safe to run anytime**: No confirmation needed

See [references/folder-structures.md](references/folder-structures.md) for recommended patterns.

### After Audit

Based on findings, suggest next steps:
- "Run `/claude-forge declutter` to fix Claude Code structure"
- "Run `/claude-forge scaffold` to create missing app directories"
- "Run `/claude-forge consolidate-env` to merge configs"
- "Run `/claude-forge deps` to clean dependencies"

---

## Workflow: Scaffold Application Structure

Create missing directories for backend/frontend following best practices.

### What It Creates

**Backend (Python/FastAPI):**
```
backend/
├── api/                     # API routes (creates __init__.py)
│   └── routes/              # Endpoint modules
├── skills/                  # Business logic modules
├── services/                # Shared services
├── models/                  # Pydantic models
│   ├── domain/              # Business entities
│   └── api/                 # Request/response schemas
├── agents/                  # LangGraph agents
│   └── nodes/               # Graph nodes
├── core/                    # Core utilities
└── tests/                   # Test directory
    ├── unit/
    └── integration/
```

**Frontend (React/Vite):**
```
frontend/src/
├── components/              # React components
│   ├── ui/                  # Base UI components
│   └── features/            # Feature components
├── pages/                   # Route pages
├── hooks/                   # Custom hooks
├── services/                # API clients
├── stores/                  # State management
├── types/                   # TypeScript types
└── utils/                   # Utilities
```

### Running Scaffold

```bash
/claude-forge scaffold
/claude-forge scaffold backend    # Backend only
/claude-forge scaffold frontend   # Frontend only
```

### Step 1: Detect Project Type

Check what exists:
```bash
ls backend/ frontend/ src/ 2>/dev/null
```

### Step 2: Show Plan

Present directories to create:
```
## Scaffold Plan

Backend directories to create:
  [x] backend/api/           (missing)
  [x] backend/api/routes/    (missing)
  [ ] backend/skills/        (exists)
  [x] backend/models/        (missing)
  ...

Create these directories? (yes/no)
```

### Step 3: Create Directories

For each approved directory:
```bash
mkdir -p backend/api/routes
touch backend/api/__init__.py
touch backend/api/routes/__init__.py
```

For TypeScript:
```bash
mkdir -p frontend/src/hooks
echo "export {};" > frontend/src/hooks/index.ts
```

### Step 4: Add Placeholder Files

Create minimal `__init__.py` for Python:
```python
"""API routes package."""
```

Create barrel `index.ts` for TypeScript:
```typescript
// Barrel export for hooks
export {};
```

### Safety Rules

- **Only creates directories** - never modifies existing files
- **Skips existing** - won't overwrite anything
- **Shows plan first** - user confirms before creation
- **Minimal files** - only __init__.py / index.ts, no boilerplate code

### What It Does NOT Do

- Refactor existing code
- Move files between directories
- Split large files
- Create boilerplate/template code

For refactoring guidance, see [references/folder-structures.md](references/folder-structures.md).

Based on findings, suggest next steps:
- "Run `/claude-forge declutter` to fix structure issues"
- "Run `/claude-forge consolidate-env` to merge configs"
- "Run `/claude-forge deps` to clean dependencies"

---

## Workflow: Consolidate Environment Files

Compare and merge .env files across the project.

### What It Does

1. **Scan**: Find all .env files (excluding examples, templates, backups)
2. **Parse**: Extract key-value pairs (values are masked for security)
3. **Compare**: Categorize keys as shared, conflicting, unique, or duplicate
4. **Report**: Show comparison table
5. **Suggest**: Recommend consolidation strategy

### Running Comparison

```bash
python ${CLAUDE_SKILL_DIR}/scripts/env_compare.py .
```

For JSON output:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/env_compare.py . --json
```

### Consolidation (with confirmation)

Dry run (preview changes):
```bash
python ${CLAUDE_SKILL_DIR}/scripts/env_compare.py . --consolidate
```

Apply changes:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/env_compare.py . --consolidate --apply
```

### Safety Rules

- **Never shows values**: Only key names displayed (values masked)
- **Never auto-merges conflicts**: Must resolve manually first
- **Creates backups**: Before modifying any .env file
- **Dry-run by default**: Must explicitly use `--apply` to change files

See [references/env-patterns.md](references/env-patterns.md) for best practices.

---

## Workflow: Dependency Analysis

Analyze Python and Node.js dependencies for issues.

### What It Checks

1. **Unused packages**: Declared but no imports found
2. **Outdated packages**: Updates available
3. **Missing imports**: Used but not declared (Python only)

### Running Analysis

```bash
python ${CLAUDE_SKILL_DIR}/scripts/dep_audit.py .
```

For JSON output:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/dep_audit.py . --json
```

Python only:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/dep_audit.py . --python-only
```

Node only:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/dep_audit.py . --node-only
```

### Limitations

**False positives for "unused":**
- Dynamic imports (`importlib.import_module()`)
- CLI tools (pytest, black, uvicorn)
- Plugins loaded via config
- Type stubs (@types/*)

### Safety Rules

- **Read-only analysis**: No packages removed automatically
- **Shows commands**: User must run removal commands manually
- **Test after changes**: Always verify build/tests pass

See [references/dep-analysis.md](references/dep-analysis.md) for detailed guidance.

---

## Templates Reference

Templates are located at `${CLAUDE_SKILL_DIR}/templates/`:

| Template | Purpose |
|----------|---------|
| `claude-md/base.md` | Core CLAUDE.md structure |
| `claude-md/langgraph.md` | LangGraph patterns section |
| `claude-md/crewai.md` | CrewAI patterns section |
| `claude-md/mcp.md` | MCP server patterns section |
| `claude-md/adk.md` | Google ADK patterns section |
| `domains/pharma-gxp.md` | GxP compliance section (optional) |
| `agents/explore-agent.md` | Read-only codebase explorer |
| `agents/coder-agent.md` | Implementation agent |
| `agents/reviewer-agent.md` | Code review agent |
| `skills/skill-template.md` | Generic skill template |
| `rules/code-style.md` | Code style rule template |
| `rules/testing.md` | Testing rule template |

---

## Best Practices Enforced

From [Anthropic's documentation](https://code.claude.com/docs/en/memory):

1. **CLAUDE.md < 200 lines** - Longer files reduce adherence
2. **Specific instructions** - "Use 2-space indent" not "format nicely"
3. **No conflicts** - Review for contradicting rules
4. **Skills for tasks** - Skills define HOW; Agents define WHAT/WHEN
5. **Path-scoped rules** - Use `.claude/rules/` for file-type specific guidelines

---

## Verification Checklist

After setup, verify:

- [ ] `CLAUDE.md` exists at root or `.claude/`
- [ ] `CLAUDE.md` is under 200 lines
- [ ] `.claude/` directory exists
- [ ] `.claude/context/_index.md` exists
- [ ] `.claude/context/active/` directory exists
- [ ] Any agents have valid YAML frontmatter
- [ ] Any skills have valid YAML frontmatter
- [ ] No circular `@` imports in CLAUDE.md
