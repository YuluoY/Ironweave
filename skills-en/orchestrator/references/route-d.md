# D: Refactoring

## Plan

> **Note**: If the CLARIFY phase already covered architecture discussion, brainstorm in Plan defaults to **skip** unless new strategy disputes arise during refactoring.

```mermaid
graph TB
    START["D Start"] --> CTX["project-context<br>Read Architecture Overview"]
    CTX --> ASSESS["Current State Assessment<br>Problem Identification + Impact Scope"]

    ASSESS --> BRAIN_CHK{"L4+ and<br>CLARIFY not done?"}
    BRAIN_CHK -->|"Yes"| BRAIN["brainstorm<br>Evaluate Refactoring Strategy"]
    BRAIN_CHK -->|"No"| PLAN_REF
    BRAIN --> PLAN_REF["Refactoring Plan<br>Target Architecture + Migration Path"]

    PLAN_REF --> ENG{"L3+?"}
    ENG -->|"Yes"| ENG_DO["engineering-principles<br>Verify Plan Compliance"]
    ENG -->|"No"| RISK
    ENG_DO --> PERF_CHK{"L4+?"}
    PERF_CHK -->|"Yes"| PERF["performance-arch-design<br>Performance Redesign"]
    PERF_CHK -->|"No"| RISK
    PERF --> RISK["Risk Assessment<br>Regression Risk + Rollback Capability"]

    RISK --> DOCS_CHK{"L3+?"}
    DOCS_CHK -->|"Yes"| DOCS["docs-output<br>Incremental Sync"]
    DOCS_CHK -->|"No"| GATE
    DOCS --> GATE["Plan Gate"]

    style CTX fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style ASSESS fill:#fff3e0,stroke:#e65100,color:#bf360c
    style BRAIN fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style PLAN_REF fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style ENG_DO fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style PERF fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style RISK fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style DOCS fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style GATE fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
```

### Variant Differences

| Skill | D-lite | D | D+ |
|-------|--------|---|-----|
| project-context | Read architecture | Read architecture | Read architecture |
| Current state assessment | Quick | Standard | Deep |
| brainstorm | Skip | Skip | Required if CLARIFY not done; skip if done |
| Refactoring plan | Brief | Standard | Detailed + migration plan |
| engineering-principles | Skip | Standard verification | Deep verification |
| performance-arch-design | Skip | Skip | Performance redesign |
| Risk assessment | Skip | Standard | Detailed + rollback plan |
| docs-output | Skip | Incremental sync | Incremental sync |

---

## Execute

General execution flow (task decomposition -> TDD cycle -> review -> merge) -> read `references/execute.md`. Route D **specialized rules**:

- **No scaffold** — Refactoring doesn't create new project/module scaffolding
- **Core principle**: After each task completes, **all existing tests must pass** (behavioral equivalence)
- `integration-test-design` **only triggered for cross-layer refactoring**
- **No accumulation**: Don't wait for multiple tasks to finish before testing collectively — verify equivalence immediately after each task

```mermaid
graph TB
    E1["Task 1..N: Step-by-step Code Per Plan<br>TDD + Behavioral Equivalence Verification Each Step"] --> E2{"Cross-layer Changes?"}
    E2 -->|"Yes"| E3["Task N+1: integration-test-design<br>Migration Verification Tests"]
    E2 -->|"No"| E4["Merge: Full Test Suite<br>Confirm Behavioral Equivalence"]
    E3 --> E4

    style E1 fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E3 fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E4 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
```
