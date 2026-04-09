# A: New Project

⛔ **Path Lock**: The Mermaid flowcharts in this route are mandatory execution paths, not references. Every node must be executed in arrow order; conditional branches follow actual conditions. Do not skip any node or exit early. After completing each node, follow the arrow to the next.

---

## Plan

### First Slice (or Single-Slice Mode)

The first Slice executes the complete Plan skill chain, producing global documents (tech-stack, engineering-principles, etc.).

> **Note**: If the CLARIFY phase was already executed, requirement-qa in Plan switches to **slice mode** (only asking S1 specific functional details, not repeating macro-level questions); brainstorm defaults to **skip** (CLARIFY already covered architecture discussion), unless new architecture disputes arise within S1 that trigger it.

```mermaid
graph TB
    START["A Start<br>Slice 1 or Single Slice"] --> CLARITY{"Requirement Clarity?<br>(Slice Level)"}
    CLARITY -->|"Functional details unclear"| QA_FULL["requirement-qa<br>Slice mode - S1 details"]
    CLARITY -->|"Roughly clear"| QA_LIGHT["requirement-qa<br>Supplement S1 details"]
    CLARITY -->|"Clear"| SKIP_QA["Skip QA"]

    QA_FULL --> BRAIN_CHK
    QA_LIGHT --> BRAIN_CHK
    SKIP_QA --> BRAIN_CHK

    BRAIN_CHK{"L4+ and<br>CLARIFY not done?"}
    BRAIN_CHK -->|"Yes"| BRAIN["brainstorm<br>Multi-perspective Solutions"]
    BRAIN_CHK -->|"No"| SPEC
    BRAIN --> SPEC["spec-writing<br>Requirement Docs"]

    SPEC --> TECH["tech-stack<br>Technology Selection"]
    TECH --> ENG{"L3+?"}
    ENG -->|"Yes"| ENG_DO["engineering-principles<br>Principle Matching"]
    ENG -->|"No"| API
    ENG_DO --> API["api-contract-design<br>API Contract"]

    API --> ERR{"L3+?"}
    ERR -->|"Yes"| ERR_DO["error-handling-strategy"]
    ERR -->|"No"| ADV_CHK
    ERR_DO --> ADV_CHK{"L4+?"}

    ADV_CHK -->|"Yes"| ADV["SubAgent Parallel:<br>performance-arch-design<br>implementation-complexity-analysis<br>observability-design"]
    ADV_CHK -->|"No"| DOCS
    ADV --> DOCS["docs-output<br>Document Initialization"]
    DOCS --> GATE["Plan Gate"]

    style QA_FULL fill:#e8eaf6,stroke:#283593,color:#1a237e
    style QA_LIGHT fill:#e8eaf6,stroke:#283593,color:#1a237e
    style BRAIN fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style SPEC fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style TECH fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style ENG_DO fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style API fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style ERR_DO fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style ADV fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style DOCS fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style GATE fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
```

### Subsequent Slices (Multi-Slice Mode)

Subsequent Slices skip global skills (tech-stack, engineering-principles, error-handling-strategy), executing only slice-level incremental skills. requirement-qa is always in **slice mode**, brainstorm is **skipped** (CLARIFY already done).

```mermaid
graph TB
    START_N["A Start<br>Slice N (N > 1)"] --> CTX_READ["Read Previous Slice Outputs<br>docs/ + .cache/context.db"]
    CTX_READ --> QA_SLICE["requirement-qa<br>Slice mode - This slice details"]
    QA_SLICE --> SPEC_SLICE["spec-writing<br>This slice only - Six-section format"]
    SPEC_SLICE --> API_SLICE["api-contract-design<br>Incremental endpoints"]
    API_SLICE --> DOCS_SLICE["docs-output<br>Incremental sync"]
    DOCS_SLICE --> GATE_N["Plan Gate"]

    style START_N fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style CTX_READ fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style QA_SLICE fill:#e8eaf6,stroke:#283593,color:#1a237e
    style SPEC_SLICE fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style API_SLICE fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style DOCS_SLICE fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style GATE_N fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
```

### Variant Differences

| Skill | A-lite | A | A+ |
|-------|--------|---|-----|
| requirement-qa | Lightweight | Standard | Deep |
| brainstorm | Skip | Skip | Required if CLARIFY not done; skip if done |
| spec-writing | Bullet list | Six-section | Six-section |
| tech-stack | Default template | Full selection | Full selection |
| engineering-principles | Skip | Standard | Multi-mode matching |
| api-contract-design | Endpoint list | Full contract | Full contract |
| error-handling-strategy | Skip | Standard | Standard |
| SubAgent Triple | Skip | Skip | Parallel execution |
| docs-output | Minimal | Initialization | Full initialization |

> brainstorm is only required in A+ (L4-L5) variants when **CLARIFY phase was NOT executed**. If CLARIFY has completed architecture discussion, brainstorm in Plan is skipped.

---

## Execute

General execution flow (task decomposition -> TDD cycle -> review -> merge) -> read `references/execute.md`. Below are Route A **specialized rules**:

### First Slice

Task decomposition must follow:

| # | Mandatory Task | Description |
|---|---------|------|
| Task 1 | `code-scaffold` | Generate complete project skeleton (directory structure, build config, common modules) |
| Last | `integration-test-design` | Design integration test framework and strategy |
| Middle | This slice's module coding | Execute per task following TDD cycle |

```mermaid
graph TB
    E1["Task 1: code-scaffold<br>Complete Project Skeleton"] --> E2["Task 2..N: Module Coding<br>TDD: RED-GREEN-REFACTOR"]
    E2 --> E3["Task N+1: integration-test-design<br>Integration Test Plan"]
    E3 --> E4["Merge: Full Test Suite + Lint"]

    style E1 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style E2 fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E3 fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E4 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
```

### Subsequent Slices

- `code-scaffold` is **skipped** (skeleton already exists), Task 1 directly starts with module coding
- `integration-test-design` does incremental (only integration tests for new modules in this slice)

```mermaid
graph TB
    E1_N["Task 1..N: Add New Module<br>Coding on Existing Skeleton (TDD)"] --> E2_N["Task N+1: integration-test-design<br>Incremental Integration Tests"]
    E2_N --> E3_N["Merge: Full Test Suite + Lint"]

    style E1_N fill:#fff9c4,stroke:#f9a825,color:#e65100
    style E2_N fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E3_N fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
```
