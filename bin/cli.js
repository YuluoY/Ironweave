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
                    (claude, copilot, cursor, windsurf, cline, trae, codebuddy, codex, gemini, all)
                    Default: all
  --lang <lang>     Language for skills: zh (Chinese, default) or en (English)
  --skills-only     Only copy skills/, skip agent config files
  --force           Overwrite existing files (default: skip existing)
  --help            Show this help message
`);
  process.exit(0);
}

if (command === 'list') {
  const langIdx = args.indexOf('--lang');
  const listLang = langIdx !== -1 ? args[langIdx + 1] : 'zh';
  const skillsSrc = listLang === 'en' ? 'skills-en' : 'skills';
  const skillsDir = path.join(__dirname, '..', skillsSrc);
  const skills = fs.readdirSync(skillsDir).filter(f => {
    return fs.statSync(path.join(skillsDir, f)).isDirectory();
  });
  console.log(`\nIronweave Skills [${listLang}] (${skills.length}):\n`);
  skills.forEach(s => console.log(`  - ${s}`));
  console.log('');
  process.exit(0);
}

if (command === 'init') {
  const targetDir = process.cwd();
  const pkgDir = path.join(__dirname, '..');

  const agentFlag = args.indexOf('--agent');
  const agent = agentFlag !== -1 ? args[agentFlag + 1] : 'all';
  const langFlag = args.indexOf('--lang');
  const lang = langFlag !== -1 ? args[langFlag + 1] : 'zh';
  const skillsOnly = args.includes('--skills-only');
  const force = args.includes('--force');

  // Directory-based agent roots (skills go inside agent dir for single-agent install)
  const dirBasedAgents = {
    cursor: '.cursor',
    windsurf: '.windsurf',
    cline: '.clinerules',
    trae: '.trae',
    codebuddy: '.codebuddy'
  };
  const isSingleDirAgent = agent !== 'all' && dirBasedAgents[agent];

  // Copy skills/
  const skillsSrc = lang === 'en' ? 'skills-en' : 'skills';
  const srcSkills = path.join(pkgDir, skillsSrc);
  const dstSkills = isSingleDirAgent
    ? path.join(targetDir, dirBasedAgents[agent], 'skills')
    : path.join(targetDir, 'skills');
  copyDirRecursive(srcSkills, dstSkills, force);
  const skillsLabel = isSingleDirAgent ? `${dirBasedAgents[agent]}/skills/` : 'skills/';
  console.log(`✓ ${skillsLabel} copied (${lang === 'en' ? 'English' : 'Chinese'})`);

  // Only install hooks for agents that use them (cursor, claude, or all)
  const hooksAgents = ['cursor', 'claude', 'all'];
  if (hooksAgents.includes(agent)) {
    const srcHooks = path.join(pkgDir, 'hooks');
    const dstHooks = path.join(targetDir, 'hooks');
    copyDirRecursive(srcHooks, dstHooks, force);
    console.log('✓ hooks/ copied');
  }

  if (!skillsOnly) {
    const agentFiles = {
      claude: [
        { src: 'CLAUDE.md', dst: 'CLAUDE.md' }
      ],
      copilot: [
        { src: '.github/copilot-instructions.md', dst: '.github/copilot-instructions.md' }
      ],
      cursor: [
        { src: '.cursor/rules', dst: '.cursor/rules', dir: true }
      ],
      windsurf: [
        { src: '.windsurf/rules', dst: '.windsurf/rules', dir: true }
      ],
      cline: [
        { src: '.clinerules', dst: '.clinerules', dir: true }
      ],
      trae: [
        { src: '.trae/rules', dst: '.trae/rules', dir: true }
      ],
      codebuddy: [
        { src: '.codebuddy/rules', dst: '.codebuddy/rules', dir: true }
      ],
      codex: [
        { src: 'AGENTS.md', dst: 'AGENTS.md' }
      ],
      gemini: [
        { src: 'GEMINI.md', dst: 'GEMINI.md' }
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
      // Patch skills path references for single dir-based agent
      if (isSingleDirAgent) {
        const prefix = dirBasedAgents[agent] + '/';
        files.forEach(f => {
          const dstPath = path.join(targetDir, f.dst);
          if (f.dir) {
            patchSkillsPathsInDir(dstPath, prefix);
          } else if (fs.existsSync(dstPath)) {
            patchSkillsPathsInFile(dstPath, prefix);
          }
        });
      }
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

function patchSkillsPathsInDir(dirPath, prefix) {
  if (!fs.existsSync(dirPath) || !fs.statSync(dirPath).isDirectory()) return;
  for (const entry of fs.readdirSync(dirPath, { withFileTypes: true })) {
    const full = path.join(dirPath, entry.name);
    if (entry.isDirectory()) patchSkillsPathsInDir(full, prefix);
    else patchSkillsPathsInFile(full, prefix);
  }
}

function patchSkillsPathsInFile(filePath, prefix) {
  let content = fs.readFileSync(filePath, 'utf8');
  const patched = content.replace(/`skills\//g, '`' + prefix + 'skills/');
  if (patched !== content) fs.writeFileSync(filePath, patched);
}
