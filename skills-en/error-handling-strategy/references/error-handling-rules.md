# Error Handling Rules and Anti-Patterns

## Exception Handling Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--|--|--|
| catch + ignore | Error is swallowed, hard to debug | At minimum log or re-throw |
| Catch generic Exception | Masks programming errors (NPE, etc.) | Catch specific exception types |
| Error codes instead of exceptions | Callers easily forget to check | Use exceptions for error paths |
| Exceptions as control flow | Poor performance and readability | Exceptions only for exceptional cases |
| Log + re-throw | Same exception logged multiple times | Only log at the final handling point |
| Return null for errors | Caller NPE risk | Use Optional or throw exception |
| Throw in finally | Overwrites original exception | finally should only clean up |

## Error Message Design

### User-Facing Messages
- Don't expose technical details (no class names, SQL, stack traces)
- Explain what happened + suggest action
- Example: `"Task not found, please check the task ID"` ✅
- Anti-example: `"NullPointerException at TaskService.java:42"` ❌

### Developer-Facing Logs
- Include full context: parameter values, state, call chain
- Use structured logging for easy searching
- Example: `log.error("Failed to start task taskId={} status={}", taskId, status, e)`

## Transactions and Exceptions

| Exception Type | Transaction Behavior | Configuration |
|--|--|--|
| RuntimeException | Auto rollback | Spring default |
| Checked Exception | No rollback | Requires `@Transactional(rollbackFor)` |
| Validation exception (Controller layer) | No transaction | Thrown outside transaction |

### Spring @Transactional Rules
```java
// Recommended: Explicit rollbackFor
@Transactional(rollbackFor = Exception.class)
public void process() { ... }

// Anti-pattern: Catching exception without re-throwing
@Transactional
public void process() {
    try {
        // ...
    } catch (Exception e) {
        log.error("...", e);
        // ❌ Transaction will NOT roll back!
    }
}
```

## Log Level Standards

| Level | Usage Scenario |
|--|--|
| ERROR | System exceptions, unrecoverable errors |
| WARN | Recoverable but abnormal situations (successful retry, degradation triggered) |
| INFO | Business-critical checkpoints (task started, completed, status changed) |
| DEBUG | Debug information (method parameters, intermediate states) |

## Timeout Configuration Reference

| Call Type | Connection Timeout | Read Timeout | Total Timeout |
|--|--|--|--|
| Database query | 3s | 10s | 15s |
| Internal microservice | 3s | 5s | 10s |
| Third-party API | 5s | 15s | 30s |
| File upload | 5s | 60s | 120s |

## Dead Letter Queue Handling

When message consumption fails and is non-retryable:

1. Route to Dead Letter Queue (DLQ)
2. Record failure reason + original message
3. Alert operations team
4. Provide manual replay interface
5. Periodically clean expired dead letters

## Idempotency and Error Retry

Retry mechanisms require business operations to be idempotent:

| Operation Type | Idempotency Strategy |
|--|--|
| Create | Idempotency-Key + deduplication table |
| Update | Optimistic locking (version number) |
| Delete | Inherently idempotent (deleting non-existent resource returns 204) |
| State change | State machine validation (only transition from valid prior states) |
