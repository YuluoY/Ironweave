<p align="center">
  <h1 align="center">Ironweave</h1>
  <p align="center">
    面向 AI 编程 Agent 的技能框架与软件开发方法论。
  </p>
  <p align="center">
    <a href="./README.md">English</a> · <a href="https://skills.sh">skills.sh</a> · <a href="#安装">安装</a> · <a href="./LICENSE">MIT 许可证</a>
  </p>
</p>

---

Ironweave 是一套完整的软件开发工作流，由一组可自由组合的 **技能（Skills）** 构建而成。它不只是写代码 — 它会先理解你要构建什么，制定计划，将工作拆分为切片，然后通过内置质量卡点逐一执行每个切片。而且这些技能会自动触发，你不需要做任何特殊操作。你的 Agent 拥有 Ironweave 就够了。

## 工作原理

从你给 Agent 一个任务开始，**orchestrator** 技能自动激活：

1. **感知上下文** — 通过 `project-context` 检测项目类型（新项目、新功能、Bug 修复、重构）
2. **评估难度** — 通过 `task-difficulty` 进行 1-10 评分，选择变体（lite / standard / plus）
3. **澄清需求** — 对于模糊或复杂的任务，使用 `requirement-qa` 和 `brainstorm` 在编码前明确范围
4. **范围切片** — 将大任务按模块依赖拆分为有序切片，每个切片可独立交付
5. **选择路径** — 从四条路径（A: 新项目、B: 新功能、C: Bug 修复、D: 重构）中选择，使用对应的技能链
6. **逐切片执行** — 每个切片经历 Plan → Execute → Validate → Deliver，每个阶段转换处都有质量卡点

如果验证失败，工作会**回流**到正确的层级 — 代码级问题回到 Execute，设计级回到 Plan，需求级回到 scope。不会盲目重试。

## 工作流

```
用户请求
    │
    ▼
  上下文感知 → 难度评估 → 澄清（如需） → 范围切片
    │
    ▼
  ┌──────────────────────────────────┐
  │  逐切片循环                       │
  │                                  │
  │  路径选择（A/B/C/D）              │
  │       │                          │
  │       ▼                          │
  │  Plan ──── 卡点 ──── Execute     │
  │                        │         │
  │                      卡点        │
  │                        │         │
  │                    Validate      │
  │                        │         │
  │                    Deliver       │
  └──────────────────────────────────┘
    │
    ▼
  完成（或进入下一切片）
```

### 三级变体

| 难度 | 变体 | 差异 |
|------|------|------|
| L1-L2（简单） | **lite** | 跳过可选技能，快速自检，不强制 TDD |
| L3（中等） | **standard** | 完整技能链，强制 TDD，标准审查 |
| L4-L5（困难） | **plus** | SubAgent 隔离执行，严格 TDD，两阶段审查，并行策略 |

## 技能库

**编排**

- `orchestrator` — 全生命周期流程编排器（路由、质量卡点、回流、切片迭代）

**需求与设计**

- `requirement-qa` — 多轮 QA 引导用户明确需求
- `brainstorm` — 多视角头脑风暴，专家 SubAgent 独立分析
- `spec-writing` — 结构化功能需求文档撰写
- `tech-stack` — 全栈技术选型与决策文档

**架构与工程**

- `engineering-principles` — 上下文感知的工程原则匹配器（SOLID、DDD、TDD、设计模式）
- `api-contract-design` — RESTful/GraphQL API 契约、DTO、OpenAPI
- `error-handling-strategy` — 异常体系、错误码、重试、熔断、降级
- `performance-arch-design` — 缓存分层、异步处理、索引策略、限流
- `observability-design` — 链路追踪、结构化日志、指标、告警

**实现**

- `code-scaffold` — 从领域模型 + 设计文档生成项目代码骨架
- `implementation-complexity-analysis` — 技术风险识别、复杂度分解
- `integration-test-design` — TestContainers、契约测试、Mock 策略

**元技能**

- `task-difficulty` — 多维度难度评分（1-10）
- `project-context` — 项目结构感知与跨会话持久化
- `docs-output` — 文档产出管理（模块化 docs/ 组织）

## 安装

### 通过 skills.sh（推荐）

```bash
# 安装全部技能（中文，默认）
npx skills add YuluoY/ironware

# 安装英文版技能
npx skills add YuluoY/ironware --lang en

# 安装指定技能
npx skills add YuluoY/ironware --skill orchestrator --skill brainstorm

# 列出可用技能
npx skills add YuluoY/ironware --list
```

或通过 npm 安装：

