# Ironweave

You have access to the Ironweave skills library — a complete software development workflow with built-in quality gates.

## How to use

The **orchestrator** skill (`skills/orchestrator/SKILL.md`) is the main entry point. It automatically:
- Senses project context and scores task difficulty
- Selects the right route (new project / new feature / bug fix / refactoring)
- Runs Plan → Execute → Validate → Deliver with quality gates per slice

For any development task, start by reading the orchestrator skill. It will guide which other skills to invoke.

## Skills available

All skills are in `skills/`. Each has a `SKILL.md` with YAML frontmatter (`name`, `description`).

Key skills: `orchestrator`, `requirement-qa`, `brainstorm`, `spec-writing`, `tech-stack`, `engineering-principles`, `api-contract-design`, `code-scaffold`, `error-handling-strategy`, `performance-arch-design`, `observability-design`, `integration-test-design`, `implementation-complexity-analysis`, `task-difficulty`, `project-context`, `docs-output`.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
