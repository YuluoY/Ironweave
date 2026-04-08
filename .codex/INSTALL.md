# Installing Ironweave for Codex

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YuluoY/ironware.git ~/.codex/ironweave
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/ironweave/skills ~/.agents/skills/ironweave
   ```

   **Windows (PowerShell):**
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
   cmd /c mklink /J "$env:USERPROFILE\.agents\skills\ironweave" "$env:USERPROFILE\.codex\ironweave\skills"
   ```

3. **Restart Codex** to discover the skills.

## Verify

```bash
ls -la ~/.agents/skills/ironweave
```

You should see a symlink pointing to the Ironweave skills directory.

## Updating

```bash
cd ~/.codex/ironweave && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
rm ~/.agents/skills/ironweave
rm -rf ~/.codex/ironweave
```
