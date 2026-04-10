# Quality Gate Detailed Rules

## Plan Gate Evaluation Flow

```mermaid
graph TB
    ENTER["Enter Plan Gate"] --> P0{"P0: Granularity Check<br>Current Slice scope manageable?"}
    P0 -->|"No: Scope too large"| FIX_SCOPE["Return to scope-sizer<br>Further split"]
    P0 -->|"Yes"| P1{"P1: User explicitly approved?"}
    P1 -->|"No"| BLOCK["Blocked<br>Await user confirmation"]
    P1 -->|"Yes"| P2{"P2: Acceptance criteria exist?<br>At least 1 verifiable criterion"}
    P2 -->|"No"| FIX_REQ["Return to requirement step<br>Add acceptance criteria"]
    P2 -->|"Yes"| P3{"P3: Scope boundary clear?<br>What to do + What not to do"}
    P3 -->|"No"| FIX_REQ2["Return to requirement step<br>Clarify scope"]
    P3 -->|"Yes"| P4{"P4: Technical approach feasible?"}
    P4 -->|"No"| FIX_DESIGN["Return to design step<br>Revise approach"]
    P4 -->|"Yes"| COND{"Conditional checks?"}

    COND -->|"Route A"| P_A{"P-A: Tech stack locked?"}
    COND -->|"Route B"| P_B{"P-B: Compatibility confirmed?"}
    COND -->|"Route C"| P_C{"P-C: Fix introduces no side effects?"}
    COND -->|"Route D"| P_D{"P-D: Each step rollbackable?"}
    COND -->|"None"| PASS

    P_A -->|"No"| FIX_TECH["Return to tech selection"]
    P_A -->|"Yes"| RISK
    P_B -->|"No"| FIX_IMPACT["Return to impact assessment"]
    P_B -->|"Yes"| RISK
    P_C -->|"No"| FIX_FIX["Return to fix approach"]
    P_C -->|"Yes"| PASS
    P_D -->|"No"| FIX_RISK["Return to risk assessment"]
    P_D -->|"Yes"| RISK

    RISK{"Route is + variant?<br>Needs risk check"}
    RISK -->|"Yes"| P_RISK{"P-R: All risks have mitigations?"}
    RISK -->|"No"| PASS
    P_RISK -->|"No"| FIX_RISK2["Return to risk assessment"]
    P_RISK -->|"Yes"| PASS["Plan Gate Passed"]

    style ENTER fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style P0 fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c,stroke-width:2px
    style FIX_SCOPE fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style BLOCK fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style FIX_REQ fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_REQ2 fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_DESIGN fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_TECH fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_IMPACT fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_FIX fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_RISK fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_RISK2 fill:#fff3e0,stroke:#e65100,color:#bf360c
    style PASS fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20,stroke-width:2px
```

### P0 Granularity Check Rules

A new first check added to the Plan gate — before user approval, determine whether the current Slice has **reasonable granularity**:

| Signal | Determination | Action |
|------|------|------|
| Current Slice involves > 3 modules | Scope too large | Return to scope-sizer for further splitting |
| Current Slice's spec docs > 5 files | Scope too large | Return to scope-sizer for further splitting |
| Current Slice estimates > 30 new files | Scope too large | Return to scope-sizer for further splitting |
| None of the above exceeded | Granularity normal | Continue to P1 |

P0 check is only performed on the first Plan gate. If already split by scope-sizer, P0 passes directly.

## Validate Gate Evaluation Flow

