# Environment File Patterns

## Best Practices

### 1. Single Source of Truth
- Root `.env` for shared configuration
- Service-specific `.env` only for truly unique values
- Avoid duplicating keys across files

### 2. Naming Conventions
```
# Service prefix
BACKEND_PORT=8080
FRONTEND_PORT=9080

# Environment suffix
DATABASE_URL_DEV=...
DATABASE_URL_PROD=...

# Feature flags
FEATURE_NEW_UI=true
```

### 3. File Hierarchy
```
project/
├── .env                  # Shared (DB, API keys, ports)
├── .env.example          # Template with all keys, no values
├── .env.local            # Local overrides (git-ignored)
├── backend/
│   └── .env              # Backend-only (if needed)
└── frontend/
    └── .env              # Frontend-only (VITE_*, NEXT_PUBLIC_*)
```

### 4. Security Rules
- `.env` files in `.gitignore`
- `.env.example` committed (no secrets)
- No production secrets in development files
- Use secret managers for production

---

## Common Patterns

### Monorepo with Shared Config
```
# Root .env - shared infrastructure
DATABASE_URL=postgres://...
REDIS_URL=redis://...
API_KEY=sk-...

# backend/.env - backend-specific
BACKEND_PORT=8080
WORKER_COUNT=4

# frontend/.env - frontend-specific
VITE_API_URL=http://localhost:8080
VITE_FEATURE_FLAG=true
```

### Separate Dev/Prod
```
# .env.development
DATABASE_URL=postgres://localhost/dev
DEBUG=true

# .env.production
DATABASE_URL=postgres://prod-server/prod
DEBUG=false
```

---

## Conflict Resolution

### Same Key, Different Values

**Option A: Environment suffix**
```
DATABASE_URL_DEV=sqlite://local.db
DATABASE_URL_PROD=postgres://prod/db
```

**Option B: Service prefix**
```
BACKEND_DATABASE_URL=postgres://...
FRONTEND_API_URL=http://...
```

**Option C: Intentional override**
```
# Root .env (default)
LOG_LEVEL=info

# backend/.env (override)
LOG_LEVEL=debug
```

---

## Migration Strategies

### Strategy A: Consolidate to Root
1. Move all shared keys to root `.env`
2. Keep only truly unique keys in service files
3. Use prefix/suffix for disambiguation

### Strategy B: Keep Separate
1. Document all keys in `.env.example`
2. Accept some duplication for clarity
3. Use validation to catch conflicts

### Strategy C: Environment Manager
1. Use tools like `direnv`, `dotenv-vault`
2. Single source loaded per environment
3. No file duplication
