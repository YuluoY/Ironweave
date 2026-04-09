# Contributing to Ironweave

Thank you for your interest in contributing! Ironweave welcomes contributions from everyone.

## Ways to Contribute

- **Report bugs** — Open an issue describing the problem
- **Suggest skills** — Propose new skills or improvements to existing ones
- **Submit PRs** — Fix bugs, improve documentation, or add features
- **Translate** — Help improve Chinese/English documentation

## Development Setup

```bash
git clone https://github.com/YuluoY/ironweave.git
cd ironweave
```

No build step required — skills are plain Markdown files.

## Skill Structure

Each skill is a directory under `skills/` containing at minimum a `SKILL.md` file:

```
skills/my-skill/
├── SKILL.md              # Required: main skill file with YAML frontmatter
├── references/           # Optional: supporting documents
│   └── rules.md
├── agents/               # Optional: SubAgent definitions
│   └── expert.md
└── scripts/              # Optional: helper scripts
    └── helper.py
```

### SKILL.md Frontmatter (Required)

```yaml
---
name: my-skill
description: >-
  One-paragraph description of what this skill does and when to use it.
---
```

Both `name` and `description` are required for [skills.sh](https://skills.sh) compatibility.

## Guidelines

1. **One skill, one concern** — Each skill should do one thing well
2. **Include trigger phrases** — The `description` field should list scenarios that activate the skill
3. **Reference, don't duplicate** — Use `references/` for shared rules; don't copy content across skills
4. **Test your changes** — Verify skills work with at least one agent before submitting
5. **Bilingual** — New skills should include both English and Chinese content where practical

## Orchestrator Changes

Changes to the orchestrator skill (`skills/orchestrator/`) require extra care:

- Ensure all 4 routes (A/B/C/D) remain consistent
- Verify quality gates in `references/gates.md` still cover all paths
- Check that reflow arrows point to correct targets
- Run through at least one scenario per route mentally

## Commit Messages

Use conventional commits:

```
feat(brainstorm): add devil's advocate role
fix(orchestrator): correct reflow target for need-level failures
docs(readme): update compatibility table
```

## Code of Conduct

Be respectful, constructive, and inclusive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

---

Questions? Open an issue or start a discussion.
