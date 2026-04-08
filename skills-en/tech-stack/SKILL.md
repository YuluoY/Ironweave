---
name: tech-stack
description: >-
  Write and maintain tech stack selection documents (e.g. docs/tech-stack.md), covering frontend (Vue 3 / React), backend (Node.js ecosystem like NestJS / Express / Koa, or Java ecosystem like Spring Boot), databases, ops, and engineering standards — full-stack technical decisions. Monorepo defaults to apps/ + packages/ layout. TS libraries use tsdown (not tsup) for bundling. All architecture and ER diagrams use Mermaid. Node.js and pnpm versions must be explicitly stated.
  Use this skill when: the user mentions tech selection, tech stack, technology architecture, technical proposal, architecture design, database design, stack decisions, framework selection, technology roadmap, dependency selection, toolchain selection, frontend/backend selection, infrastructure selection, or asks to write/revise/review technical architecture documents or discuss which frameworks/libraries/tools to use, even without explicitly saying "tech stack". Not applicable for specific feature requirement documents.
---

# Tech Stack Selection

This Skill is responsible for **tech stack selection documents** (e.g. `docs/tech-stack.md`, path per project convention) — helping teams consolidate scattered technical decisions into one traceable, reviewable document. The core value: make every technical decision documented with rationale, avoiding "I thought you were using X" communication issues.

**Does not** cover requirement specs six-section structure.

## Principles

- Write the **actually adopted** stack and dependencies in a standalone doc. Each choice should include **selection reasoning** and **compared alternatives** — this helps newcomers understand decision context and facilitates future re-evaluation.
- Frontend can be selected from **Vue 3** or **React** (Monorepo can have multiple apps coexisting); must state the chosen path and reasoning, not list all possibilities.
- **Monorepo directory convention**: `apps/` for **business applications/runnable projects**; `packages/` for **reusable packages** (component libraries, utility libraries, config packages, etc.). Tech stack doc should state whether the repo adopts this structure with any exceptions.
- **TypeScript library bundling**: TS libraries in `packages/` that need JS/type declaration output should **prefer tsdown as the bundler, not tsup** (tsdown is option-compatible with tsup for easy migration; document any Node version requirements).
- **Node.js and pnpm versions**: Tech stack doc should **explicitly state** the project's Node.js and pnpm version (or compatible range). Version choices should use current **stable LTS** (not bleeding edge, not about-to-EOL), while meeting minimum toolchain requirements (e.g., tsdown). Version info should be consistent across: `package.json` `engines` and `packageManager` fields, `.nvmrc` (if any), CI and Docker configs. Recommend using Corepack to lock pnpm version.

## Diagrams (Only Drawing Language: Mermaid)

For any **visualization** in tech stack docs (architecture, deployment, module relationships, key flows, component sequences, **database entity relationships**, etc.), **use Mermaid exclusively** — not PlantUML, Draw.io source files, plain images replacing editable structural diagrams (exported images from Mermaid rendering are fine). Mermaid is chosen because it's plain text, can be Git-managed alongside Markdown, and supports PR review and change tracking.

Common types and syntax (use as needed, can combine multiple diagrams):

| Type | Typical Use | Mermaid Form |
|------|----------|----------------|
| Architecture Diagram | Client, gateway, services, DB, cache deployment and data flow | `flowchart` / `flowchart LR` |
| Module Diagram | Business module and package dependency/call relationships | `graph TD` / `graph LR` |
| Flow Diagram | Request handling, publishing, auth steps | `flowchart` |
| Sequence Diagram | Login, payment multi-actor interaction sequences | `sequenceDiagram` |
| **ER Diagram** | **Database design**: entities, fields, keys, relationships | **`erDiagram`** |

Diagrams should be embedded in Markdown code blocks (` ```mermaid `) for version control and review.

> **When to draw**: Architecture diagram is standard for tech stack docs — at least one global architecture view; database design must have ER diagram; complex frontend-backend interactions get sequence diagrams.

## Suggested Document Structure

1. **Overview**: Project form, repo structure (explain `apps/` / `packages/` roles for Monorepo); frontend-backend boundaries; **Runtime & Toolchain**: state confirmed **Node.js** and **pnpm** versions (or ranges) with locking methods (e.g., `packageManager`, `engines`, Corepack); can include **architecture diagram**.
2. **Frontend**: Write "cross-framework common" confirmed choices first, then **one of** "Vue path" or "React path" (or per-app breakdown); can include **module diagram** showing app-package relationships.
3. **UI**: Third-party component library or custom `packages/ui` selection and principles.
4. **Backend**: Framework (Node.js ecosystem: NestJS / Express / Koa, or Java ecosystem: Spring Boot; **NestJS recommended**), API style, documentation, validation, auth, permissions, ORM (TypeORM / Prisma / Drizzle; **TypeORM recommended**), database (PostgreSQL / MySQL / MongoDB; **PostgreSQL recommended**), cache, logging. **Database design** must use Mermaid **`erDiagram`** for core entities, fields, and relationships.
5. **Ops & Infrastructure** (optional): Reverse proxy, containerization, etc. Docker is optional based on actual deployment needs.
6. **Engineering Standards**: Lint/formatting, Git hooks, commit conventions, version management, CLI, etc. (include versions or ranges as needed).

> Each section's tech choices should include brief **selection reasoning** (one or two sentences), explaining why it was chosen and what alternatives were considered. This makes the doc not just a list, but a decision record.

## Reference Tech Tables

Covers 8 categories: Runtime & Package Management, Frontend Cross-framework Common, Vue Path, React Path, UI & Component Libraries, Backend, Ops Infrastructure, Engineering Standards. When writing docs, mark each item as "Adopted / Not adopted / Pending" with reasoning.

> Full reference tech tables → `references/tech-reference-tables.md`

## Execution Method

- Based on user-provided constraints (team mandates, legacy stack, cloud vendor, etc.), narrow options; table items are **not mandatory** — unadopted technologies need not appear in the final doc, or can be marked "Not adopted".
- Output should be **deliverable Markdown** (or user-specified format), suitable for version control and implementation alignment; **structure, flow, collaboration, and database entity relationship descriptions should include Mermaid diagrams** (including **`erDiagram`**) — avoid describing with long paragraphs only.
- If user hasn't specified **Node / pnpm** versions: suggest versions based on current **stable LTS** and dependency minimums, and remind to sync across `engines`, `packageManager`, and CI/Docker.

## Common Issues and Handling

- **User only says "help me do a tech selection"**: First confirm project type (Web app? Mobile? Admin panel?), team size, existing tech stack constraints, then provide selection recommendations.
- **User wants to compare two tech approaches**: Create comparison table across dimensions like feature coverage, ecosystem maturity, learning curve, team familiarity, community activity; give recommendation with reasoning.
- **Version locking inconsistency**: Check versions in `package.json` `engines`/`packageManager`, `.nvmrc`, CI config, Docker image — if inconsistent, flag in the document and provide unification plan.
