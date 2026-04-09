<p align="center">
  <h1 align="center">Ironweave</h1>
  <p align="center">
    An agentic skills framework & software development methodology for your AI coding agents.
  </p>
  <p align="center">
    <a href="./README_CN.md">中文文档</a> · <a href="https://skills.sh">skills.sh</a> · <a href="#installation">Install</a> · <a href="./LICENSE">MIT License</a>
  </p>
</p>

---

Ironweave is a complete software development workflow for your coding agents, built on top of a set of composable **skills**. It doesn't just write code — it steps back, understands what you're building, plans the work, breaks it into slices, and executes each slice with built-in quality gates. And because the skills trigger automatically, you don't need to do anything special. Your coding agent just has Ironweave.

## How it works

It starts from the moment you give your agent a task. The **orchestrator** skill activates and:

1. **Senses context** — Detects project type (new project, new feature, bug fix, or refactoring) via `project-context`
2. **Scores difficulty** — Rates the task 1-10 via `task-difficulty`, selecting a variant (lite / standard / plus)
3. **Clarifies requirements** — For ambiguous or complex tasks, uses `requirement-qa` and `brainstorm` to nail down scope before coding
4. **Slices scope** — Breaks large tasks into ordered slices (by module dependency), each independently deliverable
5. **Routes** — Picks one of four routes (A: new project, B: new feature, C: bug fix, D: refactoring) with route-specific skill chains
6. **Executes per slice** — Each slice goes through Plan → Execute → Validate → Deliver with quality gates at each transition

If validation fails, work **reflows** to the right level — code-level issues go back to Execute, design-level back to Plan, requirement-level back to scope. No blind retries.

## The Workflow

```
User Request
    │
    ▼
  Context Sensing → Difficulty Scoring → Clarify (if needed) → Scope Slicing
    │
    ▼
  ┌──────────────────────────────────┐
  │  Per-Slice Loop                  │
  │                                  │
  │  Route Selection (A/B/C/D)      │
  │       │                          │
  │       ▼                          │
  │  Plan ──── Gate ──── Execute     │
  │                        │         │
  │                      Gate        │
  │                        │         │
  │                    Validate      │
  │                        │         │
  │                    Deliver       │
  └──────────────────────────────────┘
    │
    ▼
  Done (or next slice)
```

### Three Variants

| Difficulty | Variant | What changes |
|-----------|---------|-------------|
| L1-L2 (easy) | **lite** | Skip optional skills, quick self-review, no mandatory TDD |
| L3 (medium) | **standard** | Full skill chain, mandatory TDD, standard review |
| L4-L5 (hard) | **plus** | SubAgent isolation per task, strict TDD, two-stage review, parallel strategy |

## What's Inside

### Skills Library

**Orchestration**

- `orchestrator` — Full-lifecycle flow orchestrator (routes, quality gates, reflow, slice iteration)

**Requirements & Design**

- `requirement-qa` — Multi-round Q&A to elicit and refine requirements
- `brainstorm` — Multi-perspective brainstorming with expert SubAgents
- `spec-writing` — Structured feature specification documents
- `tech-stack` — Full-stack technology selection & decision docs

**Architecture & Engineering**

- `engineering-principles` — Context-aware principles matcher (SOLID, DDD, TDD, design patterns)
- `api-contract-design` — RESTful/GraphQL API contracts, DTOs, OpenAPI specs
- `error-handling-strategy` — Exception hierarchy, error codes, retry, circuit-breaker, fallback
- `performance-arch-design` — Cache layering, async processing, indexing, rate limiting
- `observability-design` — Distributed tracing, structured logging, metrics, alerting

**Implementation**

- `code-scaffold` — Project scaffolding from domain model + design docs
- `implementation-complexity-analysis` — Technical risk identification, complexity decomposition
- `integration-test-design` — TestContainers, contract testing, mock strategy

**Meta**

- `task-difficulty` — Multi-dimensional difficulty scoring (1-10)
- `project-context` — Project structure awareness & cross-session persistence
- `docs-output` — Document output management (modular docs/ organization)

## Installation

### Via npm

```bash
# Install all skills + all agent configs (Chinese, default)
npx ironweave@latest init

# Install English skills
npx ironweave@latest init --lang en

# Install for a specific editor only
npx ironweave@latest init --agent cursor
npx ironweave@latest init --agent trae
npx ironweave@latest init --agent windsurf

# Only copy skills, skip agent config files
npx ironweave@latest init --skills-only

# Overwrite existing files
npx ironweave@latest init --force

# List all available skills
npx ironweave@latest list
```

Available agents: `claude`, `copilot`, `cursor`, `windsurf`, `cline`, `trae`, `codebuddy`, `codex`, `gemini`, `all` (default).

> **Conflict handling**: Existing files are preserved by default. Ironweave adds its config alongside your existing rules. Use `--force` to overwrite.

> **Skills location**: When targeting a single directory-based editor (e.g., `--agent trae`), skills are installed inside the editor directory (e.g., `.trae/skills/`). With `--agent all` (default), skills go to the project root `skills/`.

### Via skills.sh

