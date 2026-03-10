# Dependency Analysis Reference

## Why Audit Dependencies?

1. **Security**: Outdated packages have known vulnerabilities
2. **Performance**: Unused packages increase bundle size and install time
3. **Maintenance**: Fewer dependencies = less to maintain
4. **Compatibility**: Outdated packages may conflict with newer ones

---

## Python Dependencies

### Finding Unused Packages

**Automatic detection limitations:**
- Dynamic imports (`importlib.import_module()`) not detected
- Plugins/extensions loaded by config not detected
- CLI tools used via subprocess not detected

**Common false positives:**
```python
# These may appear unused but are actually needed:
- pytest, pytest-* (test runners)
- black, flake8, mypy (dev tools)
- gunicorn, uvicorn (WSGI/ASGI servers)
- alembic (migration tool)
- python-dotenv (loaded via .env)
```

### Checking Outdated

```bash
# List outdated packages
pip list --outdated

# Show details for specific package
pip show <package>

# Update single package
pip install --upgrade <package>

# Update all (careful!)
pip list --outdated | cut -d' ' -f1 | xargs pip install --upgrade
```

### Safe Removal Process

1. **Check import coverage**
   ```bash
   grep -r "import package" --include="*.py" .
   grep -r "from package" --include="*.py" .
   ```

2. **Check config files**
   - pytest.ini, setup.cfg (pytest plugins)
   - pyproject.toml (tool configurations)
   - alembic.ini (database migrations)

3. **Remove from requirements**
   ```bash
   # Edit requirements.txt
   # Then reinstall to verify
   pip install -r requirements.txt
   ```

4. **Run tests**

---

## Node.js Dependencies

### Finding Unused Packages

**Using depcheck:**
```bash
npx depcheck

# With options
npx depcheck --ignores="eslint,prettier"
```

**Common false positives:**
```javascript
// These may appear unused but are needed:
- @types/* (TypeScript types)
- eslint-* (linting plugins)
- postcss, autoprefixer (CSS processing)
- vite plugins (loaded via config)
```

### Checking Outdated

```bash
# List outdated
npm outdated

# Interactive update
npx npm-check-updates -i

# Update specific package
npm update <package>

# Update to latest major version
npm install <package>@latest
```

### Dependencies vs DevDependencies

**dependencies**: Required at runtime
```json
{
  "dependencies": {
    "react": "^18.0.0",
    "axios": "^1.0.0"
  }
}
```

**devDependencies**: Only needed for development
```json
{
  "devDependencies": {
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "@types/react": "^18.0.0"
  }
}
```

### Safe Removal Process

1. **Check imports**
   ```bash
   grep -r "from 'package'" --include="*.ts" --include="*.tsx" .
   grep -r "require('package')" --include="*.js" .
   ```

2. **Check config files**
   - vite.config.ts (plugins)
   - tailwind.config.js (plugins)
   - postcss.config.js (plugins)
   - .eslintrc (extends, plugins)

3. **Remove**
   ```bash
   npm uninstall <package>
   ```

4. **Test build**
   ```bash
   npm run build
   npm test
   ```

---

## Dependency Hygiene

### Regular Maintenance

**Weekly:**
- Check for security advisories (`npm audit`, `pip-audit`)

**Monthly:**
- Review outdated packages
- Update patch versions

**Quarterly:**
- Update minor versions
- Review and remove unused packages

### Lock Files

**Python:**
- `requirements.txt` with pinned versions
- Or `poetry.lock` / `pip-tools`

**Node.js:**
- `package-lock.json` (npm)
- `yarn.lock` (yarn)
- `pnpm-lock.yaml` (pnpm)

**Always commit lock files** to ensure reproducible builds.

---

## Security Scanning

### Python
```bash
# pip-audit
pip install pip-audit
pip-audit

# safety
pip install safety
safety check
```

### Node.js
```bash
# Built-in
npm audit

# Fix automatically
npm audit fix

# Fix with breaking changes
npm audit fix --force
```
