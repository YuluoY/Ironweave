# A：新项目

## Plan

### 首个 Slice（或单 slice 模式）

首个 Slice 执行完整 Plan skill 链，产出全局性文档（tech-stack、engineering-principles 等）。

> **注意**：如果 CLARIFY 阶段已执行，Plan 中的 requirement-qa 切换为 **slice 模式**（仅问 S1 具体功能细节，不重复宏观问题）；brainstorm 默认**跳过**（CLARIFY 已做架构讨论），除非 S1 内出现新的架构争议才触发。

```mermaid
graph TB
    START["A 启动<br>Slice 1 或单 slice"] --> CLARITY{"需求清晰度?<br>（slice 级）"}
    CLARITY -->|"功能细节不明"| QA_FULL["requirement-qa<br>slice 模式 — S1 细节"]
    CLARITY -->|"大致清晰"| QA_LIGHT["requirement-qa<br>补充 S1 细节"]
    CLARITY -->|"清晰"| SKIP_QA["跳过 QA"]

    QA_FULL --> BRAIN_CHK
    QA_LIGHT --> BRAIN_CHK
    SKIP_QA --> BRAIN_CHK

    BRAIN_CHK{"L4+ 且<br>CLARIFY 未做?"}
    BRAIN_CHK -->|"是"| BRAIN["brainstorm<br>多视角方案"]
    BRAIN_CHK -->|"否"| SPEC
    BRAIN --> SPEC["spec-writing<br>需求文档"]

    SPEC --> TECH["tech-stack<br>技术选型"]
    TECH --> ENG{"L3+?"}
    ENG -->|"是"| ENG_DO["engineering-principles<br>原则匹配"]
    ENG -->|"否"| API
    ENG_DO --> API["api-contract-design<br>API 契约"]

    API --> ERR{"L3+?"}
    ERR -->|"是"| ERR_DO["error-handling-strategy"]
    ERR -->|"否"| ADV_CHK
    ERR_DO --> ADV_CHK{"L4+?"}

    ADV_CHK -->|"是"| ADV["SubAgent 并行:<br>performance-arch-design<br>implementation-complexity-analysis<br>observability-design"]
    ADV_CHK -->|"否"| DOCS
    ADV --> DOCS["docs-output<br>文档初始化"]
    DOCS --> GATE["Plan 卡点"]

    style QA_FULL fill:#e8eaf6,stroke:#283593,color:#1a237e
    style QA_LIGHT fill:#e8eaf6,stroke:#283593,color:#1a237e
    style BRAIN fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style SPEC fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style TECH fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style ENG_DO fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style API fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style ERR_DO fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style ADV fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style DOCS fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style GATE fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
```

### 后续 Slice（多 slice 模式时）

后续 Slice 跳过全局性 skill（tech-stack、engineering-principles、error-handling-strategy），只执行 slice 级增量 skill。requirement-qa 始终为 **slice 模式**，brainstorm **跳过**（CLARIFY 已做）。

```mermaid
graph TB
    START_N["A 启动<br>Slice N (N > 1)"] --> CTX_READ["读取前置 Slice 产出<br>docs/ + .cache/context.db"]
    CTX_READ --> QA_SLICE["requirement-qa<br>slice 模式 — 本 slice 细节"]
    QA_SLICE --> SPEC_SLICE["spec-writing<br>仅本 slice 六段式"]
    SPEC_SLICE --> API_SLICE["api-contract-design<br>增量端点"]
    API_SLICE --> DOCS_SLICE["docs-output<br>增量同步"]
    DOCS_SLICE --> GATE_N["Plan 卡点"]

    style START_N fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style CTX_READ fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style QA_SLICE fill:#e8eaf6,stroke:#283593,color:#1a237e
    style SPEC_SLICE fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style API_SLICE fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style DOCS_SLICE fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style GATE_N fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
```

### 变体差异

| Skill | A-lite | A | A+ |
|-------|--------|---|-----|
| requirement-qa | 轻量 | 标准 | 深度 |
| brainstorm | 跳过 | 跳过 | CLARIFY 未做则必做；CLARIFY 已做则跳过 |
| spec-writing | 要点列表 | 六段式 | 六段式 |
| tech-stack | 默认模板 | 完整选型 | 完整选型 |
| engineering-principles | 跳过 | 标准 | 多模式匹配 |
| api-contract-design | 端点列表 | 完整契约 | 完整契约 |
| error-handling-strategy | 跳过 | 标准 | 标准 |
| SubAgent 三件套 | 跳过 | 跳过 | 并行执行 |
| docs-output | 最小化 | 初始化 | 完整初始化 |

> brainstorm 仅在 A+（L4-L5）变体中且 **CLARIFY 阶段未执行** 时必做。如果 CLARIFY 已完成架构讨论，Plan 中的 brainstorm 跳过。

---

## Execute

通用执行流程（任务分解 → TDD 循环 → 审查 → 汇合）→ 读取 `references/execute.md`。以下为 Route A 的**特化规则**：

### 首个 Slice

任务分解时必须遵守：

| # | 强制任务 | 说明 |
|---|---------|------|
| Task 1 | `code-scaffold` | 生成完整项目骨架（目录结构、构建配置、公共模块） |
| 最后 | `integration-test-design` | 设计集成测试框架和策略 |
| 中间 | 本 slice 模块编码 | 按 TDD 循环逐 task 执行 |

```mermaid
graph TB
    E1["Task 1: code-scaffold<br>完整项目骨架"] --> E2["Task 2..N: 模块编码<br>TDD: RED-GREEN-REFACTOR"]
    E2 --> E3["Task N+1: integration-test-design<br>集成测试方案"]
    E3 --> E4["汇合: 全量测试 + lint"]

    style E1 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style E2 fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E3 fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E4 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
```

### 后续 Slice

- `code-scaffold` **跳过**（骨架已存在），Task 1 直接是模块编码
- `integration-test-design` 做增量（仅本 slice 新增模块的集成测试）

```mermaid
graph TB
    E1_N["Task 1..N: 在已有骨架上<br>新增模块编码 (TDD)"] --> E2_N["Task N+1: integration-test-design<br>增量集成测试"]
    E2_N --> E3_N["汇合: 全量测试 + lint"]

    style E1_N fill:#fff9c4,stroke:#f9a825,color:#e65100
    style E2_N fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E3_N fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
```
