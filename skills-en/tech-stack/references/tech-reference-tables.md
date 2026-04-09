# Reference Tech Tables

The following tables are **for selection reference only**. Each category has items marked "recommended" as default suggestions, but **recommended ≠ mandatory** — users can choose other technologies (including those not listed) based on their team's situation, just document the reasoning. When writing into the final document, each item must be annotated with "Adopted / Not adopted / TBD" with rationale.

---

## Runtime & Package Management

| Category | Technology | Notes |
|----------|-----------|-------|
| Runtime | Node.js | Recommend current **stable LTS** (not latest); specify version or semver range, ensure ≥ toolchain minimum |
| Package manager | pnpm | Specify exact version, lock via `packageManager` field (e.g., `"packageManager": "pnpm@10.12.0"`); sync via Corepack; Monorepo uses `pnpm-workspace.yaml` |

> **Version consistency check**: Confirm that Node versions in `package.json` `engines`/`packageManager`, `.nvmrc`, CI config, and Docker base image all point to the same version.

---

## Frontend · Cross-Framework Common

| Category | Technology | Notes |
|----------|-----------|-------|
| Build | Vite | Ultra-fast cold start, native ESM; mature templates for Vue / React |
| Package management | pnpm + Monorepo | Saves disk space, unified multi-package management; **see "Runtime & Package Management" for pnpm version** |
| Styling | Sass + BEM | Maintainable style architecture |
| Style linting | Stylelint | Sass/CSS style consistency |
| HTTP requests | axios | API request encapsulation |
| Icon library | Font Awesome | Rich vector icons, supports tree-shaking |
| Utility library (general) | lodash-es | Framework-agnostic common utility functions |
| Unit testing | Vitest | Integrated with Vite ecosystem |
| End-to-end testing | Playwright | Full-chain E2E testing |
| Library bundling (`packages/` TS) | tsdown | Build and type declarations for publishable/internal TS libraries; **use tsdown instead of tsup**, compatible with tsup's main options for easy migration |
| Client-side storage | IndexedDB (via Dexie.js / idb) | Browser-side high-capacity structured storage; Dexie.js provides a concise Promise API, idb is a lightweight wrapper; suited for offline caching, draft storage, local data sync |

---

## Frontend · Vue Track (Include When Selected)

| Category | Technology | Notes |
|----------|-----------|-------|
| Framework | Vue 3 + TypeScript | Progressive framework, type-safe |
| Routing | Vue Router | Official routing solution |
| State management | Pinia | Lightweight, full TypeScript support |
| Composition utilities | VueUse | Common composable function wrappers |
| Internationalization | vue-i18n | Multi-language support (tree-shakeable) |

---

## Frontend · React Track (Include When Selected)

| Category | Technology | Notes |
|----------|-----------|-------|
| Framework | React 18+ + TypeScript | Mature component model and ecosystem |
| Routing | React Router / TanStack Router | Choose based on project scale and data loading needs |
| State management | Zustand, Jotai, Redux Toolkit, etc. | Choose based on data flow complexity |
| Internationalization | react-i18next, etc. | Multi-language support (tree-shakeable) |
| Full-stack / SSR (optional) | Next.js, Remix, etc. | Include in selection when SSR or full-stack capability is needed |

---

## Frontend · UI & Component Libraries

| Category | Technology | Notes |
|----------|-----------|-------|
| Third-party component library (Vue) | Element Plus, Ant Design Vue, Naive UI, Vuetify, etc. | Choose based on design specifications, accessibility, and licensing |
| Third-party component library (React) | Ant Design, MUI, Chakra UI, Mantine, Radix + styling solution, etc. | Same as above |
| Custom component library | Independent package in Monorepo (e.g., `packages/ui`) | Align with Design Tokens, documentation site, and accessibility standards; can coexist with or progressively replace third-party libs |

---

## Backend (Node.js Family)

| Category | Technology | Notes |
|----------|-----------|-------|
| Framework (recommended) | **NestJS** | Modular, decorator-driven Node.js framework, suited for medium-to-large projects |
| Framework (alternative) | Express | Most mature Node.js web framework, rich ecosystem, suited for lightweight projects |
| Framework (alternative) | Koa | Built by the Express team, leaner middleware model, suited for scenarios needing fine-grained middleware control |
| API style | RESTful | Standard HTTP semantics |
| API docs | Swagger / OpenAPI | Auto-generated, NestJS official integration |
| Validation | class-validator + class-transformer | DTO layer validation, NestJS standard |
| Authentication | Dual Token + Passport.js | Access token + refresh token |
| Authorization | RBAC | Role-based access control |
| ORM (recommended) | **TypeORM** | Decorator support, deep NestJS integration |
| ORM (alternative) | Prisma | Type-safe schema-first ORM, excellent migration experience |
| ORM (alternative) | Drizzle | Lightweight TypeScript-first ORM, SQL-like API |
| Database (recommended) | **PostgreSQL** | Relational, production-grade stability, feature-rich (JSON, full-text search, window functions, etc.) |
| Database (alternative) | MySQL | Widely-used relational database, mature community |
| Database (alternative) | MongoDB | Document database, suited for semi-structured data scenarios |
| Caching | Redis | Token storage, hot data caching |
| Logging | Winston / pino | Structured log output |

---

## Backend (Java Family, Alternative Track)

| Category | Technology | Notes |
|----------|-----------|-------|
| Framework | Spring Boot | De facto standard in the Java ecosystem, first choice for enterprise projects |
| API style | RESTful / Spring MVC | Controller + Service layer standard architecture |
| API docs | SpringDoc (OpenAPI 3) | Annotation-driven auto-generation, replaces legacy Springfox |
| Validation | Jakarta Validation (Bean Validation) | Annotation-based validation, built into Spring Boot |
| Authentication | Spring Security + JWT | Mature security framework, supports multiple auth methods |
| Authorization | RBAC / Spring Security | Role-based or expression-based access control |
| ORM | MyBatis-Plus / JPA (Hibernate) | MyBatis-Plus for flexible SQL control; JPA for domain-driven design |
| Database | Same as Node.js family | PostgreSQL (recommended) / MySQL / MongoDB |
| Caching | Redis + Spring Cache | Abstract cache layer, seamless Redis integration |
| Logging | SLF4J + Logback | Spring Boot default logging framework |
| Build | Maven / Gradle | Maven is stable and mature; Gradle offers faster builds |

---

## DevOps & Infrastructure (Optional)

| Category | Technology | Notes |
|----------|-----------|-------|
| Reverse proxy | Nginx | Static asset hosting, API forwarding |
| Containerization (optional) | Docker + Docker Compose | Environment consistency, dev-production alignment; adopt based on deployment needs |

---

## Engineering Standards

| Category | Technology | Notes |
|----------|-----------|-------|
| Code linting | oxlint + oxfmt | High-performance Oxc-based lint and formatting |
| Git hooks | Husky + lint-staged | Auto-lint staged files before commit |
| Commit conventions | commitlint | Enforce commit message format (e.g., Conventional Commits) |
| Version management | Changesets | Monorepo multi-package versioning and release management |
| CLI tooling | Commander + Inquirer | CLI scaffold development (command parsing + interactive prompts) |
| CLI styling | chalk / picocolors + ora + boxen | Terminal colored output (picocolors is lighter with zero deps), loading spinners, info boxes |
| CLI arg parsing (alternative) | yargs / citty | Feature-richer argument parsing solutions |
