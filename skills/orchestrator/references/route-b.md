# B：已有项目新功能

⛔ **路径锁定**：本路径的 Mermaid 流程图是强制执行路线，不是参考。每个节点必须按图中箭头顺序执行，条件分支按实际情况走对应分支。禁止跳过任何节点、禁止提前退出。每完成一个节点后，沿箭头进入下一个。

---

## Plan

> **注意**：如果 CLARIFY 阶段已执行，Plan 中的 requirement-qa 切换为 **slice 模式**（仅问当前 slice 的功能细节和影响范围，不重复宏观问题）；brainstorm 默认**跳过**（CLARIFY 已做架构讨论），除非 slice 内出现新的实现方案争议才触发。

```mermaid
graph TB
    START["B 启动"] --> CTX["project-context<br>读取现有架构"]
    CTX --> CLARITY{"需求清晰度?<br>（slice 级）"}
    CLARITY -->|"模糊"| QA["requirement-qa<br>聚焦功能边界"]
    CLARITY -->|"半清晰"| QA_C["requirement-qa<br>澄清约束"]
    CLARITY -->|"清晰"| SKIP_QA["跳过 QA"]

    QA --> BRAIN_CHK
    QA_C --> BRAIN_CHK
    SKIP_QA --> BRAIN_CHK

    BRAIN_CHK{"L4+ 且<br>CLARIFY 未做?"}
    BRAIN_CHK -->|"是"| BRAIN["brainstorm<br>评估实现方案"]
    BRAIN_CHK -->|"否"| IMPACT
    BRAIN --> IMPACT["影响评估<br>兼容性 + 回归范围"]

    IMPACT --> SPEC["spec-writing<br>增量需求文档"]
    SPEC --> API_CHK{"涉及新 API?"}
    API_CHK -->|"是"| API["api-contract-design<br>增量契约"]
    API_CHK -->|"否"| ENG_CHK
    API --> ENG_CHK{"涉及架构变更?"}
    ENG_CHK -->|"是"| ENG["engineering-principles"]
    ENG_CHK -->|"否"| ERR_CHK
    ENG --> ERR_CHK{"L4+?"}
    ERR_CHK -->|"是"| ERR["error-handling-strategy"]
    ERR_CHK -->|"否"| DOCS
    ERR --> DOCS["docs-output<br>增量同步"]
    DOCS --> GATE["Plan 卡点"]

    style CTX fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style QA fill:#e8eaf6,stroke:#283593,color:#1a237e
    style QA_C fill:#e8eaf6,stroke:#283593,color:#1a237e
    style BRAIN fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style IMPACT fill:#fff3e0,stroke:#e65100,color:#bf360c
    style SPEC fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style API fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style ENG fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style ERR fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style DOCS fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style GATE fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
```

### 变体差异

| Skill | B-lite | B | B+ |
|-------|--------|---|-----|
| project-context | 读取 | 读取 | 读取 |
| requirement-qa | 快速澄清 | 标准 | 深度 |
| brainstorm | 跳过 | 跳过 | CLARIFY 未做则必做；CLARIFY 已做则跳过 |
| 影响评估 | 跳过 | 标准 | 深度 |
| spec-writing | 增量 | 增量 | 增量 |
| api-contract-design | 按需 | 按需 | 按需 |
| engineering-principles | 跳过 | 按需 | 按需 |
| error-handling-strategy | 跳过 | 跳过 | 标准 |
| docs-output | 跳过 | 增量同步 | 增量同步 |

---

## Execute

通用执行流程（任务分解 → TDD 循环 → 审查 → 汇合）→ 读取 `references/execute.md`。以下为 Route B 的**特化规则**：

| 条件 | 任务分解特殊处理 |
|------|----------------|
| **新增模块** | Task 1 = 该模块的 `code-scaffold`（模块级，非项目级） |
| **跨模块集成** | 必须包含 `integration-test-design` 增量任务 |
| **单模块内部** | 无特殊要求，按通用 TDD 流程 |

```mermaid
graph TB
    E1{"新模块?"}
    E1 -->|"是"| E2["Task 1: code-scaffold<br>模块骨架"]
    E1 -->|"否"| E3["Task 1..N: 功能编码<br>TDD: RED-GREEN-REFACTOR"]
    E2 --> E3
    E3 --> E4{"跨模块集成?"}
    E4 -->|"是"| E5["Task N+1: integration-test-design<br>增量集成测试"]
    E4 -->|"否"| E6["汇合: 全量测试 + lint"]
    E5 --> E6

    style E2 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style E3 fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E5 fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E6 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
```
