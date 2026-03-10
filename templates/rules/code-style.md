---
paths:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.js"
---

# Code Style Guidelines

## General
- Use descriptive variable and function names
- Keep functions focused and single-purpose
- Maximum function length: ~50 lines
- Maximum file length: ~500 lines

## Python Specific
- Follow PEP 8 style guide
- Use type hints for function signatures
- Use docstrings for public functions
- Prefer f-strings for string formatting

## TypeScript/JavaScript Specific
- Use TypeScript for type safety
- Prefer const over let
- Use async/await over raw promises
- Export types alongside implementations

## Comments
- Add comments only where logic isn't obvious
- Prefer self-documenting code over comments
- Keep comments up to date with code changes
- Use TODO/FIXME for known issues
