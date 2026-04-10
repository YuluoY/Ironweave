# 质量卡点详细规则

## Plan 卡点判定流程

```mermaid
graph TB
    ENTER["进入 Plan 卡点"] --> P0{"P0: 粒度检查<br>当前 Slice 范围可控?"}
    P0 -->|"否: 范围过大"| FIX_SCOPE["回到 scope-sizer<br>进一步拆分"]
    P0 -->|"是"| P1{"P1: 用户明确批准?"}
    P1 -->|"否"| BLOCK["阻塞<br>等待用户确认"]
    P1 -->|"是"| P2{"P2: 有验收标准?<br>至少 1 条可验证的标准"}
    P2 -->|"否"| FIX_REQ["回到需求步骤<br>补充验收标准"]
    P2 -->|"是"| P3{"P3: 范围边界明确?<br>做什么 + 不做什么"}
    P3 -->|"否"| FIX_REQ2["回到需求步骤<br>明确范围"]
    P3 -->|"是"| P4{"P4: 技术方案可行?"}
    P4 -->|"否"| FIX_DESIGN["回到设计步骤<br>修改方案"]
    P4 -->|"是"| COND{"有条件检项?"}

    COND -->|"路径 A"| P_A{"P-A: 技术选型已锁定?"}
    COND -->|"路径 B"| P_B{"P-B: 兼容性已确认?"}
    COND -->|"路径 C"| P_C{"P-C: 修复不引入副作用?"}
    COND -->|"路径 D"| P_D{"P-D: 每步可回滚?"}
    COND -->|"无"| PASS

    P_A -->|"否"| FIX_TECH["回到技术选型"]
    P_A -->|"是"| RISK
    P_B -->|"否"| FIX_IMPACT["回到影响评估"]
    P_B -->|"是"| RISK
    P_C -->|"否"| FIX_FIX["回到修复方案"]
    P_C -->|"是"| PASS
    P_D -->|"否"| FIX_RISK["回到风险评估"]
    P_D -->|"是"| RISK

    RISK{"路径为 +变体?<br>需要风险检查"}
    RISK -->|"是"| P_RISK{"P-R: 风险均有缓解措施?"}
    RISK -->|"否"| PASS
    P_RISK -->|"否"| FIX_RISK2["回到风险评估"]
    P_RISK -->|"是"| PASS["Plan 卡点通过"]

    style ENTER fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style P0 fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c,stroke-width:2px
    style FIX_SCOPE fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style BLOCK fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style FIX_REQ fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_REQ2 fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_DESIGN fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_TECH fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_IMPACT fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_FIX fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_RISK fill:#fff3e0,stroke:#e65100,color:#bf360c
    style FIX_RISK2 fill:#fff3e0,stroke:#e65100,color:#bf360c
    style PASS fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20,stroke-width:2px
```

### P0 粒度检查规则

Plan 卡点新增的首项检查——在用户批准前先判断当前 Slice 是否**粒度合理**：

| 信号 | 判定 | 动作 |
|------|------|------|
| 当前 Slice 涉及 > 3 个模块 | 范围过大 | 回到 scope-sizer 进一步拆分 |
| 当前 Slice 的 spec 文档 > 5 个文件 | 范围过大 | 回到 scope-sizer 进一步拆分 |
| 当前 Slice 预估新增文件 > 30 个 | 范围过大 | 回到 scope-sizer 进一步拆分 |
| 以上均不超标 | 粒度正常 | 继续 P1 |

P0 检查仅在首次 Plan 卡点时执行。如果已经通过 scope-sizer 拆分过，P0 直接通过。

## Validate 卡点判定流程

