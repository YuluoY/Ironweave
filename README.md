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
- `skill-creator` — Create, modify, and evaluate agent skills

## Installation

### Via skills.sh (Recommended)

```bash
# Install all skills
npx skills add YuluoY/ironware

# Install specific skills
npx skills add YuluoY/ironware --skill orchestrator --skill brainstorm

# List available skills
npx skills add YuluoY/ironware --list
```

Supports **40+ agents**: Claude Code, GitHub Copilot, Cursor, Codex, Windsurf, Cline, OpenCode, Gemini CLI, Trae, CodeBuddy, and more.

### Per-Agent Manual Installation

<details>
<summary><b>Claude Code</b></summary>

```bash
git clone https://github.com/YuluoY/ironware.git ~/.claude/ironweave
mkdir -p ~/.claude/skills
ln -s ~/.claude/ironweave/skills ~/.claude/skills/ironweave
```

Or use the Claude plugin system — Ironweave ships with `.claude-plugin/plugin.json`.

</details>

<details>
<summary><b>VS Code GitHub Copilot</b></summary>

Copy the `skills/` directory into your project, then add to `.github/copilot-instructions.md`:

```markdown
The orchestrator skill (skills/orchestrator/SKILL.md) is the main entry point.
For any development task, start by reading it.
```

Or clone Ironweave directly — it ships with `.github/copilot-instructions.md` pre-configured.

</details>

<details>
<summary><b>Cursor</b></summary>

```bash
git clone https://github.com/YuluoY/ironware.git
```

Ironweave ships with `.cursorrules` and `.cursor-plugin/plugin.json` for auto-discovery.

</details>

<details>
<summary><b>Codex (OpenAI)</b></summary>

```bash
git clone https://github.com/YuluoY/ironware.git ~/.codex/ironweave
mkdir -p ~/.agents/skills
ln -s ~/.codex/ironweave/skills ~/.agents/skills/ironweave
```

See [.codex/INSTALL.md](./.codex/INSTALL.md) for details.

</details>

<details>
<summary><b>OpenCode</b></summary>

Add to your `opencode.json`:

```json
{
  "plugin": ["ironweave@git+https://github.com/YuluoY/ironware.git"]
}
```

See [.opencode/INSTALL.md](./.opencode/INSTALL.md) for details.

</details>

<details>
<summary><b>Windsurf / Cline / Gemini CLI</b></summary>

Ironweave ships with `.windsurfrules`, `.clinerules`, and `GEMINI.md` respectively. Clone the repo and the agent auto-discovers the rules.

```bash
git clone https://github.com/YuluoY/ironware.git
```

</details>

<details>
<summary><b>Trae / CodeBuddy / Other Agents</b></summary>

Copy the `skills/` directory into your project. Then add the following to your agent's custom instructions:

> The orchestrator skill (`skills/orchestrator/SKILL.md`) is the main entry point. For any development task, start by reading it. All skills are in `skills/`, each with a `SKILL.md` containing instructions.

</details>

## Project Structure

```
ironweave/
├── skills/
│   ├── orchestrator/              # Flow orchestrator
│   │   ├── SKILL.md              # Orchestrator logic
│   │   └── references/           # Methodology docs
│   ├── brainstorm/
│   ├── spec-writing/
│   ├── code-scaffold/
│   ├── ...                        # 16 more skills
│   └── skill-creator/
├── CLAUDE.md                      # Claude Code instructions
├── AGENTS.md                      # Codex instructions
├── GEMINI.md                      # Gemini CLI instructions
├── .github/copilot-instructions.md  # VS Code Copilot
├── .cursorrules                   # Cursor rules
├── .windsurfrules                 # Windsurf rules
├── .clinerules                    # Cline rules
├── .claude-plugin/plugin.json     # Claude plugin manifest
├── .cursor-plugin/plugin.json     # Cursor plugin manifest
├── .codex/INSTALL.md              # Codex install guide
├── .opencode/INSTALL.md           # OpenCode install guide
├── README.md
├── README_CN.md
├── CONTRIBUTING.md
├── LICENSE
└── package.json
```

## Philosophy

- **Adaptive routing** over linear workflows — different task types need different flows
- **Quality gates with reflow** over pass/fail — failures route back to the right phase
- **Scope slicing** before execution — large tasks split into ordered, independently deliverable slices
- **Overhead scales with complexity** — simple tasks stay fast (lite), hard tasks get full rigor (plus)
- **Skills as methodology** — each skill encodes decision trees, not just templates

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Skills live directly in this repository. Follow `skills/skill-creator` for creating and testing new skills.

## License

[MIT](./LICENSE) © Ironweave Contributors
