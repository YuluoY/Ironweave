# B: New Feature for Existing Project

## Plan

> **Note**: If the CLARIFY phase was already executed, requirement-qa in Plan switches to **slice mode** (only asking about current slice's functional details and impact scope, not repeating macro-level questions); brainstorm defaults to **skip** (CLARIFY already covered architecture discussion), unless new implementation approach disputes arise within the slice that trigger it.

```mermaid
graph TB
    START["B Start"] --> CTX["project-context<br>Read Existing Architecture"]
    CTX --> CLARITY{"Requirement Clarity?<br>(Slice Level)"}
    CLARITY -->|"Vague"| QA["requirement-qa<br>Focus on Feature Boundaries"]
    CLARITY -->|"Semi-clear"| QA_C["requirement-qa<br>Clarify Constraints"]
    CLARITY -->|"Clear"| SKIP_QA["Skip QA"]

    QA --> BRAIN_CHK
    QA_C --> BRAIN_CHK
    SKIP_QA --> BRAIN_CHK

    BRAIN_CHK{"L4+ and<br>CLARIFY not done?"}
    BRAIN_CHK -->|"Yes"| BRAIN["brainstorm<br>Evaluate Implementation Approaches"]
    BRAIN_CHK -->|"No"| IMPACT
    BRAIN --> IMPACT["Impact Assessment<br>Compatibility + Regression Scope"]

    IMPACT --> SPEC["spec-writing<br>Incremental Requirement Docs"]
    SPEC --> API_CHK{"New APIs Involved?"}
    API_CHK -->|"Yes"| API["api-contract-design<br>Incremental Contract"]
    API_CHK -->|"No"| ENG_CHK
    API --> ENG_CHK{"Architecture Changes?"}
    ENG_CHK -->|"Yes"| ENG["engineering-principles"]
    ENG_CHK -->|"No"| ERR_CHK
    ENG --> ERR_CHK{"L4+?"}
    ERR_CHK -->|"Yes"| ERR["error-handling-strategy"]
    ERR_CHK -->|"No"| DOCS
    ERR --> DOCS["docs-output<br>Incremental Sync"]
    DOCS --> GATE["Plan Gate"]

    style CTX fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style QA fill:#e8eaf6,stroke:#283593,color:#1a237e
    style QA_C fill:#e8eaf6,stroke:#283593,color:#1a237e
    style BRAIN fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style IMPACT fill:#fff3e0,stroke:#e65100,color:#bf360c
    style SPEC fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style API fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style ENG fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style ERR fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style DOCS fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style GATE fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
```

### Variant Differences

| Skill | B-lite | B | B+ |
|-------|--------|---|-----|
| project-context | Read | Read | Read |
| requirement-qa | Quick clarification | Standard | Deep |
| brainstorm | Skip | Skip | Required if CLARIFY not done; skip if done |
| Impact assessment | Skip | Standard | Deep |
| spec-writing | Incremental | Incremental | Incremental |
| api-contract-design | As needed | As needed | As needed |
| engineering-principles | Skip | As needed | As needed |
| error-handling-strategy | Skip | Skip | Standard |
| docs-output | Skip | Incremental sync | Incremental sync |

---

## Execute

General execution flow (task decomposition -> TDD cycle -> review -> merge) -> read `references/execute.md`. Below are Route B **specialized rules**:

| Condition | Task Decomposition Special Handling |
|------|----------------|
| **New module** | Task 1 = `code-scaffold` for that module (module-level, not project-level) |
| **Cross-module integration** | Must include `integration-test-design` incremental task |
| **Single module internal** | No special requirements, follow standard TDD flow |

```mermaid
graph TB
    E1{"New Module?"}
    E1 -->|"Yes"| E2["Task 1: code-scaffold<br>Module Skeleton"]
    E1 -->|"No"| E3["Task 1..N: Feature Coding<br>TDD: RED-GREEN-REFACTOR"]
    E2 --> E3
    E3 --> E4{"Cross-module Integration?"}
    E4 -->|"Yes"| E5["Task N+1: integration-test-design<br>Incremental Integration Tests"]
    E4 -->|"No"| E6["Merge: Full Test Suite + Lint"]
    E5 --> E6

    style E2 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style E3 fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E5 fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E6 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
```
