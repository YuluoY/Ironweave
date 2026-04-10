<p align="center">
  <h1 align="center">Nimis</h1>
  <p align="center">
    面向 AI 编程 Agent 的技能框架与软件开发方法论。
  </p>
  <p align="center">
    <a href="./README.md">English</a> · <a href="https://skills.sh">skills.sh</a> · <a href="#安装">安装</a> · <a href="./LICENSE">MIT 许可证</a>
  </p>
</p>

---

Nimis 是一套完整的软件开发工作流，由一组可自由组合的 **技能（Skills）** 构建而成。它不只是写代码 — 它会先理解你要构建什么，制定计划，将工作拆分为切片，然后通过内置质量卡点逐一执行每个切片。而且这些技能会自动触发，你不需要做任何特殊操作。你的 Agent 拥有 Nimis 就够了。

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
npx nimis@latest init

# 安装英文版技能
npx nimis@latest init --lang en

# 只安装特定编辑器的配置
npx nimis@latest init --agent cursor
npx nimis@latest init --agent trae
npx nimis@latest init --agent windsurf

# 只复制 skills/，不安装编辑器配置
npx nimis@latest init --skills-only

# 覆盖已有文件
npx nimis@latest init --force

# 列出所有可用技能
npx nimis@latest list
```

可选编辑器：`claude`、`copilot`、`cursor`、`windsurf`、`cline`、`trae`、`codebuddy`、`codex`、`gemini`、`all`（默认全部）。

> **冲突处理**：默认不覆盖已有文件。Nimis 会将配置与你现有的规则并存。使用 `--force` 强制覆盖。

> **Skills 位置**：指定单个目录型编辑器时（如 `--agent trae`），skills 会安装到该编辑器目录内（如 `.trae/skills/`）。使用 `--agent all`（默认）时，skills 安装在项目根目录 `skills/`。

### 通过 skills.sh

```bash
# 安装到指定编辑器（推荐）
npx skills add YuluoY/nimis --skill '*' -a cursor -y
npx skills add YuluoY/nimis --skill '*' -a trae -y
npx skills add YuluoY/nimis --skill '*' -a claude-code -y

# 安装到多个编辑器
npx skills add YuluoY/nimis --skill '*' -a cursor -a windsurf -y

# 安装到所有编辑器（会生成很多 agent 目录）
npx skills add YuluoY/nimis --all

# 交互式选择技能和编辑器
npx skills add YuluoY/nimis

# 列出可用技能
npx skills add YuluoY/nimis --list
```

skills.sh 的 Agent 名称：`claude-code`、`github-copilot`、`cursor`、`windsurf`、`cline`、`trae`、`codebuddy`、`codex`、`gemini-cli`。

> 注意：`skills.sh` 不支持 `--lang` 参数。如需英文版，请使用 `npx nimis@latest init --lang en`。

### 各 Agent 手动安装

<details>
<summary><b>Claude Code</b></summary>

Nimis 自带项目根目录的 `CLAUDE.md` — Claude Code 会自动读取。

```bash
git clone https://github.com/YuluoY/nimis.git
```

</details>

<details>
<summary><b>VS Code GitHub Copilot</b></summary>

Nimis 已预配置 `.github/copilot-instructions.md`。

```bash
git clone https://github.com/YuluoY/nimis.git
```

</details>

<details>
<summary><b>Cursor</b></summary>

Nimis 自带 `.cursor/rules/nimis.mdc`（`alwaysApply: true`），可自动发现。

```bash
git clone https://github.com/YuluoY/nimis.git
```

</details>

<details>
<summary><b>Windsurf</b></summary>

Nimis 自带 `.windsurf/rules/nimis.md`（`trigger: always_on`），可自动发现。

```bash
git clone https://github.com/YuluoY/nimis.git
```

</details>

<details>
<summary><b>Cline</b></summary>

Nimis 自带 `.clinerules/nimis.md`，可自动发现。

```bash
git clone https://github.com/YuluoY/nimis.git
```

</details>

<details>
<summary><b>Trae</b></summary>

Nimis 自带 `.trae/rules/nimis.md`，可自动发现。

```bash
git clone https://github.com/YuluoY/nimis.git
```

</details>

<details>
<summary><b>CodeBuddy（腾讯云）</b></summary>

Nimis 自带 `.codebuddy/rules/nimis/RULE.mdc`（`alwaysApply: true`），可自动发现。

```bash
git clone https://github.com/YuluoY/nimis.git
```

</details>

<details>
<summary><b>Codex (OpenAI)</b></summary>

Nimis 自带项目根目录的 `AGENTS.md` — Codex 会自动读取。

```bash
git clone https://github.com/YuluoY/nimis.git
```

</details>

<details>
<summary><b>Gemini CLI</b></summary>

Nimis 自带项目根目录的 `GEMINI.md` — Gemini CLI 会自动读取。

```bash
git clone https://github.com/YuluoY/nimis.git
```

</details>

## 项目结构

```
nimis/
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
├── .cursor/rules/nimis.mdc        # Cursor
├── .windsurf/rules/nimis.md       # Windsurf
├── .clinerules/nimis.md           # Cline
├── .trae/rules/nimis.md           # Trae
├── .codebuddy/rules/nimis/RULE.mdc  # CodeBuddy
├── README.md
├── README_CN.md
├── CONTRIBUTING.md
├── LICENSE
└── package.json
```

## 设计理念

### 核心原则

**文档驱动开发** — 文档先于代码。每个功能以结构化文档（`specs/`）启动，成为需求、技术决策和 API 契约的唯一真相来源。代码实现文档，而非文档回溯描述代码。

**全链路可追溯** — 每个技术决策都记录*为什么选它*和*对比过哪些备选*。进度通过 `docs/` 持续追踪，跨会话上下文通过 SQLite 持久化。没有任何环节依赖记忆。

**对抗 AI 认知弱点** — AI 代理天然低估复杂度、跳过验证、跨会话遗忘上下文、遗忘计划。Nimis 的机制直接针对这些弱点：路径锁定防跳步，难度节流阀防低估，文件持久化防遗忘，机械对账防遗漏。

**人定策略，机器执行** — 系统提供默认值和推荐方案，但人类拥有无条件覆盖权。技术选型是推荐而非强制，难度评分可随时用自然语言覆盖。AI 执行工作流，人类掌握决策权。

**开销自适应** — 流程重量匹配问题重量。简单任务（lite）跳过可选 skill 保持快速，中等任务（standard）走完整链路，困难任务（plus）增加额外评审和并行策略。拒绝一刀切。

### 设计机制

- **路径锁定** — 路由流程图是强制执行路线，不是参考。每个节点按箭头顺序执行，禁止跳过。
- **节流阀** — 难度评估内置上浮偏差。因为 AI 倾向于低估复杂度，评分主动上浮——除非明确简单。
- **落盘即释放** — 每个 skill 产出写入文件后，后续步骤从文件读取，不依赖上下文窗口。对抗注意力衰减。
- **精准回流** — 验证失败时按偏差来源精准回退（代码级→Execute，设计级→Plan，需求级→范围），而非全盘推翻。
- **机械对账** — 交付时以清单对比（Plan 产出 vs 实际文件），信任文件系统而非模型记忆。
- **推荐不等于强制** — 技术参考表提供默认推荐，但只要说明理由，任何技术都是合法选择。

## 贡献

请参阅 [CONTRIBUTING.md](./CONTRIBUTING.md)。技能直接存放在本仓库中。

## 许可证

[MIT](./LICENSE) © Nimis Contributors