```mermaid
graph TB
    ENTER["进入 Validate 卡点"] --> V0{"V0: Execute 完整性<br>（标准+以上变体）"}
    V0 -->|"不通过"| RF_C0["代码级回流<br>回到 Execute 补齐"]
    V0 -->|"通过 / lite跳过"| V1{"V1: 实现与 spec 一致?<br>（Slice 级复验）"}
    V1 -->|"否"| V1_SEV{"偏差来源?"}
    V1_SEV -->|"spec 本身有误"| RF_R["需求级回流"]
    V1_SEV -->|"方案设计遗漏"| RF_D["设计级回流"]
    V1_SEV -->|"实现偏差"| RF_C1["代码级回流"]
    V1 -->|"是"| V2{"V2: 核心路径测试通过?"}

    V2 -->|"否"| RF_C2["代码级回流"]
    V2 -->|"是"| V3{"V3: 无新增 lint/type 错误?"}

    V3 -->|"否"| RF_C3["代码级回流"]
    V3 -->|"是"| V_COND{"有条件检项?"}

    V_COND -->|"路径 B/C"| V4{"V4: 回归测试通过?"}
    V_COND -->|"路径 D"| V5{"V5: 行为等价?"}
    V_COND -->|"无"| V_PLUS

    V4 -->|"否"| V4_SEV{"回归失败原因?"}
    V4_SEV -->|"方案缺陷"| RF_D2["设计级回流"]
    V4_SEV -->|"代码问题"| RF_C4["代码级回流"]
    V4 -->|"是"| V_PLUS{"路径为 +变体?"}

    V5 -->|"否"| V5_SEV{"等价失败原因?"}
    V5_SEV -->|"重构方案有误"| RF_D3["设计级回流"]
    V5_SEV -->|"实现错误"| RF_C5["代码级回流"]
    V5 -->|"是"| V_PLUS

    V_PLUS -->|"是"| V6{"V6: 边界场景覆盖?"}
    V_PLUS -->|"否"| PASS

    V6 -->|"否"| RF_C6["代码级回流<br>补充边界测试"]
    V6 -->|"是"| PASS["Validate 通过"]

    style ENTER fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style V0 fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c,stroke-width:2px
    style RF_C0 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style RF_R fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style RF_D fill:#ffe0b2,stroke:#e65100,color:#bf360c
    style RF_D2 fill:#ffe0b2,stroke:#e65100,color:#bf360c
    style RF_D3 fill:#ffe0b2,stroke:#e65100,color:#bf360c
    style RF_C1 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style RF_C2 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style RF_C3 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style RF_C4 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style RF_C5 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style RF_C6 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style PASS fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20,stroke-width:2px
```

### V0 Execute 完整性检查

V0 是 Validate 的首项检查——验证 Execute 阶段的**过程质量**而非仅看最终结果。

| 变体 | V0 检查内容 | 不通过动作 |
|------|-----------|----------|
| **lite / fast** | **跳过** V0，直接进 V1 | — |
| **标准** | 每个任务完成了 TDD 循环（有测试覆盖）；全量测试通过 | 回到 Execute 补测试 |
| **+ 变体** | 每个任务通过两阶段审查（Spec 合规 + 代码质量）；无任务处于 BLOCKED/NEEDS_CONTEXT 状态 | 回到 Execute 补齐审查或解决阻塞 |

V0 检查的是 Execute 过程的**完备性**，不是代码正确性（那是 V1-V3 的职责）。如果 V0 不通过，说明 Execute 阶段有步骤被跳过，需要回去补齐。

### V1 说明（增强）

V1 在融合后承担 **Slice 级的 Spec 合规复验**。与 Execute 中 task 级的 Spec 合规审查的区别：

| 维度 | Execute Task 审查 | Validate V1 |
|------|-----------------|-------------|
| 粒度 | 单个 task vs 其对应的 spec 片段 | 整个 Slice 的全部 task 组合 vs 完整 spec |
| 视角 | 局部正确性 | 全局一致性 — 任务间的衔接、遗漏、冲突 |
| 场景 | task 内 | 跨 task 集成后 |

## 回流层级判定

```mermaid
graph TB
    FAIL["Validate 不通过<br>有回流项"] --> COUNT{"同一问题<br>已回流几次?"}
    COUNT -->|">= 2 次"| HUMAN["暂停<br>请求用户介入"]
    COUNT -->|"< 2 次"| LEVEL{"最高回流层级?"}

    LEVEL -->|"范围级"| SNAP_S["中间快照<br>已确认产出物落盘"]
    SNAP_S --> ACT_S["回到 scope-sizer<br>重新拆分 Slice<br>当前 Slice 过大无法在一次通过中完成"]
    LEVEL -->|"需求级"| SNAP_R["中间快照<br>决策存档"]
    SNAP_R --> ACT_R["回到 Plan 需求步骤<br>重新 QA 或重写 spec<br>重过完整 Plan 后 Execute 再 Validate"]
    LEVEL -->|"设计级"| ACT_D["回到 Plan 设计步骤<br>修改方案<br>重过 Plan 卡点后 Execute 再 Validate"]
    LEVEL -->|"代码级"| ACT_C["回到 Execute<br>修复代码<br>重过 Validate"]

    style FAIL fill:#f5f5f5,stroke:#616161,color:#212121
    style HUMAN fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c,stroke-width:2px
    style SNAP_S fill:#fff9c4,stroke:#f9a825,color:#e65100,stroke-width:2px
    style SNAP_R fill:#fff9c4,stroke:#f9a825,color:#e65100,stroke-width:2px
    style ACT_S fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style ACT_R fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style ACT_D fill:#ffe0b2,stroke:#e65100,color:#bf360c
    style ACT_C fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
```

