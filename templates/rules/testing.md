---
paths:
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/*.test.ts"
  - "**/*.spec.ts"
---

# Testing Guidelines

## Test Structure
- Arrange: Set up test data and conditions
- Act: Execute the code being tested
- Assert: Verify the expected outcome

## Naming
- Test names should describe the scenario
- Pattern: `test_[method]_[scenario]_[expected_result]`
- Example: `test_login_with_invalid_password_returns_401`

## Coverage
- Focus on business logic and edge cases
- Don't test framework code
- Aim for meaningful coverage, not 100%

## Mocking
- Mock external dependencies (APIs, databases)
- Don't mock the code being tested
- Keep mocks simple and focused

## Test Data
- Use realistic but fake data
- Don't use production data
- Consider using factories/fixtures

## Assertions
- One logical assertion per test
- Use descriptive assertion messages
- Test both success and failure cases
