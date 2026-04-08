# C: Bug Fix

## Plan

```mermaid
graph TB
    START["C Start"] --> CTX["project-context<br>Locate Error Module"]
    CTX --> FAST{"L1-L2?"}
    FAST -->|"Yes"| MERGE["Diagnose + Fix Plan<br>Combined Steps"]
    FAST -->|"No"| REPRO{"Reproduced?"}

    REPRO -->|"No"| DO_REPRO["Reproduce Issue"]
    REPRO -->|"Yes"| ROOT
    DO_REPRO --> ROOT["Root Cause Analysis<br>Locate Specific Code"]

    ROOT --> IMPACT_CHK{"L3+?"}
    IMPACT_CHK -->|"Yes"| IMPACT["Impact Assessment<br>Fix Side-effect Scope"]
    IMPACT_CHK -->|"No"| FIX
    IMPACT --> FIX["Fix Plan"]

    MERGE --> GATE["Plan Gate"]
    FIX --> GATE

    style CTX fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style ROOT fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style IMPACT fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style MERGE fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style GATE fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
```

### Variant Differences

| Step | C-fast | C | C+ |
|------|--------|---|-----|
| project-context | Locate module | Locate module | Locate module |
| Reproduction | Skip (quick diagnose) | Standard reproduction | Standard reproduction |
| Root cause analysis | Combined into diagnosis | Standard | Deep |
| Impact assessment | Skip | Skip | Required |
| Fix plan | Combined into diagnosis | Standard | Detailed |

---

## Execute

General execution flow -> read `references/execute.md`. Route C **specialized rules**:

- **No scaffold** — Bug fixes don't need project/module scaffolding
- **Regression testing mandatory** — Confirm fix doesn't introduce new issues

| Variant | Execute Strategy | TDD |
|------|------------|-----|
| **C-fast** | Skip task decomposition, main agent directly: diagnose -> fix -> regression test | Optional |
| **C** | Decompose fix plan into 1-3 tasks, execute via TDD flow | Mandatory |
| **C+** | Standard task decomposition + SubAgent isolation + two-stage review | Strict |

```mermaid
graph TB
    E1["Code Fix Per Plan<br>(TDD: Write Regression Test First)"] --> E2["Regression Testing<br>+ Affected Module Tests"]
    E2 --> E3["Merge: Full Test Suite Confirmation"]

    style E1 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style E2 fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style E3 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
```
