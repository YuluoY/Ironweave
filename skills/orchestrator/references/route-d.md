# D：重构

## Plan

> **注意**：如果 CLARIFY 阶段已执行架构讨论，Plan 中的 brainstorm 默认**跳过**，除非重构过程中发现新的策略争议。

```mermaid
graph TB
    START["D 启动"] --> CTX["project-context<br>读取架构全貌"]
    CTX --> ASSESS["现状评估<br>问题识别 + 影响范围"]

    ASSESS --> BRAIN_CHK{"L4+ 且<br>CLARIFY 未做?"}
    BRAIN_CHK -->|"是"| BRAIN["brainstorm<br>评估重构策略"]
    BRAIN_CHK -->|"否"| PLAN_REF
    BRAIN --> PLAN_REF["重构方案<br>目标架构 + 迁移路径"]

    PLAN_REF --> ENG{"L3+?"}
    ENG -->|"是"| ENG_DO["engineering-principles<br>验证方案合规性"]
    ENG -->|"否"| RISK
    ENG_DO --> PERF_CHK{"L4+?"}
    PERF_CHK -->|"是"| PERF["performance-arch-design<br>性能重设计"]
    PERF_CHK -->|"否"| RISK
    PERF --> RISK["风险评估<br>回归风险 + 回滚能力"]

    RISK --> DOCS_CHK{"L3+?"}
    DOCS_CHK -->|"是"| DOCS["docs-output<br>增量同步"]
    DOCS_CHK -->|"否"| GATE
    DOCS --> GATE["Plan 卡点"]

    style CTX fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style ASSESS fill:#fff3e0,stroke:#e65100,color:#bf360c
    style BRAIN fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style PLAN_REF fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style ENG_DO fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style PERF fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style RISK fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style DOCS fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style GATE fill:#fff3e0,stroke:#e65100,color:#bf360c,stroke-width:2px
```

### 变体差异

| Skill | D-lite | D | D+ |
|-------|--------|---|-----|
| project-context | 读取架构 | 读取架构 | 读取架构 |
| 现状评估 | 快速 | 标准 | 深度 |
| brainstorm | 跳过 | 跳过 | CLARIFY 未做则必做；CLARIFY 已做则跳过 |
| 重构方案 | 简要 | 标准 | 详细 + 迁移计划 |
| engineering-principles | 跳过 | 标准验证 | 深度验证 |
| performance-arch-design | 跳过 | 跳过 | 性能重设计 |
| 风险评估 | 跳过 | 标准 | 详细 + 回滚方案 |
| docs-output | 跳过 | 增量同步 | 增量同步 |

---

## Execute

通用执行流程（任务分解 → TDD 循环 → 审查 → 汇合）→ 读取 `references/execute.md`。Route D 的**特化规则**：

- **无 scaffold** — 重构不新建项目/模块骨架
- **核心原则**：每个 task 完成后**原有测试必须全部通过**（行为等价）
- `integration-test-design` **仅在跨层重构时触发**
- **不允许积累**：不允许多个 task 完成后再统一测试，每个 task 后立即验证等价性

```mermaid
graph TB
    E1["Task 1..N: 按重构方案分步编码<br>TDD + 每步行为等价验证"] --> E2{"跨层变更?"}
    E2 -->|"是"| E3["Task N+1: integration-test-design<br>迁移验证测试"]
    E2 -->|"否"| E4["汇合: 全量测试<br>确认行为等价"]
    E3 --> E4

    style E1 fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E3 fill:#e8eaf6,stroke:#283593,color:#1a237e
    style E4 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
```
