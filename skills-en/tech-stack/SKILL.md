---
name: tech-stack
description: >-
  Write and maintain tech stack selection documents (output to specs/tech-stack/ directory, split by category), covering frontend, backend, databases, ops, and engineering standards — full-stack technical decisions. Reference tech tables are for selection reference only — users can freely choose any technology, including those not listed in the tables. All architecture and ER diagrams use Mermaid.
  Use this skill when: the user mentions tech selection, tech stack, technology architecture, technical proposal, architecture design, database design, stack decisions, framework selection, technology roadmap, dependency selection, toolchain selection, frontend/backend selection, infrastructure selection, or asks to write/revise/review technical architecture documents or discuss which frameworks/libraries/tools to use, even without explicitly saying "tech stack". Not applicable for specific feature requirement documents.
---

# Tech Stack Selection

This Skill is responsible for **tech stack selection documents** (`specs/tech-stack/` directory, split by category) — helping teams consolidate scattered technical decisions into a set of traceable, reviewable documents. The core value: make every technical decision documented with rationale, avoiding "I thought you were using X" communication issues.

**Does not** cover requirement specs six-section structure.

## Principles

- Write the **actually adopted** stack and dependencies in standalone docs. Each choice should include **selection reasoning** and **compared alternatives** — this helps newcomers understand decision context and facilitates future re-evaluation.
- **Recommended ≠ mandatory**: The reference tech tables (`references/tech-reference-tables.md`) provide **default recommended solutions** per category (e.g., NestJS for backend, PostgreSQL for database, etc.) for quick decision-making. However, users can choose other technologies (including those not listed) based on team familiarity, project scale, and business requirements — just document the reasoning.
- Frontend framework, backend framework, database, and other core selections are determined by **team familiarity, project scale, and business requirements**; must state the chosen path and reasoning, not list all possibilities.
- **Monorepo directory convention** (if adopted): `apps/` for **business applications/runnable projects**; `packages/` for **reusable packages** (component libraries, utility libraries, config packages, etc.). Tech stack doc should state whether the repo adopts this structure with any exceptions.
- **Runtime and toolchain versions**: Tech stack docs should **explicitly state** the project's runtime version (e.g., Node.js, Java, etc.) and package manager version (e.g., pnpm, npm, yarn, etc.). Version info should be consistent across `package.json` (or equivalent config), CI, and container configs.

## Diagram Strategy

For any **visualization** in tech stack docs, do not use PlantUML, Draw.io source files, or plain images replacing editable structural diagrams (exported images from Mermaid rendering are fine).

| Scenario | Tool | Mermaid Form |
|----------|------|-------------|
| Architecture diagrams (deployment, data flow) | Mermaid | `flowchart` / `flowchart LR` |
| Module diagrams (dependencies, call relationships) | Mermaid | `graph TD` / `graph LR` |
| Flow diagrams (request handling, auth steps) | Mermaid | `flowchart` |
| Sequence diagrams (multi-actor interactions) | Mermaid | `sequenceDiagram` |
| ER diagrams (database entity relationships) | Mermaid | `erDiagram` |
| **Directory trees / file structures** | **Plain text tree** (`├── └──`) | — |

**Rule**: Logic, module, flow, sequence, architecture, and ER diagrams **must use Mermaid code**. Directory trees/file structures use plain text tree format. Mermaid is plain text — Git-manageable, diffable, PR-reviewable.

> **When to draw**: Architecture diagram is standard for tech stack docs — at least one global architecture view; database design must have ER diagram; complex frontend-backend interactions get sequence diagrams.

## Output Directory Structure

Tech stack selection documents are split into separate files by category, output to the `specs/tech-stack/` directory:

```
specs/tech-stack/
├── overview.md          # Overview: project form, repo structure, runtime versions, global architecture diagram
├── frontend.md          # Frontend: framework selection, UI component libraries, build tools, state management
├── backend.md           # Backend: framework, API style, auth, permissions, logging
├── database.md          # Database: database selection, ORM, caching, ER diagrams
├── ops.md               # Ops & Infrastructure: deployment, containerization, reverse proxy, CI/CD
└── engineering-standards.md  # Engineering Standards: lint, Git hooks, commit conventions, version management
```

> Adjust files based on actual project scale. Small projects can merge into fewer files; large projects can further split (e.g., frontend files per app).

### Content Guidelines Per File

1. **overview.md**: Project form, repo structure (explain directory roles for Monorepo), frontend-backend boundaries; runtime and toolchain versions with locking methods; can include **architecture diagram**.
2. **frontend.md**: Framework selection with reasoning, cross-framework common choices, UI component library selection; can include **module diagram** showing app-package relationships.
3. **backend.md**: Framework selection with reasoning, API style, API documentation, validation, authentication, authorization model, logging strategy.
4. **database.md**: Database selection with reasoning, ORM selection, caching strategy; **database design** must use Mermaid **`erDiagram`** for core entities, fields, and relationships.
5. **ops.md** (optional): Deployment strategy, reverse proxy, containerization, CI/CD pipeline. Include based on actual deployment needs.
6. **engineering-standards.md**: Lint/formatting, Git hooks, commit conventions, version management, CLI tools, etc. (include versions or ranges as needed).

> Each section's tech choices should include brief **selection reasoning** (one or two sentences), explaining why it was chosen and what alternatives were considered. This makes the doc not just a list, but a decision record.

## Reference Tech Tables

Covers categories including runtime & package management, frontend, UI & component libraries, backend, databases, ops infrastructure, and engineering standards. When writing docs, mark each item as "Adopted / Not adopted / TBD" with reasoning.

> **Recommended ≠ mandatory**: Items marked "recommended" in the reference tech tables are default suggestions. Users can choose other technologies (including those not covered) based on their situation — just document the reasoning.

> Full reference tech tables → `references/tech-reference-tables.md`

## Execution Method

- Based on user-provided constraints (team mandates, legacy stack, cloud vendor, etc.), narrow options; items marked "recommended" in the reference tech tables are default suggestions, **recommended ≠ mandatory** — users can choose technologies not listed in the tables. Unadopted technologies need not appear in the final doc, or can be marked "Not adopted".
- Output is **category-split Markdown files** under the `specs/tech-stack/` directory, suitable for version control and implementation alignment; **structure, flow, collaboration, and database entity relationship descriptions should include Mermaid diagrams** (including **`erDiagram`**) — avoid describing with long paragraphs only.
- If user hasn't specified runtime versions: suggest versions based on current **stable releases** and dependency minimums, and remind to sync across corresponding config files.

## Common Issues and Handling

- **User only says "help me do a tech selection"**: First confirm project type (Web app? Mobile? Admin panel?), team size, existing tech stack constraints, then provide selection recommendations.
- **User wants to compare two tech approaches**: Create comparison table across dimensions like feature coverage, ecosystem maturity, learning curve, team familiarity, community activity; give recommendation with reasoning.
- **Version locking inconsistency**: Check versions in `package.json` `engines`/`packageManager`, `.nvmrc`, CI config, Docker image — if inconsistent, flag in the document and provide unification plan.