### 范围级回流触发条件

当 Validate 阶段发现以下情况时，触发范围级回流：
- Execute 过程中发现当前 Slice 实际涉及的模块或文件远超预期
- 测试覆盖范围过大导致无法在合理时间内完成
- 代码生成量超过上下文窗口承载能力

范围级回流后，回到 scope-sizer 将当前 Slice 进一步拆分为更小的子 Slice。

---

## 回流中间快照（强制）

当触发**范围级**或**需求级**回流时，在跳转到回流目标之前，必须先输出一份中间快照。这是回流动作的一部分，不是独立步骤——模型在输出回流结论时直接附带快照。

**设计级**和**代码级**回流影响范围小，不需要快照。

### 触发规则

| 回流层级 | 是否快照 | 原因 |
|---------|---------|------|
| 范围级 | **是（强制）** | 当前 Slice 将被拆分，已完成的部分产出必须落盘，否则子 Slice 无法感知 |
| 需求级 | **是（强制）** | 需求可能被颠覆，之前的设计决策需要存档以便对比 |
| 设计级 | 否 | 仅修改方案，spec 变化在 Plan 重做时覆盖即可 |
| 代码级 | 否 | 仅修复代码，无文档/上下文变化 |

### 快照输出格式

回流结论后直接附带，作为回流输出模板的一部分：

```markdown
### 回流中间快照

**当前 Slice**: S2 — 核心域
**回流层级**: 范围级 / 需求级
**触发原因**: [具体原因]

#### 已确认产出物（需落盘）
| 产出物 | 目标路径 | 状态 |
|--------|---------|------|
| 技术选型文档 | docs/tech-stack.md | ✅ 已同步 |
| S1 API 契约 | docs/api/auth.md | ✅ 已同步 |
| S2 需求 spec | docs/novel/spec.md | ⚠️ 需写入 |

#### 需要持久化的决策
- [决策1]: ...
- [决策2]: ...

#### 动作
1. 写入上述 ⚠️ 标记的文件
2. 更新 .cache/context.db（增量同步涉及的模块）
3. 更新 docs/progress/ 状态（标记当前 Slice 为"回流中"）
4. 跳转到 [回流目标]
```

### 快照执行方式

- **不派 SubAgent**：主 agent 直接写文件，减少开销
- **仅写变更部分**：不做全量同步，只把"已确认但未落盘"的产出物写入
- **快照完成后**：再执行回流跳转

---

## 卡点输出格式

每次卡点检查后输出：

```markdown
### ✅ / ❌ [Plan / Validate] 卡点检查

| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| P0 | 粒度检查 | ✅ | Slice 范围 2 模块 · 4 功能点 |
| P1 | 用户批准 | ✅ | 用户回复"确认" |
| P2 | 验收标准 | ✅ | 3 条验收标准 |
| P3 | 范围边界 | ❌ | 未说明"不做什么" |
| P4 | 技术可行 | ✅ | — |

**结论**: ❌ 不通过
**不通过原因**: P3 — 范围边界不明确
**建议动作**: 回到需求步骤，补充"本次不做"清单
**回流目标**: Plan → 需求 QA
```

---

## ⛔ Phase Chain Guard 集成

卡点检查输出后，**必须**调用 `phase_guard.py gate` 记录结果。这是机械化证据链，不可跳过。

### Plan 卡点通过后

```bash
python3 skills/project-context/scripts/phase_guard.py gate \
  --root . --slice <SN> --phase plan --result pass \
  --outputs '[{"path":"docs/plan.md"},{"path":"docs/spec.md"}]'
```

### Plan 卡点失败后

```bash
python3 skills/project-context/scripts/phase_guard.py gate \
  --root . --slice <SN> --phase plan --result fail
```

### Validate 卡点通过后

```bash
python3 skills/project-context/scripts/phase_guard.py gate \
  --root . --slice <SN> --phase validate --result pass
```

### Validate 卡点失败后（触发回流）

```bash
python3 skills/project-context/scripts/phase_guard.py gate \
  --root . --slice <SN> --phase validate --result fail
```

回流修复完成后，重新进入对应阶段时 `phase_guard.py enter` 会正常放行（因为它检查的是**前置**阶段的 gate-pass，不是当前阶段）。
