#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const command = args[0] || 'init';

if (command === '--help' || command === '-h') {
  console.log(`
ironweave - Agentic skills framework for AI coding agents

Usage:
  npx ironweave init [options]     Install skills into current project
  npx ironweave list               List all available skills

Options:
  --agent <name>    Only install config for specific agent
                    (claude, copilot, cursor, windsurf, cline, codex, gemini, all)
                    Default: all
  --skills-only     Only copy skills/, skip agent config files
  --force           Overwrite existing files (default: skip existing)
  --help            Show this help message
`);
  process.exit(0);
}

if (command === 'list') {
  const skillsDir = path.join(__dirname, '..', 'skills');
  const skills = fs.readdirSync(skillsDir).filter(f => {
    return fs.statSync(path.join(skillsDir, f)).isDirectory();
  });
  console.log(`\nIronweave Skills (${skills.length}):\n`);
  skills.forEach(s => console.log(`  - ${s}`));
  console.log('');
  process.exit(0);
}

if (command === 'init') {
  const targetDir = process.cwd();
  const pkgDir = path.join(__dirname, '..');

  const agentFlag = args.indexOf('--agent');
  const agent = agentFlag !== -1 ? args[agentFlag + 1] : 'all';
  const skillsOnly = args.includes('--skills-only');
  const force = args.includes('--force');

  // Copy skills/ and hooks/
  const srcSkills = path.join(pkgDir, 'skills');
  const dstSkills = path.join(targetDir, 'skills');
  copyDirRecursive(srcSkills, dstSkills, force);
  console.log('✓ skills/ copied');

  const srcHooks = path.join(pkgDir, 'hooks');
  const dstHooks = path.join(targetDir, 'hooks');
  copyDirRecursive(srcHooks, dstHooks, force);
  console.log('✓ hooks/ copied');

  if (!skillsOnly) {
    const agentFiles = {
      claude: [
        { src: 'CLAUDE.md', dst: 'CLAUDE.md' },
        { src: '.claude-plugin', dst: '.claude-plugin', dir: true }
      ],
      copilot: [
        { src: '.github/copilot-instructions.md', dst: '.github/copilot-instructions.md' }
      ],
      cursor: [
        { src: '.cursorrules', dst: '.cursorrules' },
        { src: '.cursor-plugin', dst: '.cursor-plugin', dir: true }
      ],
      windsurf: [
        { src: '.windsurfrules', dst: '.windsurfrules' }
      ],
      cline: [
        { src: '.clinerules', dst: '.clinerules' }
      ],
      codex: [
        { src: 'AGENTS.md', dst: 'AGENTS.md' },
        { src: '.codex', dst: '.codex', dir: true }
      ],
      gemini: [
        { src: 'GEMINI.md', dst: 'GEMINI.md' },
        { src: 'gemini-extension.json', dst: 'gemini-extension.json' }
      ]
    };

    const agents = agent === 'all' ? Object.keys(agentFiles) : [agent];

    agents.forEach(a => {
      const files = agentFiles[a];
      if (!files) {
        console.log(`✗ Unknown agent: ${a}`);
        return;
      }
      files.forEach(f => {
        const srcPath = path.join(pkgDir, f.src);
        const dstPath = path.join(targetDir, f.dst);
        if (f.dir) {
          copyDirRecursive(srcPath, dstPath, force);
        } else {
          const dstDir = path.dirname(dstPath);
          if (!fs.existsSync(dstDir)) fs.mkdirSync(dstDir, { recursive: true });
          if (force || !fs.existsSync(dstPath)) {
            fs.copyFileSync(srcPath, dstPath);
          }
        }
      });
      console.log(`✓ ${a} config installed`);
    });
  }

  console.log('\n🎉 Ironweave installed! Your agent will auto-discover the skills.\n');
  process.exit(0);
}

console.error(`Unknown command: ${command}. Run "npx ironweave --help" for usage.`);
process.exit(1);

function copyDirRecursive(src, dst, force) {
  if (!fs.existsSync(src)) return;
  if (!fs.existsSync(dst)) fs.mkdirSync(dst, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const dstPath = path.join(dst, entry.name);
    if (entry.isDirectory()) {
      copyDirRecursive(srcPath, dstPath, force);
    } else if (force || !fs.existsSync(dstPath)) {
      fs.copyFileSync(srcPath, dstPath);
    }
  }
}
