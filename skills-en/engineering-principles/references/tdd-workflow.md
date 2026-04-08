# TDD Workflow

## When to Apply

- Project has a test framework configured (jest / vitest / junit / pytest / go test)
- New feature development or bug fixes

## When NOT to Apply

- Legacy project without test framework and no plans to introduce one
- Pure UI styling changes (no logic)
- One-off scripts / migration scripts

## Red-Green-Refactor Cycle

```
RED       → Write a failing test (define expected behavior)
GREEN     → Write the minimum code to make the test pass
REFACTOR  → Refactor code, keeping tests green
```

Each cycle should take 5-15 minutes.

## Test Pyramid

```
        /  E2E   \          Few · Slow · High confidence
       / Integration \      Moderate · Medium speed
      /  Unit Tests    \    Many · Fast · High frequency
```

| Level | Proportion | What to Test |
|-------|-----------|--------------|
| Unit | 70% | Pure functions, business logic, utility methods |
| Integration | 20% | API endpoints, database interactions, inter-module collaboration |
| E2E | 10% | Critical user flows, smoke tests |

## Specific Guidelines

- **DO**: Every new public function gets at least 1 positive + 1 negative test
- **DO**: For bug fixes, write a reproduction test first, then fix the code
- **DO**: Test method names describe behavior: `should_return_error_when_email_invalid`
- **DON'T**: Test implementation details (don't mock private methods)
- **DON'T**: Use conditional logic in tests (if/for)
- **DON'T**: Verify multiple unrelated behaviors in a single test

## BDD Extension (Requires E2E Framework)

Applicable when: Project has Cypress / Playwright configured.

Write acceptance scenarios in Gherkin format:

```gherkin
Scenario: User logs in successfully
  Given the user is on the login page
  When they enter correct username and password
  And click the login button
  Then they should be redirected to the homepage
  And the username should be displayed
```
