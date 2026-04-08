# Execute Phase Detailed Rules

After passing the Plan gate, enter Execute. This phase transforms Plan outputs (spec + API contract + design docs) into **runnable code**, completed through three layers: task decomposition -> TDD-driven task loop -> merge.

```mermaid
graph TB
    PLAN_PASS["Plan Gate Passed"] --> DECOMPOSE["Task Decomposition"]
    DECOMPOSE --> TASK_LOOP["Task Loop"]
    TASK_LOOP --> TASK{"Get Next Task"}
    TASK --> TDD["TDD Execution<br>RED - GREEN - REFACTOR"]
    TDD --> REVIEW{"Task Review<br>(By Variant)"}
    REVIEW -->|"Pass"| COMMIT["Task Complete<br>Commit Point"]
    REVIEW -->|"Fail"| TDD
    COMMIT --> MORE{"More Tasks?"}
    MORE -->|"Yes"| TASK
    MORE -->|"No"| MERGE["Merge<br>Full Test Suite + Lint"]
    MERGE --> VALIDATE["Enter Validate Gate"]

    style PLAN_PASS fill:#f5f5f5,stroke:#616161,color:#212121
    style DECOMPOSE fill:#e8eaf6,stroke:#283593,color:#1a237e,stroke-width:2px
    style TASK_LOOP fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style TDD fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20,stroke-width:2px
    style REVIEW fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
    style COMMIT fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style MERGE fill:#e3f2fd,stroke:#1565c0,color:#0d47a1,stroke-width:2px
    style VALIDATE fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
```

---

## 1. Task Decomposition

Transform Plan outputs into an ordered list of atomic tasks. This is the **bridge** from Plan (design layer) to Execute (code layer).

### Decomposition Principles

| Principle | Description |
|------|------|
| **Atomicity** | Each task focuses on a single concern: one function, one endpoint, one component |
| **Verifiable** | Each task has a clear verification method (test command / type check / manual verification) |
| **Ordered** | Tasks have explicit dependencies: infrastructure -> data layer -> service layer -> interface layer -> UI |
| **TDD-friendly** | Each task writes tests before implementation (tests and implementation can be in the same task) |

### Task Format

```markdown
### Task N: [Task Name]

**Goal**: [One-sentence description]
**Files**: [Precise file paths]
  - `src/domain/novel/Novel.java` — New
  - `src/domain/novel/NovelRepository.java` — New
  - `test/domain/novel/NovelTest.java` — New
**Dependencies**: Task N-1 (or none)
**Verification**: `mvn test -pl novel-domain` passes, 0 errors

#### Steps
1. Create `NovelTest.java`, write 3 test cases (RED)
2. Create `Novel.java` entity class, implement logic to make tests pass (GREEN)
3. Create `NovelRepository.java` interface
4. Review code, eliminate duplication (REFACTOR)
```

### Variant Differences

| Variant | Task Decomposition Method | Notes |
|------|------------|---------|
| **lite / fast** | **No decomposition**, main agent codes directly per Plan | Hot fix, simple features don't need splitting |
| **Standard** | **Decompose by module/feature**, each task may involve 2-5 files | Single task granularity ~5-10 minutes |
| **+ variant** | **Strict decomposition by concern**, each task focuses on a single concern | Single task granularity ~2-5 minutes, includes complete code |

---

## 2. TDD-Driven Task Execution

All standard and above variants enforce TDD. TDD is not "write tests after coding" — it's **test-first**.

### TDD Cycle

```mermaid
graph LR
    RED["RED<br>Write Failing Test<br>Define Expected Behavior"] --> GREEN["GREEN<br>Write Minimal Code<br>Make Test Pass"]
    GREEN --> REFACTOR["REFACTOR<br>Clean Up Code<br>Keep Tests Green"]
    REFACTOR --> CHECK{"Tests Still Green?"}
    CHECK -->|"Yes"| DONE["Task Complete"]
    CHECK -->|"No"| GREEN

    style RED fill:#ffcdd2,stroke:#c62828,color:#b71c1c,stroke-width:2px
    style GREEN fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20,stroke-width:2px
    style REFACTOR fill:#e3f2fd,stroke:#1565c0,color:#0d47a1,stroke-width:2px
    style DONE fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
```

### RED Phase Rules