```mermaid
graph TB
    ENTER["Enter Validate Gate"] --> V0{"V0: Execute Completeness<br>(Standard+ variants)"}
    V0 -->|"Fail"| RF_C0["Code-level Reflux<br>Return to Execute to complete"]
    V0 -->|"Pass / lite skip"| V1{"V1: Implementation matches spec?<br>(Slice-level re-verification)"}
    V1 -->|"No"| V1_SEV{"Deviation source?"}
    V1_SEV -->|"Spec itself is wrong"| RF_R["Requirement-level Reflux"]
    V1_SEV -->|"Design approach omission"| RF_D["Design-level Reflux"]
    V1_SEV -->|"Implementation deviation"| RF_C1["Code-level Reflux"]
    V1 -->|"Yes"| V2{"V2: Core path tests pass?"}

    V2 -->|"No"| RF_C2["Code-level Reflux"]
    V2 -->|"Yes"| V3{"V3: No new lint/type errors?"}

    V3 -->|"No"| RF_C3["Code-level Reflux"]
    V3 -->|"Yes"| V_COND{"Conditional checks?"}

    V_COND -->|"Route B/C"| V4{"V4: Regression tests pass?"}
    V_COND -->|"Route D"| V5{"V5: Behavioral equivalence?"}
    V_COND -->|"None"| V_PLUS

    V4 -->|"No"| V4_SEV{"Regression failure cause?"}
    V4_SEV -->|"Approach defect"| RF_D2["Design-level Reflux"]
    V4_SEV -->|"Code issue"| RF_C4["Code-level Reflux"]
    V4 -->|"Yes"| V_PLUS{"Route is + variant?"}

    V5 -->|"No"| V5_SEV{"Equivalence failure cause?"}
    V5_SEV -->|"Refactoring approach is wrong"| RF_D3["Design-level Reflux"]
    V5_SEV -->|"Implementation error"| RF_C5["Code-level Reflux"]
    V5 -->|"Yes"| V_PLUS

    V_PLUS -->|"Yes"| V6{"V6: Edge case coverage?"}
    V_PLUS -->|"No"| PASS

    V6 -->|"No"| RF_C6["Code-level Reflux<br>Add edge case tests"]
    V6 -->|"Yes"| PASS["Validate Passed"]

    style ENTER fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style V0 fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c,stroke-width:2px
    style RF_C0 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style RF_R fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style RF_D fill:#ffe0b2,stroke:#e65100,color:#bf360c
    style RF_D2 fill:#ffe0b2,stroke:#e65100,color:#bf360c
    style RF_D3 fill:#ffe0b2,stroke:#e65100,color:#bf360c
    style RF_C1 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style RF_C2 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style RF_C3 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style RF_C4 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style RF_C5 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style RF_C6 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style PASS fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20,stroke-width:2px
```

### V0 Execute Completeness Check

V0 is Validate's first check — verifying Execute phase **process quality** rather than just final results.

| Variant | V0 Check Content | Fail Action |
|------|-----------|----------|
| **lite / fast** | **Skip** V0, go directly to V1 | — |
| **Standard** | Every task completed TDD cycle (has test coverage); full test suite passes | Return to Execute to add tests |
| **+ variant** | Every task passed two-stage review (spec compliance + code quality); no tasks in BLOCKED/NEEDS_CONTEXT state | Return to Execute to complete review or resolve blockers |

V0 checks Execute process **completeness**, not code correctness (that's V1-V3's responsibility). If V0 fails, it means Execute phase had steps skipped that need to be completed.

### V1 Notes (Enhanced)

After integration, V1 serves as **Slice-level Spec compliance re-verification**. Differences from task-level Spec compliance review in Execute:

| Dimension | Execute Task Review | Validate V1 |
|------|-----------------|-------------|
| Granularity | Single task vs its corresponding spec fragment | All tasks in the entire Slice combined vs complete spec |
| Perspective | Local correctness | Global consistency — inter-task connections, omissions, conflicts |
| Scope | Within task | After cross-task integration |

## Reflux Level Determination

```mermaid
graph TB
    FAIL["Validate Failed<br>Has reflux items"] --> COUNT{"Same issue<br>refluxed how many times?"}
    COUNT -->|">= 2 times"| HUMAN["Pause<br>Request user intervention"]
    COUNT -->|"< 2 times"| LEVEL{"Highest reflux level?"}

    LEVEL -->|"Scope-level"| SNAP_S["Intermediate Snapshot<br>Persist confirmed artifacts"]
    SNAP_S --> ACT_S["Return to scope-sizer<br>Re-split Slice<br>Current Slice too large to pass in one attempt"]
    LEVEL -->|"Requirement-level"| SNAP_R["Intermediate Snapshot<br>Archive decisions"]
    SNAP_R --> ACT_R["Return to Plan requirement step<br>Redo QA or rewrite spec<br>Re-run full Plan then Execute then Validate"]
    LEVEL -->|"Design-level"| ACT_D["Return to Plan design step<br>Revise approach<br>Re-pass Plan gate then Execute then Validate"]
    LEVEL -->|"Code-level"| ACT_C["Return to Execute<br>Fix code<br>Re-pass Validate"]

    style FAIL fill:#f5f5f5,stroke:#616161,color:#212121
    style HUMAN fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c,stroke-width:2px
    style SNAP_S fill:#fff9c4,stroke:#f9a825,color:#e65100,stroke-width:2px
    style SNAP_R fill:#fff9c4,stroke:#f9a825,color:#e65100,stroke-width:2px
    style ACT_S fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style ACT_R fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style ACT_D fill:#ffe0b2,stroke:#e65100,color:#bf360c
    style ACT_C fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
```