```bash
# Install to a specific editor (recommended)
npx skills add YuluoY/ironweave --skill '*' -a cursor -y
npx skills add YuluoY/ironweave --skill '*' -a trae -y
npx skills add YuluoY/ironweave --skill '*' -a claude-code -y

# Install to multiple editors
npx skills add YuluoY/ironweave --skill '*' -a cursor -a windsurf -y

# Install to ALL editors (installs many agent directories)
npx skills add YuluoY/ironweave --all

# Interactive: select skills and editors
npx skills add YuluoY/ironweave

# List available skills
npx skills add YuluoY/ironweave --list
```

Agent names for skills.sh: `claude-code`, `github-copilot`, `cursor`, `windsurf`, `cline`, `trae`, `codebuddy`, `codex`, `gemini-cli`.

> Note: `skills.sh` does not support `--lang`. For English skills, use `npx ironweave@latest init --lang en`.

### Per-Agent Manual Installation

<details>
<summary><b>Claude Code</b></summary>

Ironweave ships with `CLAUDE.md` at the project root — Claude Code reads this automatically.

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>VS Code GitHub Copilot</b></summary>

Ironweave ships with `.github/copilot-instructions.md` pre-configured.

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>Cursor</b></summary>

Ironweave ships with `.cursor/rules/ironweave.mdc` (`alwaysApply: true`) for auto-discovery.

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>Windsurf</b></summary>

Ironweave ships with `.windsurf/rules/ironweave.md` (`trigger: always_on`) for auto-discovery.

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>Cline</b></summary>

Ironweave ships with `.clinerules/ironweave.md` for auto-discovery.

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>Trae</b></summary>

Ironweave ships with `.trae/rules/ironweave.md` for auto-discovery.

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>CodeBuddy (Tencent Cloud)</b></summary>

Ironweave ships with `.codebuddy/rules/ironweave/RULE.mdc` (`alwaysApply: true`) for auto-discovery.

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>Codex (OpenAI)</b></summary>

Ironweave ships with `AGENTS.md` at the project root — Codex reads this automatically.

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>Gemini CLI</b></summary>

Ironweave ships with `GEMINI.md` at the project root — Gemini CLI reads this automatically.

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

## Project Structure

```
ironweave/
├── skills/                            # Skills (Chinese)
│   ├── orchestrator/                # Flow orchestrator
│   │   ├── SKILL.md                # Orchestrator logic
│   │   └── references/             # Methodology docs
│   ├── brainstorm/
│   ├── spec-writing/
│   ├── code-scaffold/
│   ├── ...                          # 16 skills total
│   └── docs-output/
├── skills-en/                         # Skills (English)
├── CLAUDE.md                        # Claude Code
├── AGENTS.md                        # Codex / cross-agent compat
├── GEMINI.md                        # Gemini CLI
├── .github/copilot-instructions.md    # VS Code Copilot
├── .cursor/rules/ironweave.mdc        # Cursor
├── .windsurf/rules/ironweave.md       # Windsurf
├── .clinerules/ironweave.md           # Cline
├── .trae/rules/ironweave.md           # Trae
├── .codebuddy/rules/ironweave/RULE.mdc  # CodeBuddy
├── README.md
├── README_CN.md
├── CONTRIBUTING.md
├── LICENSE
└── package.json
```

## Philosophy

Ironweave is built around one insight: **AI coding agents have systematic cognitive weaknesses** — they underestimate complexity, skip validation, lose context across sessions, and forget what they planned. Every mechanism in Ironweave targets a specific weakness.

- **Path Lock, Not Suggestions** — Flowcharts in route files are mandatory execution paths, not references. Every node must be executed in arrow order. AI is not trusted to self-police completeness.
- **Throttle Before You Build** — Difficulty scoring with built-in upward bias acts as a throttle valve. Because AI systematically underestimates complexity, the score is nudged up unless the task is clearly trivial.
- **Weight Matches Problem** — Three variants (lite / standard / plus) ensure simple tasks stay fast and hard tasks get full rigor. The overhead of the process should match the risk of the problem.
- **Evidence, Not Vibes** — Every decision must anchor to project context facts. "Industry best practice" alone is not a valid justification. If no evidence is found, the assumption must be explicitly labeled.
- **Recommended ≠ Mandatory** — Tech reference tables provide default recommendations for quick decisions, but users can choose any technology — including ones not listed. The human always has the final say.
- **Persist Then Forget** — Each skill writes output to files. Subsequent steps read from files, never from window memory. This directly counters AI context window overflow and attention decay.
- **Reflow, Not Restart** — When validation fails, work routes back to the exact level that broke: code-level → Execute, design-level → Plan, requirement-level → scope. No full teardowns for local issues.
- **Mechanical Reconciliation** — At delivery, a checklist comparison (Plan outputs vs. actual files) catches gaps that AI memory would miss. Trust the filesystem, not the model.
- **Source Is Truth** — All caches, databases, and generated docs are derivatives of source. When conflicts arise, source wins.
- **Human Override Always** — Users can override classification and difficulty with natural language at any point. The system has defaults; humans have final authority.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Skills live directly in this repository.

## License

[MIT](./LICENSE) © Ironweave Contributors