```bash
# 安装中文技能（默认）
npx ironweave init

# 安装英文版技能
npx ironweave init --lang en
```

支持 **40+ 个 Agent**：Claude Code、GitHub Copilot、Cursor、Codex、Windsurf、Cline、OpenCode、Gemini CLI、Trae、CodeBuddy 等。

### 各 Agent 手动安装

<details>
<summary><b>Claude Code</b></summary>

```bash
git clone https://github.com/YuluoY/ironware.git ~/.claude/ironweave
mkdir -p ~/.claude/skills
ln -s ~/.claude/ironweave/skills ~/.claude/skills/ironweave
```

也可使用 Claude 插件系统 — Ironweave 自带 `.claude-plugin/plugin.json`。

</details>

<details>
<summary><b>VS Code GitHub Copilot</b></summary>

将 `skills/` 目录复制到你的项目中，然后在 `.github/copilot-instructions.md` 中添加：

```markdown
The orchestrator skill (skills/orchestrator/SKILL.md) is the main entry point.
For any development task, start by reading it.
```

或直接克隆 Ironweave — 已预配置 `.github/copilot-instructions.md`。

</details>

<details>
<summary><b>Cursor</b></summary>

```bash
git clone https://github.com/YuluoY/ironware.git
```

Ironweave 自带 `.cursorrules` 和 `.cursor-plugin/plugin.json`，可自动发现。

</details>

<details>
<summary><b>Codex (OpenAI)</b></summary>

```bash
git clone https://github.com/YuluoY/ironware.git ~/.codex/ironweave
mkdir -p ~/.agents/skills
ln -s ~/.codex/ironweave/skills ~/.agents/skills/ironweave
```

详见 [.codex/INSTALL.md](./.codex/INSTALL.md)。

</details>

<details>
<summary><b>OpenCode</b></summary>

在 `opencode.json` 中添加：

```json
{
  "plugin": ["ironweave@git+https://github.com/YuluoY/ironware.git"]
}
```

详见 [.opencode/INSTALL.md](./.opencode/INSTALL.md)。

</details>

<details>
<summary><b>Windsurf / Cline / Gemini CLI</b></summary>

Ironweave 分别自带 `.windsurfrules`、`.clinerules`、`GEMINI.md`。克隆仓库后 Agent 自动发现规则。

```bash
git clone https://github.com/YuluoY/ironware.git
```

</details>

<details>
<summary><b>Trae / CodeBuddy / 其他 Agent</b></summary>

将 `skills/` 目录复制到你的项目中，然后在 Agent 的自定义指令中添加：

> The orchestrator skill (`skills/orchestrator/SKILL.md`) is the main entry point. For any development task, start by reading it. All skills are in `skills/`, each with a `SKILL.md` containing instructions.

</details>

## 项目结构

```
ironweave/
├── skills/                          # 技能（中文）
│   ├── orchestrator/              # 流程编排器
│   │   ├── SKILL.md              # 编排器逻辑
│   │   └── references/           # 方法论文档
│   ├── brainstorm/
│   ├── spec-writing/
│   ├── code-scaffold/
│   ├── ...                        # 另外 16 个技能
│   └── docs-output/
├── skills-en/                       # 技能（英文）
├── CLAUDE.md                      # Claude Code 指令
├── AGENTS.md                      # Codex 指令
├── GEMINI.md                      # Gemini CLI 指令
├── .github/copilot-instructions.md  # VS Code Copilot
├── .cursorrules                   # Cursor 规则
├── .windsurfrules                 # Windsurf 规则
├── .clinerules                    # Cline 规则
├── .claude-plugin/plugin.json     # Claude 插件清单
├── .cursor-plugin/plugin.json     # Cursor 插件清单
├── .codex/INSTALL.md              # Codex 安装指南
├── .opencode/INSTALL.md           # OpenCode 安装指南
├── README.md
├── README_CN.md
├── CONTRIBUTING.md
├── LICENSE
└── package.json
```

## 设计理念

- **自适应路由** 而非线性工作流 — 不同任务类型需要不同的流程
- **质量卡点 + 回流** 而非通过/失败 — 失败回流到正确的阶段
- **执行前范围切片** — 大任务拆分为有序切片，每个独立可交付
- **开销随复杂度缩放** — 简单任务保持快速（lite），困难任务获得完整保障（plus）
- **技能即方法论** — 每个技能编码了决策树，不只是模板

## 贡献

请参阅 [CONTRIBUTING.md](./CONTRIBUTING.md)。技能直接存放在本仓库中。

## 许可证

[MIT](./LICENSE) © Ironweave Contributors
