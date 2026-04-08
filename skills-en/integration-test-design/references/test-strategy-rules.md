# Integration Test Strategy Rules and Anti-Patterns

## Test Pyramid Proportions

| Level | Proportion | Execution Speed | Maintenance Cost |
|--|--|--|--|
| Unit tests | 70% | < 100ms each | Low |
| Integration tests | 20% | < 5s each | Medium |
| E2E tests | 10% | < 30s each | High |

## Integration Test Naming Convention

```
should_[expected_behavior]_when_[condition]
```

Examples:
- `should_return_paginated_list_when_page_size_is_specified`
- `should_throw_not_found_when_task_does_not_exist`
- `should_rollback_when_downstream_service_fails`

## Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--|--|--|
| Shared test data | Tests depend on each other | Each test creates its own data |
| Test order dependency | Fails in parallel execution | No shared state between tests |
| Over-mocking | Tests are unrealistic | Mock only uncontrollable external dependencies |
| God Test | One test verifies everything | One test, one assertion subject |
| Hardcoded URL/Port | Breaks on environment change | Use dynamic configuration |
| Sleep waits | Flaky, wastes time | Use Awaitility / polling |
| Ignoring cleanup | Test pollution | `@AfterEach` or transaction rollback |

## TestContainers Best Practices

### Container Reuse (Speed Up CI)
```java
// Use static containers (shared across test classes)
@Testcontainers
class Test1 {
    @Container
    static PostgreSQLContainer<?> pg = new PostgreSQLContainer<>("postgres:16");
}
```

### Container Wait Strategy
```java
new GenericContainer<>("custom-image")
    .waitingFor(Wait.forHttp("/health").forStatusCode(200))
    .withStartupTimeout(Duration.ofSeconds(60));
```

## WireMock Standards

### Exact Matching (Recommended)
```java
stubFor(get(urlEqualTo("/api/external/123"))
    .willReturn(aResponse()
        .withStatus(200)
        .withHeader("Content-Type", "application/json")
        .withBody("""
            {"id": 123, "name": "test"}
            """)));
```

### Simulating Timeout
```java
stubFor(get(urlEqualTo("/api/slow"))
    .willReturn(aResponse()
        .withStatus(200)
        .withFixedDelay(5000)));  // 5-second delay
```

### Simulating 500 Error
```java
stubFor(get(urlEqualTo("/api/fail"))
    .willReturn(aResponse().withStatus(500)));
```

## Boundary Scenario Checklist

- [ ] Empty list query (returns empty array, not null)
- [ ] Pagination page 0 / beyond total pages
- [ ] Deleting non-existent resource (404 / idempotent 204)
- [ ] Concurrent creation of same-name resource (unique constraint conflict → 409)
- [ ] Empty request body / missing fields (400 + detailed field errors)
- [ ] Oversized fields (exceeding database column length)
- [ ] Special character input (SQL injection attempts, XSS tags)
- [ ] Network timeout simulation (external dependency unreachable)
- [ ] Transaction rollback verification (data consistency on partial failure)
