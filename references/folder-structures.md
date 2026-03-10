# Application Folder Structure Patterns

## Backend (Python/FastAPI)

### Recommended Structure
```
backend/
├── main.py                  # FastAPI app entry
├── api/                     # Route handlers
│   ├── __init__.py
│   ├── routes/              # Endpoint definitions
│   └── deps.py              # Shared dependencies
├── skills/                  # Business logic modules (domain skills)
│   ├── retrieval/           # RAG/search skill
│   ├── extraction/          # Data extraction skill
│   └── judge/               # Evaluation skill
├── agents/                  # LangGraph/CrewAI agents
│   ├── orchestrator.py
│   └── workflows/
├── services/                # Shared services
│   ├── llm.py               # LLM client
│   ├── vectordb.py          # Vector database
│   └── database.py          # PostgreSQL
├── models/                  # Pydantic models
│   ├── domain/              # Business entities
│   └── api/                 # Request/response schemas
├── core/                    # Core utilities
│   ├── config.py            # Settings
│   └── logging.py           # Logging setup
├── data/                    # Data files (git-ignored)
└── tests/                   # Test files
    ├── unit/
    └── integration/
```

### Anti-patterns
- `utils/` with 50+ files (split by domain)
- `helpers/` catch-all (be specific)
- Flat structure with 100+ files in one directory
- Business logic in route handlers

---

## Frontend (React/Vite)

### Recommended Structure
```
frontend/
├── src/
│   ├── main.tsx             # Entry point
│   ├── App.tsx              # Root component
│   ├── components/          # Reusable components
│   │   ├── ui/              # Base UI (buttons, inputs)
│   │   └── features/        # Feature components
│   ├── pages/               # Route pages
│   ├── hooks/               # Custom hooks
│   ├── services/            # API clients
│   ├── stores/              # State management
│   ├── types/               # TypeScript types
│   └── utils/               # Utilities
├── public/                  # Static assets
└── tests/                   # Test files
```

### Anti-patterns
- Components with 500+ lines (split them)
- Business logic in components (use hooks/services)
- Deeply nested component trees (flatten)
- No separation between UI and feature components

---

## Monorepo Patterns

### Shared Code
```
project/
├── packages/
│   ├── shared/              # Shared types, utils
│   ├── ui/                  # Shared UI components
│   └── config/              # Shared configs
├── apps/
│   ├── backend/
│   └── frontend/
```

### Backend + Frontend
```
project/
├── backend/                 # Python backend
├── frontend/                # React frontend
├── shared/                  # Shared (types, constants)
└── docs/                    # Documentation
```

---

## AI/Agent Projects (LangGraph/CrewAI)

### LangGraph Pattern
```
backend/
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py      # Main graph
│   ├── nodes/               # Graph nodes
│   │   ├── retrieve.py
│   │   ├── extract.py
│   │   └── judge.py
│   ├── state.py             # Agent state
│   └── tools/               # Agent tools
├── skills/                  # Standalone skills (non-agent)
└── services/                # Shared services
```

### CrewAI Pattern
```
backend/
├── crews/
│   ├── research_crew.py
│   └── analysis_crew.py
├── agents/
│   ├── researcher.py
│   └── analyst.py
├── tasks/
│   └── task_definitions.py
└── tools/
    └── custom_tools.py
```

---

## Structure Health Checks

### Good Signs
- [ ] Clear separation: api/ vs skills/ vs services/
- [ ] Consistent naming (all lowercase, underscores)
- [ ] Tests mirror source structure
- [ ] No circular imports
- [ ] Each directory has __init__.py (Python)
- [ ] index.ts barrel exports (TypeScript)

### Warning Signs
- [ ] Files over 500 lines
- [ ] Directories with 50+ files
- [ ] Deep nesting (>4 levels)
- [ ] Inconsistent naming
- [ ] "misc", "other", "stuff" directories
- [ ] Business logic in wrong layer

### Critical Issues
- [ ] No clear entry point
- [ ] Circular dependencies
- [ ] Mixed concerns in single files
- [ ] No test directory
