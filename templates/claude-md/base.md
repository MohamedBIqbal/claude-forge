# Claude Instructions for [PROJECT_NAME]

## Project Overview

[DESCRIPTION]

---

## Technical Context

**Framework:** [FRAMEWORK]
**Domain:** [DOMAIN]

---

## Service Configuration

**Ports and endpoints to document:**
```
Backend:  port XXXX
Frontend: port XXXX
Database: [type], database name "[name]"
```

**Start commands:**
```bash
# Backend
cd backend && [start command]

# Frontend
cd frontend && [start command]
```

---

## Development Guidelines

### Code Style
- Follow existing patterns in the codebase
- Keep functions focused and single-purpose
- Add comments only where logic isn't self-evident

### AI Agent Patterns
- Skills define HOW; Agents define WHAT/WHEN
- Target ~15K tokens max per agent context
- Use progressive disclosure for complex skills

### Avoiding Hardcoding
- Use generic patterns with placeholders, not specific examples
- Multishot examples teach patterns, not keyword lists
- Dynamic detection over prescriptive lists

---

## Available Skills

| Skill | Purpose |
|-------|---------|
| /project-setup | Set up or reorganize project structure |

---

## Context Persistence

- Index: `.claude/context/_index.md`
- Active: `.claude/context/active/`
- Archive: `.claude/context/archive/`

**Save context** when approaching limits or before major topic switches.

---

## Safety Guidelines

**ALWAYS ask before:**
- Database modifications
- Destructive git operations (push --force, reset --hard)
- External system changes
- Credential modifications
