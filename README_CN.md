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

### 通过 npm

```bash
# 安装全部技能 + 全部编辑器配置（中文，默认）
npx ironweave@latest init

# 安装英文版技能
npx ironweave@latest init --lang en

# 只安装特定编辑器的配置
npx ironweave@latest init --agent cursor
npx ironweave@latest init --agent trae
npx ironweave@latest init --agent windsurf

# 只复制 skills/，不安装编辑器配置
npx ironweave@latest init --skills-only

# 覆盖已有文件
npx ironweave@latest init --force

# 列出所有可用技能
npx ironweave@latest list
```

可选编辑器：`claude`、`copilot`、`cursor`、`windsurf`、`cline`、`trae`、`codebuddy`、`codex`、`gemini`、`all`（默认全部）。

> **冲突处理**：默认不覆盖已有文件。Ironweave 会将配置与你现有的规则并存。使用 `--force` 强制覆盖。

> **Skills 位置**：指定单个目录型编辑器时（如 `--agent trae`），skills 会安装到该编辑器目录内（如 `.trae/skills/`）。使用 `--agent all`（默认）时，skills 安装在项目根目录 `skills/`。

### 通过 skills.sh

```bash
# 安装到指定编辑器（推荐）
npx skills add YuluoY/ironweave --skill '*' -a cursor -y
npx skills add YuluoY/ironweave --skill '*' -a trae -y
npx skills add YuluoY/ironweave --skill '*' -a claude-code -y

# 安装到多个编辑器
npx skills add YuluoY/ironweave --skill '*' -a cursor -a windsurf -y

# 安装到所有编辑器（会生成很多 agent 目录）
npx skills add YuluoY/ironweave --all

# 交互式选择技能和编辑器
npx skills add YuluoY/ironweave

# 列出可用技能
npx skills add YuluoY/ironweave --list
```

skills.sh 的 Agent 名称：`claude-code`、`github-copilot`、`cursor`、`windsurf`、`cline`、`trae`、`codebuddy`、`codex`、`gemini-cli`。

> 注意：`skills.sh` 不支持 `--lang` 参数。如需英文版，请使用 `npx ironweave@latest init --lang en`。

### 各 Agent 手动安装

<details>
<summary><b>Claude Code</b></summary>

Ironweave 自带项目根目录的 `CLAUDE.md` — Claude Code 会自动读取。

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>VS Code GitHub Copilot</b></summary>

Ironweave 已预配置 `.github/copilot-instructions.md`。

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>Cursor</b></summary>

Ironweave 自带 `.cursor/rules/ironweave.mdc`（`alwaysApply: true`），可自动发现。

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>Windsurf</b></summary>

Ironweave 自带 `.windsurf/rules/ironweave.md`（`trigger: always_on`），可自动发现。

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>Cline</b></summary>

Ironweave 自带 `.clinerules/ironweave.md`，可自动发现。

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>Trae</b></summary>

Ironweave 自带 `.trae/rules/ironweave.md`，可自动发现。

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>CodeBuddy（腾讯云）</b></summary>

Ironweave 自带 `.codebuddy/rules/ironweave/RULE.mdc`（`alwaysApply: true`），可自动发现。

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>Codex (OpenAI)</b></summary>

Ironweave 自带项目根目录的 `AGENTS.md` — Codex 会自动读取。

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

<details>
<summary><b>Gemini CLI</b></summary>

Ironweave 自带项目根目录的 `GEMINI.md` — Gemini CLI 会自动读取。

```bash
git clone https://github.com/YuluoY/ironweave.git
```

</details>

## 项目结构

```
ironweave/
├── skills/                            # 技能（中文）
│   ├── orchestrator/                # 流程编排器
│   │   ├── SKILL.md                # 编排器逻辑
│   │   └── references/             # 方法论文档
│   ├── brainstorm/
│   ├── spec-writing/
│   ├── code-scaffold/
│   ├── ...                          # 共 16 个技能
│   └── docs-output/
├── skills-en/                         # 技能（英文）
├── CLAUDE.md                        # Claude Code
├── AGENTS.md                        # Codex / 跨 Agent 兼容
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