- Write tests first, describing **expected behavior** rather than implementation details
- Tests must **currently fail** (compilation error or assertion failure)
- Write only one test scenario at a time, don't write all cases at once

### GREEN Phase Rules

- Write the **minimum code** to make the test pass
- Don't pursue elegance, only correctness
- No premature optimization, no features not required by tests (YAGNI)

### REFACTOR Phase Rules

- Eliminate duplicate code (DRY)
- Improve naming and structure
- Run tests immediately after each refactoring to confirm green
- Refactoring does not change external behavior

### Variant Differences

| Variant | TDD Requirement |
|------|---------|
| **lite / fast** | **Optional** — main agent decides whether to write tests first |
| **Standard** | **Mandatory** — every task must follow RED->GREEN->REFACTOR |
| **+ variant** | **Strict** — each test scenario gets its own RED->GREEN round, no batching |

---

## 3. Execution Mode: Main Agent vs SubAgent

Select execution mode based on variant. The core difference is **context isolation**.

### Main Agent Execution (lite / fast / standard)

```mermaid
graph TB
    MAIN["Main Agent"] --> T1["Task 1"]
    T1 --> T2["Task 2"]
    T2 --> T3["Task N"]
    T3 --> DONE["Merge"]

    style MAIN fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
```

- Main agent executes tasks in order
- Shared context, previous task's code is visible to the next task
- Can directly reference spec and preceding code when issues arise
- **Suitable for**: tightly coupled tasks requiring frequent context reference

### SubAgent Isolated Execution (+ variant)

```mermaid
graph TB
    CTRL["Main Agent<br>= Controller"] --> DISPATCH["Dispatch Tasks"]
    DISPATCH --> SA1["SubAgent 1<br>Task 1"]
    SA1 -->|"Done/Failed"| CTRL2["Main Agent Review"]
    CTRL2 --> SA2["SubAgent 2<br>Task 2"]
    SA2 -->|"Done/Failed"| CTRL3["Main Agent Review"]
    CTRL3 --> SA3["SubAgent N<br>Task N"]
    SA3 -->|"Done/Failed"| FINAL["Merge"]

    style CTRL fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c,stroke-width:2px
    style SA1 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style SA2 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style SA3 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style CTRL2 fill:#fff3e0,stroke:#e65100,color:#bf360c
    style CTRL3 fill:#fff3e0,stroke:#e65100,color:#bf360c
```

- Each task is executed by a **fresh SubAgent** to avoid context pollution
- SubAgent input package (precisely controlled):
  - Task description (from task decomposition)
  - Involved file contents (current version)
  - Spec summary (portions relevant to this task)
  - Predecessor task output summary (if any)
- **SubAgent does NOT receive**: complete Plan output, other tasks' code, session history
- **Suitable for**: relatively independent tasks requiring protection from attention drift

### SubAgent Status Reports

After completion, SubAgent reports status to Controller:

| Status | Meaning | Controller Action |
|------|------|----------------|
| **DONE** | Task complete, tests pass | Proceed to review |
| **DONE_WITH_CONCERNS** | Task complete, but has concerns | Focus review on concern areas |
| **NEEDS_CONTEXT** | Missing information, cannot complete | Re-dispatch with supplementary context |
| **BLOCKED** | Blocked by prerequisite dependency | Adjust task order or resolve blocker first |

---

## 4. Task Review

After each task completes, review is performed before moving to the next task. Review depth increases by variant.

### Quick Self-check (lite / fast)

Main agent does a quick check after coding:
- [ ] Code compiles, no new lint/type errors
- [ ] Core logic matches spec
- No formal review process needed

### Standard Self-check (standard variant)

Main agent does after each task:
- [ ] TDD three phases complete: test-first -> implementation passes -> refactoring done
- [ ] Code matches spec (interface signatures, data models, behavior logic)
- [ ] No new lint/type errors
- [ ] New code doesn't break existing tests

### Two-stage SubAgent Review (+ variant)

