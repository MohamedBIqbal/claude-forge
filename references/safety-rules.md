# Safety Rules for Project Setup

## Tiered Risk Model

### SAFE (No confirmation needed)
- Read files
- Generate reports
- Show diffs
- List directory contents
- Parse configs (without exposing secrets)

### CONFIRM (Ask before executing)
- Move files
- Create directories
- Update references in files
- Rename files

### DANGEROUS (Explicit approval + backup required)
- Modify .env files
- Remove dependencies
- Change configuration files
- Delete anything (should be MOVE instead)

---

## Universal Rules

1. **Never delete** - only move or archive
2. **Never modify** without showing diff first
3. **Never touch**:
   - `.git/`
   - `node_modules/`
   - `venv/`, `.venv/`
   - `__pycache__/`
   - `*.pyc`
   - `.DS_Store`
4. **Always backup** before modifying configs
5. **Git-aware**: Use `git mv` in git repos

---

## Secrets Protection

### Never expose in output:
- API keys
- Passwords
- Tokens
- Connection strings with credentials
- Private keys

### Safe to show:
- Key names (without values)
- File paths
- Line counts
- Structure information

### .env handling:
```
SAFE:    "DATABASE_URL exists in root/.env"
UNSAFE:  "DATABASE_URL=postgres://user:pass@host/db"
```

---

## Abort Triggers

Stop immediately if:
- User types "abort", "stop", "cancel"
- Uncommitted changes detected (for destructive ops)
- Running in production (NODE_ENV=production, ENVIRONMENT=prod)
- File permissions prevent backup

---

## Backup Protocol

Before modifying any config file:

1. Check if backup location is writable
2. Create backup: `filename.backup.YYYYMMDD-HHMMSS`
3. Verify backup was created
4. Only then proceed with modification
5. Report backup location to user

---

## Git Integration

### In git repos:
- Use `git mv` instead of `mv`
- Check for uncommitted changes before destructive ops
- Warn if moving files that are staged

### Not in git repos:
- Use standard `mv`
- Create manual backups more aggressively
- Suggest initializing git

---

## Error Handling

### Recoverable errors:
- File not found → Skip, continue, report
- Permission denied → Report, suggest fix
- Parse error → Show raw content, ask user

### Fatal errors:
- Cannot create backup → Abort operation
- Disk full → Abort with clear message
- Conflicting operations → Abort, explain

---

## Audit Mode Specific

The `audit` mode is special:
- **Read-only by design**
- **Cannot modify anything**
- **Safe to run anytime**
- **No confirmation needed**
- **No backups needed** (nothing changes)
