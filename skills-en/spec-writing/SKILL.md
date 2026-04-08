---
name: spec-writing
description: >-
  Write and revise modular requirement/feature documents, output to the specs/ directory. Each feature document contains a six-section structure: Feature Overview, User Stories, Requirement Description, Technical Requirements, Constraints, and Test Criteria. All structural diagrams exclusively use Mermaid (flowchart, sequenceDiagram, erDiagram, etc.). Monorepo defaults to apps/ + packages/ layout.
  Use this skill when: the user mentions requirement documents, PRD, product requirements, feature documents, specs, user stories, acceptance criteria, feature requirements, requirement analysis, business requirements, functional requirements, requirement specifications, requirement review, requirement changes, feature decomposition, or asks to write/revise/review detailed feature descriptions, even without explicitly saying "requirement document". Not applicable for pure tech stack selection documents.
---

# Requirement Documents (Specs)

This Skill is responsible for **writing and revising requirement documents** — from a one-liner to structured, deliverable feature documentation. The core problem it solves: transforming requirement expression from vague verbal communication into trackable, reviewable, acceptance-ready standardized documents.

**Not** responsible for standalone tech stack selection documents. **Does not** replace UI visual design mockups, but all structural information must be expressed using **Mermaid** because Mermaid supports version control, collaborative editing, and Markdown embedding.

## Principles

- **Modular**: Split directories by system module; within modules, **each page or feature point gets its own file**, avoiding overly long single files. Benefits: clear responsibility boundaries per file, teams can write in parallel, review and changes only need to focus on affected files.
- **Structured**: Each feature document must contain the following **six sections**, no exceptions. The six-section structure ensures a closed loop from "what to do" to "how to verify", preventing omissions.
- **Monorepo context**: When requirements involve repo layout, default to **`apps/`** for business apps and **`packages/`** for reusable packages; defer to user/repo instructions when they differ.

## Diagrams (Only Drawing Language: Mermaid)

For any **visualization** in requirement documents, **use Mermaid exclusively**. Mermaid is plain text — Git-manageable, diffable, PR-reviewable.

Common types: `graph TD/LR` (module/architecture), `flowchart` (flow/state), `sequenceDiagram` (sequence), `erDiagram` (entity relationship). Embed in ` ```mermaid ` code blocks.

> **When to draw**: >= 2 actors interacting -> sequence diagram; >= 3 branching steps -> flowchart; new/changed entities -> ER diagram; module dependencies -> module diagram.
>
> Detailed type tables, usage guide, and examples → `references/mermaid-guide.md`

## Suggested Directory Example

```
specs/
+-- auth/
|   +-- login.md
|   +-- register.md
+-- user/
|   +-- profile.md
|   +-- settings.md
+-- dashboard/
    +-- overview.md
```

## Six-Section Feature Document Structure

1. **Feature Overview**
   One or two sentences describing the goal and business value: what it does, why it matters, with clear scope. A good overview lets someone unfamiliar with the project understand the feature's significance in 10 seconds.

2. **User Stories**
   Format: `As a [user role], I want to [accomplish something], so that [I gain some value].`
   Can have multiple entries covering different roles or scenarios.

   **Examples**:
   - As a **regular user**, I want to log in via phone number + SMS code, so that I can quickly access the system without memorizing passwords.
   - As an **admin**, I want to view login failure logs, so that I can promptly detect abnormal access behavior.

3. **Requirement Description** (Structured)
   - **Input**: Data, trigger conditions
   - **Output**: Results, UI changes
   - **Interaction Flow**: Steps and state transitions (**complex flows must include flowchart or sequence diagram**)
   - **UI Requirements**: Layout, component forms, copy; empty state / loading state / error state

4. **Technical Requirements**
   API and data structures, performance targets (response time, concurrency, etc.), special implementations (debounce, polling, lazy loading, etc.); include **module diagram** for multi-module collaboration; when **adding or changing database tables/entities**, include **`erDiagram`** (or cross-reference with the project's unified ER doc and note the changes).

5. **Constraints**
   Timeline and priority, third-party dependencies (SMS, payment, maps, etc.), compliance and security, **boundaries of what's NOT being built**. Clarifying "what not to do" is equally important as "what to do" — it prevents scope creep.

6. **Test Criteria** (Acceptance)
   - **Happy path**: Cover core business flows
   - **Boundary values**: Extremes, nulls, max lengths, etc.
   - **Exception paths** (invalid input, network errors, insufficient permissions, etc.)
   - **Regression points** (existing features potentially affected)
   - **Cross-combination matrix** (when multiple test dimensions exist)

   Each test criterion should be executable: describe action steps and expected results, not just abstract requirements.

### Cross-Combination Matrix and Priority Assessment

When a feature involves multiple independent test dimensions (>= 2 dimensions with at least one having >= 3 values), **explicitly list the dimension combination matrix** and **assess each combination's priority** (P0 / P1 / P2 / P3) to lay groundwork for TDD.

Priority order: Core business path -> Money/security related -> Error recovery -> Boundary values -> Equivalence class merging -> Logically unreachable. P0 rows in the matrix directly correspond to the first batch of TDD test cases.

> Full matrix steps, priority definitions, judgment criteria, and 12-combination login example → `references/test-matrix.md`

## Execution Method

- **New document**: Define module and file path first, then fill in six sections sequentially; confirm with user when info is missing — don't fabricate business rules; **provide Mermaid diagrams where appropriate, don't skip**.
- **Revision**: Maintain module boundaries; sync updates to "Test Criteria" and "Constraints" for affected items, and **update related Mermaid diagrams**.
- **Review assistance**: When user provides existing requirement docs for review, check completeness against all six sections, point out gaps or ambiguities, provide revision suggestions.

## Common Issues and Handling

- **User gives only a one-liner** (e.g., "build a login feature"): First decompose into an information collection checklist (which login methods? Third-party login? Registration needed?), gradually guide user to clarify, then output the six-section document.
- **Requirements span multiple modules**: Generate independent docs per module, but cross-reference related modules in "Technical Requirements". Include module dependency diagram when necessary.
- **Mermaid diagram too complex**: Split into multiple focused diagrams, each addressing one concern (e.g., one sequence diagram for login flow, another for token refresh flow).
