---
name: engineering-principles
description: >-
  工程原则匹配器——根据当前任务和项目上下文，从原则库中筛选出适用的开发原则和约束，输出可执行的指导清单到 specs/engineering-principles.md。不强推不适用的原则（如无测试依赖的旧项目不推TDD），只输出经上下文验证后确实适用的原则。被动调用，不会主动触发。
  务必在以下场景使用本 skill：编码规范、设计原则、架构指导、代码质量、可维护性、可扩展性、TDD、DDD、SOLID、设计模式、工程实践、代码审查、engineering principles、code quality、best practices、ddd、tdd、bdd、solid、clean code、重构建议。
---

# 工程原则匹配器

本 Skill 解决一个核心问题：**模型写代码时缺乏工程纪律**。不是所有原则都适用于所有项目——旧项目没有测试框架就不该强推 TDD，小项目不需要 DDD 分层。

本 Skill 的核心逻辑：**先感知项目上下文 → 再匹配适用原则 → 输出可执行约束**。

## 核心机制

```mermaid
graph LR
    TASK["当前任务"]
    CTX["项目上下文扫描<br/>技术栈·测试框架·项目规模·目录结构"]
    MATCH["原则匹配<br/>上下文条件 → 适用原则"]
    OUT["输出<br/>适用原则清单 + DO/DON'T"]

    TASK --> CTX --> MATCH --> OUT

    style TASK fill:#e3f2fd,stroke:#1976d2
    style CTX fill:#fff3e0,stroke:#f57c00
    style MATCH fill:#f3e5f5,stroke:#7b1fa2
    style OUT fill:#e8f5e9,stroke:#388e3c
```

## 原则分类与适用条件

每个原则类别有明确的**适用前置条件**——条件不满足则跳过。

| 分类 | 包含原则 | 适用条件 |
|------|---------|---------|
| **SOLID** | SRP, OCP, LSP, ISP, DIP | 项目使用 OOP 语言（TS/Java/Python class） |
| **DDD 分层** | 聚合、限界上下文、领域服务、值对象 | 项目有明确的业务领域且模块 ≥ 3 个 |
| **TDD** | 红绿重构、测试先行、测试金字塔 | 项目已配置测试框架（jest/vitest/junit/pytest） |
| **BDD** | Gherkin 验收、场景驱动 | 项目有 E2E 测试工具（cypress/playwright） |
| **设计模式** | 小尺度(Guard Clause/表驱动/Pipe)、经典GoF(工厂/建造者/装饰器/策略/观察者/状态机/命令/责任链)、中尺度(管道/断路器/工作池/仓库)、前端/后端/跨域模式 | 代码中存在可识别的模式适用场景 |
| **架构模式** | 分层架构、六边形/Clean Architecture、微内核/插件、模块化单体、微服务、事件驱动、Serverless | 涉及系统架构决策或项目初始化 |
| **反模式** | 上帝对象、循环依赖、散弹式修改、过度抽象、贫血模型等 | 代码审查或重构任务 |
| **Clean Code** | 命名、函数长度、注释、可读性 | **始终适用**（无条件） |
| **错误处理** | 异常分级、边界校验、防御式编程 | **始终适用**（无条件） |
| **可测试性** | 依赖注入、纯函数、接口隔离 | 项目有测试框架 或 新建项目 |
| **性能意识** | 避免 N+1、懒加载、缓存策略 | 涉及数据库查询或 API 调用的任务 |
| **安全实践** | 输入校验、SQL 注入防护、XSS、CSRF | 涉及用户输入、API 端点、认证 |

> 每个分类的完整原则和 DO/DON'T 见 → `references/` 下对应文件
>
> 设计模式按尺度分文件：`design-patterns.md`（总表索引）→ `patterns-small-scale.md` / `patterns-classic.md` / `patterns-module.md` / `patterns-frontend.md` / `patterns-backend.md` / `patterns-crosscut.md` / `patterns-architecture.md` / `anti-patterns.md`（按需加载）

## 上下文扫描

匹配原则前，先扫描项目上下文确定以下信息：

### 自动检测项

| 检测项 | 检测方式 | 影响选择 |
|-------|---------|---------|
| 语言/框架 | package.json, pom.xml, pyproject.toml, tsconfig | SOLID/DDD/设计模式的适用方式 |
| 测试框架 | jest.config, vitest.config, pytest.ini, build.gradle | TDD/BDD 是否适用 |
| 项目规模 | 文件数量、模块数量 | DDD 分层是否值得引入 |
| 目录结构 | 是否已有分层（controller/service/repository） | 分层实践是否延续 |
| 已有测试 | __tests__/, *.test.*, *.spec.* | 测试覆盖现状 |
| E2E 工具 | cypress/, playwright.config | BDD 是否适用 |
| ORM/数据库 | prisma/, typeorm, mybatis, sequelize | 性能意识、数据建模原则 |

### 上下文分级

| 项目类型 | 特征 | 默认适用原则 |
|---------|------|------------|
| **新项目** | 无 src/, 无 package.json 或空项目 | Clean Code + SOLID + 可测试性（推荐 TDD） |
| **小项目** | < 50 文件, 单模块 | Clean Code + SOLID + 错误处理 |
| **中型项目** | 50-500 文件, 2-5 模块, 有测试 | 全部可选（按检测结果） |
| **大型项目** | > 500 文件, 多模块 | DDD + SOLID + 性能 + 安全（按检测结果） |
| **遗留项目** | 无测试框架, 无明确分层 | Clean Code + 错误处理 + 渐进式改善 |

## 输出格式

### 原则清单

```markdown
# 工程原则匹配报告

## 项目上下文
- 语言/框架: TypeScript + NestJS
- 测试框架: vitest（已配置）
- 项目规模: 中型（~200 文件）
- 目录结构: DDD 分层（controller/service/repository）

## 适用原则

### ✅ 始终适用
- **Clean Code**: 函数 ≤ 30 行, 有意义的变量名, 避免 magic number
- **错误处理**: 业务异常 vs 系统异常分级, 不吞异常

### ✅ 经检测适用
- **SOLID (OOP)**: 检测到 class 使用 → SRP, OCP, DIP 适用
- **TDD**: 检测到 vitest → 新功能应先写测试
- **DDD 分层**: 检测到已有 controller/service/repository 结构 → 延续
- **可测试性**: 依赖注入已使用（NestJS @Injectable） → 继续遵循
- **性能**: 涉及数据库 → 注意 N+1, 添加必要索引

### ⏭️ 不适用（跳过理由）
- **BDD**: 未检测到 E2E 框架（无 cypress/playwright）
- **设计模式-工厂/策略**: 当前任务不涉及多态/策略选择场景
```

### 单原则约束（嵌入编码）

当模型执行编码任务时，适用的原则以简短约束形式嵌入：

```
[原则约束]
- SRP: 每个类/函数只做一件事
- OCP: 通过接口扩展，不修改已有类
- TDD: 先写失败测试 → 通过 → 重构
- 错误处理: 用自定义异常类，不用字符串
```

## Python 脚本

```bash
python scripts/principles_matcher.py match --root <project_root> [--task <任务描述>] [--format json|markdown]
```

- `--root`：项目路径，用于扫描上下文
- `--task`：任务描述（可选），辅助匹配更精确的原则
- 无 `--root` 时仅基于任务描述做通用匹配

> 脚本实现见 → `scripts/principles_matcher.py`
