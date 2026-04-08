# Installing Ironweave for OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed

## Installation

Add ironweave to the `plugin` array in your `opencode.json` (global or project-level):

```json
{
  "plugin": ["ironweave@git+https://github.com/YuluoY/ironware.git"]
}
```

Restart OpenCode. The plugin auto-installs and registers all skills.

## Usage

Use OpenCode's native `skill` tool:

```
use skill tool to list skills
use skill tool to load ironweave/orchestrator
```

## Updating

Ironweave updates automatically when you restart OpenCode.

To pin a specific version:

```json
{
  "plugin": ["ironweave@git+https://github.com/YuluoY/ironware.git#v1.0.0"]
}
```

## Uninstalling

Remove the plugin entry from your `opencode.json` and restart OpenCode.