```mermaid
graph TB
    TASK_DONE["SubAgent Task Complete"] --> STAGE1["Stage 1: Spec Compliance Review"]
    STAGE1 --> S1_CHK{"Compliant?"}
    S1_CHK -->|"No"| S1_FIX["SubAgent Fix<br>+ Re-review"]
    S1_FIX --> STAGE1
    S1_CHK -->|"Yes"| STAGE2["Stage 2: Code Quality Review"]
    STAGE2 --> S2_CHK{"Qualified?"}
    S2_CHK -->|"No"| S2_FIX["SubAgent Fix<br>+ Re-review"]
    S2_FIX --> STAGE2
    S2_CHK -->|"Yes"| PASS["Review Passed"]

    style STAGE1 fill:#e8eaf6,stroke:#283593,color:#1a237e,stroke-width:2px
    style STAGE2 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20,stroke-width:2px
    style S1_FIX fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style S2_FIX fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style PASS fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20,stroke-width:2px
```

**Stage 1: Spec Compliance Review**

Executed by the Main Agent (Controller), comparing:

| Check Dimension | Comparison Target |
|---------|---------|
| Interface signatures | API contract docs vs actual code |
| Data models | Domain model design vs actual entity classes |
| Behavior logic | Business rules in spec vs actual implementation |
| Error handling | error-handling-strategy vs actual exception handling |

Fail -> SubAgent fixes -> re-review. **Max 2 fix rounds per task**; if still failing, escalate to Validate phase.

**Stage 2: Code Quality Review**

Executed after Stage 1 passes:

| Check Dimension | Focus Areas |
|---------|--------|
| Security | OWASP Top 10, input validation, output encoding |
| Readability | Naming, function length, complexity |
| DRY | Any duplicate code |
| YAGNI | Any code beyond requirements |
| Test quality | Tests cover behavior (not implementation), sufficient coverage |

Fail -> SubAgent fixes -> re-review. Also max 2 rounds.

---

## 5. Merge

After all tasks complete, run full verification:

```mermaid
graph TB
    ALL_TASKS["All Tasks Complete"] --> FULL_TEST["Full Test Suite<br>Unit + Integration"]
    FULL_TEST --> LINT["Full Lint + Type Check"]
    LINT --> TYPE_CHK{"All Pass?"}
    TYPE_CHK -->|"Yes"| VALIDATE["Enter Validate Gate"]
    TYPE_CHK -->|"No"| DIAG["Diagnose Failure"]
    DIAG --> FIX["Fix<br>(May need to return to a specific Task)"]
    FIX --> FULL_TEST

    style ALL_TASKS fill:#f5f5f5,stroke:#616161,color:#212121
    style FULL_TEST fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20,stroke-width:2px
    style LINT fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style VALIDATE fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
```

The merge phase checks overall health after task integration:
- Whether tasks that passed individually still pass when combined
- Whether there are missing integration points (inter-module calls, event propagation, etc.)
- Full lint/type check with no new errors

---

## 6. Route-Specific Rules

Execute has special behaviors on different routes. Detailed rules are defined in corresponding `route-{x}.md` files.

**General principle**: This file (execute.md) defines **common mechanisms** for TDD, task decomposition, review, etc. Each route-{x}.md's Execute section defines **route-specific rules** (e.g., scaffold timing, regression test strategy, behavioral equivalence constraints). They complement each other; route files take precedence.

---

## 7. Model Selection Recommendations (Optional)

If the execution environment supports multi-model switching (e.g., SubAgent can specify a model), select by task type:

| Task Type | Recommended Model | Examples |
|---------|---------|------|
| **Mechanical** | Fast/economic model | Boilerplate code, CRUD endpoints, config files, repetitive pattern code |
| **Integration** | Standard model | Cross-module calls, middleware integration, database migration scripts |
| **Architectural** | Strongest model | New pattern introduction, complex state management, performance-critical paths, security-sensitive code |

If the environment doesn't support model switching, ignore this section and use the current model uniformly.

---

## Summary: Variant Strategy Quick Reference

| Dimension | lite / fast | Standard | + variant |
|------|-----------|------|--------|
| **Task decomposition** | No decomposition | By module/feature | Strict by concern |
| **TDD** | Optional | Mandatory | Strict (per scenario) |
| **Execution mode** | Main agent codes directly | Main agent executes by task | SubAgent isolated execution |
| **Task review** | Quick self-check | Standard self-check | Two-stage SubAgent review |
| **Model selection** | N/A | N/A | Select by task type |
| **Merge** | Manual confirmation | Full test + lint | Full test + lint + integration verification |
