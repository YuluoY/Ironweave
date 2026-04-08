# Code Quality Checklist

## Clean Code (Always Applicable)

### Naming

- **DO**: `getUserByEmail(email)` — verb + noun, clear intent
- **DON'T**: `getData(e)` — meaningless abbreviation

### Functions

- Single function ≤ 30 lines (consider splitting if longer)
- Parameters ≤ 3 (use an object parameter if more)
- One function does one thing (describable with a single verb)
- Avoid boolean parameters (split into two functions)

### Avoid Magic Numbers

- **DO**: `const MAX_RETRY = 3; if (retries >= MAX_RETRY)`
- **DON'T**: `if (retries >= 3)`

### Comments

- Good code doesn't need comments explaining "what" (naming should be self-explanatory)
- Comments are for explaining "why" (business reasons, historical decisions, workarounds)
- **DON'T**: `// increment counter` `count++`

## Error Handling (Always Applicable)

### Exception Tiers

| Tier | Type | Handling |
|------|------|---------|
| Business exceptions | Validation failures, business rule violations | Return clear error codes and messages |
| System exceptions | Database timeouts, network errors | Log + degrade/retry |
| Fatal exceptions | Missing config, unavailable dependencies | Fail fast |

### Specific Guidelines

- **DO**: Custom exception classes to distinguish business vs system exceptions
- **DO**: Catch and format uniformly at system boundaries (Controller/API Gateway)
- **DON'T**: `catch (e) {}` — never swallow exceptions
- **DON'T**: Use exceptions to control normal flow

### Boundary Validation

- Validate input at system entry points (Controller/API)
- Domain layer assumes valid input (already validated at entry)
- **DO**: `if (!email.includes('@')) throw new ValidationError('...')`
- **DON'T**: Repeat the same validation at every layer

## Testability (When Test Framework Is Available)

- Inject dependencies through constructors (don't `new` inside methods)
- Prefer pure functions (no side effects, output depends only on input)
- Isolate external dependencies (DB / HTTP / filesystem) behind interfaces
- Avoid global state and side effects in static methods

## Performance Awareness (When DB / API Is Involved)

| Issue | Checklist Item |
|-------|---------------|
| N+1 queries | Single queries in a loop → switch to batch queries |
| Missing indexes | No index on WHERE/JOIN fields → check execution plan |
| Large data returns | API returning all fields → select only needed fields |
| Redundant computation | Same data queried multiple times in one request → cache/prefetch |

## Security Practices (When User Input / API Is Involved)

| Threat | Defense |
|--------|---------|
| SQL Injection | Parameterized queries, no SQL concatenation |
| XSS | Output encoding, CSP headers |
| CSRF | Token validation |
| Unauthorized access | Verify current user permissions on every API |
| Sensitive data | bcrypt passwords, sanitize logs, don't return sensitive fields |
