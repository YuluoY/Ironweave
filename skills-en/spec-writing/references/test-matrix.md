# Test Standards: Cross-Combination Matrix and Priority Assessment

## Cross-Combination Matrix

When a feature involves multiple independent test dimensions, you need to **explicitly list the dimension combination matrix** to provide a foundation for subsequent TDD test-driven development. Core value: Turn implicit combination logic into a trackable test case list, avoiding missed critical paths.

### Orchestration Steps

1. **Identify test dimensions**: Extract all independent variables that affect behavior from the requirement description
2. **List values for each dimension**: Enumerate all valid values for each dimension
3. **Generate combination matrix**: List all logical combinations in a table
4. **Assess priority**: Mark each combination as P0 / P1 / P2 / P3
5. **Annotate expected results**: Expected behavior for each combination

### When to Orchestrate

- When test dimensions ≥ 2 and at least one dimension has ≥ 3 values, explicitly list the matrix
- Simple binary scenarios (e.g., "logged in / not logged in") don't need a matrix

## Test Priority Assessment

### Priority Definitions

| Priority | Meaning | TDD Requirement |
|----------|---------|-----------------|
| **P0** | Core business path; feature is unusable if this fails | Must write corresponding test cases before development |
| **P1** | Important but non-blocking; affects UX or security | Should add tests within the Sprint |
| **P2** | Nice-to-have boundary coverage | Write when capacity allows |
| **P3** | Equivalent to other combinations or logically unreachable | No test needed; must explain skip reason |

### Priority Judgment Criteria

Judge each test combination's priority in the following order:

1. **Core business path**: The most common path users take in normal flow → P0
2. **Finance/security related**: Paths involving payments, permissions, data security → P0
3. **Error recovery path**: Recovery flow after user operation errors → P1
4. **Boundary value combinations**: Extreme values, empty values, max length, etc. → P1
5. **Equivalence class merging**: Multiple combinations with identical expected behavior → Keep one as P1, rest as P3
6. **Logically unreachable**: Combinations that cannot be triggered due to mutually exclusive preconditions → P3

### Complete Example (User Login Feature)

**Test Dimensions:**
- A - Login method: Phone + verification code, Email + password
- B - User status: New user, Existing, Locked
- C - Network status: Normal, Timeout

**Combination Matrix (2 x 3 x 2 = 12 combinations):**

| # | Login Method | User Status | Network | Expected Result | Priority | Priority Reason |
|---|-------------|-------------|---------|----------------|----------|-----------------|
| 1 | Phone + code | Existing | Normal | Login success, redirect to home | P0 | Core business path |
| 2 | Phone + code | New user | Normal | Auto-register and login | P0 | New user first experience |
| 3 | Phone + code | Locked | Normal | Show account locked message | P0 | Security related |
| 4 | Phone + code | Existing | Timeout | Show network error, preserve input | P1 | Error recovery path |
| 5 | Email + password | Existing | Normal | Login success, redirect to home | P0 | Core business path |
| 6 | Email + password | New user | Normal | Show user not found | P0 | Core branch |
| 7 | Email + password | Locked | Normal | Show account locked message | P0 | Security related |
| 8 | Email + password | Existing | Timeout | Show network error, preserve input | P1 | Error recovery path |
| 9 | Phone + code | New user | Timeout | Show network error | P3 | Same behavior as #4 (equivalence class) |
| 10 | Phone + code | Locked | Timeout | Show network error | P3 | Network error takes precedence over business message (equivalence class) |
| 11 | Email + password | New user | Timeout | Show network error | P3 | Same behavior as #8 (equivalence class) |
| 12 | Email + password | Locked | Timeout | Show network error | P3 | Same as #10 (equivalence class) |

**Statistics:** P0: 6 / P1: 2 / P3: 4 → TDD first batch requires at least 6 test cases (P0)

## Integration with TDD

1. **P0 rows** directly correspond to test cases that must be written — write these tests before development
2. **P1 rows** are supplemented after P0 tests pass
3. The **expected result** column in the matrix IS the `expect` assertion for test cases
4. The dimension values in the matrix ARE the **parameterized inputs** for test cases (e.g., `test.each` / `@pytest.mark.parametrize`)
