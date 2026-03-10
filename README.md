# Claude Forge

A Claude Code skill for setting up, auditing, and maintaining well-structured AI agent projects following Anthropic's best practices.

## Features

| Command | Description |
|---------|-------------|
| `/claude-forge new` | Set up new project with best practices |
| `/claude-forge declutter` | Reorganize scattered files to proper locations |
| `/claude-forge audit` | Read-only health check (structure, configs, deps) |
| `/claude-forge scaffold` | Create missing app directories (backend/frontend) |
| `/claude-forge consolidate-env` | Compare and merge .env files |
| `/claude-forge deps` | Analyze dependencies (unused, outdated) |

## Installation

### Option 1: Clone to global skills (recommended)

```bash
# Clone to your Claude Code skills directory
git clone https://github.com/MohamedBIqbal/claude-forge.git ~/.claude/skills/claude-forge
```

### Option 2: Clone to project

```bash
# Clone to your project's .claude/skills directory
git clone https://github.com/MohamedBIqbal/claude-forge.git .claude/skills/claude-forge
```

## Usage

After installation, use the skill in Claude Code:

```
/claude-forge new           # Interactive project setup
/claude-forge audit         # Check project health
/claude-forge declutter     # Organize files
```

## What It Does

### `new` - New Project Setup
- Creates `.claude/` directory structure (skills, agents, rules, context)
- Generates CLAUDE.md from templates
- Supports AI frameworks: LangGraph, CrewAI, MCP, ADK
- Optional domain templates (e.g., pharma-gxp for regulated industries)

### `declutter` - Project Reorganization
- Moves skill files to `.claude/skills/<name>/SKILL.md`
- Moves docs to `docs/`
- Updates references in CLAUDE.md
- Uses `git mv` when in a git repo
- Shows migration plan before any changes

### `audit` - Health Check (Read-Only)
- Checks CLAUDE.md exists and line count (<200 recommended)
- Verifies `.claude/` structure completeness
- Finds scattered skills/docs that should be organized
- Compares .env files across project (keys only, values masked)
- Checks for large files and missing `__init__.py`/`index.ts`

### `scaffold` - App Structure
- Creates missing backend directories (api/, models/, services/, agents/)
- Creates missing frontend directories (hooks/, services/, stores/, types/)
- Adds minimal `__init__.py` or `index.ts` barrel files
- Shows plan and asks for confirmation

### `consolidate-env` - Environment Files
- Finds all .env files (excluding .example, .template)
- Compares keys across files
- Identifies conflicts, duplicates, unique keys
- Dry-run by default, requires explicit `--apply`

### `deps` - Dependency Analysis
- Finds unused packages (declared but not imported)
- Python: requirements.txt, pyproject.toml
- Node: package.json
- Shows removal commands (doesn't auto-remove)

## Templates

The skill includes templates for:

| Template | Description |
|----------|-------------|
| `claude-md/base.md` | Core CLAUDE.md structure |
| `claude-md/langgraph.md` | LangGraph agent patterns |
| `claude-md/crewai.md` | CrewAI patterns |
| `claude-md/mcp.md` | MCP server patterns |
| `claude-md/adk.md` | Google ADK patterns |
| `domains/pharma-gxp.md` | GxP compliance (optional) |

## Best Practices Enforced

Based on [Anthropic's Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code):

1. **CLAUDE.md < 200 lines** - Longer files reduce adherence
2. **Specific instructions** - "Use 2-space indent" not "format nicely"
3. **No conflicts** - Review for contradicting rules
4. **Skills for tasks** - Skills define HOW; Agents define WHAT/WHEN
5. **Path-scoped rules** - Use `.claude/rules/` for file-type specific guidelines

## Safety

- **Never deletes files** - Only moves them
- **Shows plan first** - Always asks for confirmation before changes
- **Read-only audit** - `audit` mode never modifies anything
- **No secrets exposed** - .env comparison shows keys only
- **Git-aware** - Uses `git mv` when in a git repo

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Test your changes with `/claude-forge audit`
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE)

## Author

Built with Claude Code.
