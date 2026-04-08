# Deliver Phase

After passing the Validate gate, enter Deliver. This phase includes **three mandatory steps** that cannot be skipped for any path. **Every Slice's Deliver performs a complete sync** — not just the final Slice. Intermediate Slices must also sync to ensure outputs are persistable and recoverable across sessions.

```mermaid
graph TB
    DELIVER_IN["Validate Gate Passed"] --> PARALLEL["SubAgent Parallel"]
    PARALLEL --> DOCS_FINAL["docs-output<br>Document Sync"]
    PARALLEL --> CTX_SYNC["project-context<br>Project State Writeback"]
    DOCS_FINAL --> JOIN["Join"]
    CTX_SYNC --> JOIN
    JOIN --> RECONCILE["Reconcile Audit<br>Mechanical Comparison / Gap-fill"]
    RECONCILE --> SLICE_CHK{"Multi-Slice Mode?"}
    SLICE_CHK -->|"Yes"| SLICE_SUM["Output Slice Delivery Summary<br>+ Update Slice Progress"]
    SLICE_CHK -->|"No"| FINAL_SUM["Output Final Delivery Summary"]
    SLICE_SUM --> NEXT{"More Slices?"}
    NEXT -->|"Yes"| PAUSE{"User Choice<br>Continue / Pause"}
    NEXT -->|"No"| FINAL_SUM
    PAUSE -->|"Continue"| LOOP["Enter Next Slice"]
    PAUSE -->|"Pause"| SAVE["Save Progress<br>Resume from This Slice Next Time"]
    FINAL_SUM --> DONE["Deliver Complete"]

    style DELIVER_IN fill:#f5f5f5,stroke:#616161,color:#212121
    style PARALLEL fill:#fff3e0,stroke:#e65100,color:#bf360c
    style DOCS_FINAL fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style CTX_SYNC fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style JOIN fill:#fff3e0,stroke:#e65100,color:#bf360c
    style RECONCILE fill:#fff9c4,stroke:#f9a825,color:#e65100,stroke-width:2px
    style SLICE_SUM fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style FINAL_SUM fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style DONE fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20,stroke-width:2px
    style PAUSE fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
    style SAVE fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
```

## docs-output (Mandatory)

- Sync all documents produced by this Slice iteration to the docs/ directory
- Includes: requirement docs, design docs, API contracts, test plans, etc.
- For Route A's first Slice, docs were initialized during Plan phase; this is the final-state update
- Subsequent Slices / B/C/D routes do incremental sync

## project-context (Mandatory)

- Write back key information from this Slice iteration to project context
- Includes: new modules, changed files, new technical decisions, known issues
- Ensures next conversation or next Slice can correctly perceive current project state

## Reconcile Audit (Mandatory)

After SubAgent parallel sync completes, before outputting delivery summary, perform a **mechanical comparison**. Don't rely on model memory — use comparison checklists to discover omissions.

### Reconcile Rules

| Comparison Dimension | Left Side (Plan/Execute Output List) | Right Side (Actual On-disk State) | Gap Handling |
|---------|------|------|---------|
| **Document Completeness** | Spec/design/API file list from Plan phase | Actual files in `docs/` directory | Missing -> write immediately |
| **Context Consistency** | Module/file list from Execute | Modules recorded in `.cache/context.db` | Missing -> incremental sync |
| **Decision Traceability** | Technical decisions made in this Slice | Corresponding decision records in `docs/` | Missing -> append to module docs |

### Reconcile Output Format

```markdown
### Reconcile Audit

| # | Dimension | Result | Notes |
|---|------|------|------|
| R1 | Document Completeness | Pass | Plan produced 4 files, all exist in docs/ |
| R2 | Context Consistency | Warning | Execute added user module, not in context.db -> synced |
| R3 | Decision Traceability | Pass | 2 technical decisions both recorded |

**Gap-fill Action**: Incrementally synced user module to context.db
```

### Execution Method

- **Main agent executes directly**, no SubAgent dispatch (comparison + gap-fill is lightweight)
- Gaps are directly written/synced, no backflow needed
- Reconcile must complete before entering delivery summary

## Slice Delivery Summary (Multi-Slice Mode)

After each Slice completes, output:
- What this Slice accomplished (scope)
- Which files/modules changed
- Preview of next Slice scope
- Whether to continue to next Slice or pause

## Final Delivery Summary

After all Slices complete (or single-Slice mode), output:
- What was accomplished (scope)
- Which files/modules changed
- Remaining issues or follow-up TODOs
- Next step recommendations

## Slice Progress Persistence

In multi-Slice mode, each Slice's Deliver also writes Slice progress to docs/progress/:

```markdown
## Slice Progress

| Slice | Status | Completion Time | Scope |
|-------|------|---------|------|
| S1 | Done | 2026-04-08 | Infrastructure + Auth |
| S2 | In Progress | - | Core Domain: Novel Management |
| S3 | Pending | - | Supporting Domain: User + Bookshelf |
| S4 | Pending | - | Integration: Search + Recommendations |
```

On next session resume, read this table to locate the continuation point.