### Scope-Level Reflux Trigger Conditions

When the Validate phase discovers the following, scope-level reflux is triggered:
- During Execute, the actual modules or files involved in the current Slice far exceed expectations
- Test coverage scope is too large to complete in reasonable time
- Code generation volume exceeds context window capacity

After scope-level reflux, return to scope-sizer to further split the current Slice into smaller sub-Slices.

---

## Reflux Intermediate Snapshots (Mandatory)

When **scope-level** or **requirement-level** reflux is triggered, an intermediate snapshot must be output before jumping to the reflux target. This is part of the reflux action, not a separate step — the model directly attaches the snapshot when outputting reflux conclusions.

**Design-level** and **code-level** reflux have small impact scope and don't need snapshots.

### Trigger Rules

| Reflux Level | Snapshot Required | Reason |
|---------|---------|------|
| Scope-level | **Yes (mandatory)** | Current Slice will be split; completed partial outputs must be persisted, otherwise sub-Slices cannot perceive them |
| Requirement-level | **Yes (mandatory)** | Requirements may be overturned; previous design decisions need archiving for comparison |
| Design-level | No | Only revising approach; spec changes are covered when Plan is redone |
| Code-level | No | Only fixing code; no document/context changes |

### Snapshot Output Format

Directly attached after reflux conclusion, as part of the reflux output template:

```markdown
### Reflux Intermediate Snapshot

**Current Slice**: S2 — Core Domain
**Reflux Level**: Scope-level / Requirement-level
**Trigger Reason**: [Specific reason]

#### Confirmed Artifacts (Need Persistence)
| Artifact | Target Path | Status |
|--------|---------|------|
| Tech stack document | docs/tech-stack.md | Synced |
| S1 API contract | docs/api/auth.md | Synced |
| S2 requirement spec | docs/novel/spec.md | Needs writing |

#### Decisions to Persist
- [Decision 1]: ...
- [Decision 2]: ...

#### Actions
1. Write the files marked as needing writing above
2. Update .cache/context.db (incremental sync of involved modules)
3. Update docs/progress/ status (mark current Slice as "in reflux")
4. Jump to [reflux target]
```

### Snapshot Execution Method

- **No SubAgent dispatch**: Main agent writes files directly, reducing overhead
- **Only write changed parts**: No full sync, only write "confirmed but not yet persisted" artifacts
- **After snapshot completes**: Then execute reflux jump

---

## Gate Output Format

Output after each gate check:

```markdown
### Pass / Fail [Plan / Validate] Gate Check

| # | Check Item | Result | Notes |
|---|--------|------|------|
| P0 | Granularity check | Pass | Slice scope: 2 modules - 4 feature points |
| P1 | User approval | Pass | User replied "confirmed" |
| P2 | Acceptance criteria | Pass | 3 acceptance criteria |
| P3 | Scope boundary | Fail | Did not specify "what not to do" |
| P4 | Technical feasibility | Pass | — |

**Conclusion**: Fail
**Failure Reason**: P3 — Scope boundary unclear
**Recommended Action**: Return to requirement step, add "out of scope" list
**Reflux Target**: Plan -> Requirement QA
```

---

## ⛔ Phase Chain Guard Integration

After outputting the gate check result, you **must** call `phase_guard.py gate` to record it. This is the mechanical evidence chain and must not be skipped.

### After Plan Gate Pass

```bash
python3 skills/project-context/scripts/phase_guard.py gate \
  --root . --slice <SN> --phase plan --result pass \
  --outputs '[{"path":"docs/plan.md"},{"path":"docs/spec.md"}]'
```

### After Plan Gate Fail

```bash
python3 skills/project-context/scripts/phase_guard.py gate \
  --root . --slice <SN> --phase plan --result fail
```

### After Validate Gate Pass

```bash
python3 skills/project-context/scripts/phase_guard.py gate \
  --root . --slice <SN> --phase validate --result pass
```

### After Validate Gate Fail (triggers reflux)

```bash
python3 skills/project-context/scripts/phase_guard.py gate \
  --root . --slice <SN> --phase validate --result fail
```

After reflux repair, re-entering the corresponding phase via `phase_guard.py enter` will proceed normally (it checks the **prior** phase's gate-pass, not the current phase).
