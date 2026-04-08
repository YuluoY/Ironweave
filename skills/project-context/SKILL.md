---
name: project-context
description: >-
  项目结构感知与持久化——在项目根目录 .cache/context.db（SQLite）中维护项目文件树快照与代码结构摘要，解决模型跨会话遗忘项目结构的问题。被动调用，不会主动触发。只读取项目源码（一级数据），不修改任何文件。
  务必在以下场景使用本 skill：需要了解项目全局结构、查询某模块的文件列表和导出符号、跨会话恢复项目结构理解、项目感知、context sync、项目记忆、project memory、代码摘要索引、查看项目结构。本 skill 不修改源码，不管理文档产出。
---

# 项目结构感知

本 Skill 解决一个核心问题：**AI 模型在跨会话时丢失对项目结构的理解**。每次新会话都要重新扫描目录、重新理解代码组织，效率低且容易遗漏。

本 Skill 通过在项目中维护一个 **SQLite 数据库**（`.ai/context.db`），将项目文件树和代码结构摘要持久化，使得跨会话快速恢复项目认知。

## 数据模型

```mermaid
graph TD
    SRC["项目源码<br/>唯一真实源 · 只读参考<br/>代码文件 = ground truth"]
    DB[".cache/context.db<br/>运行时 SQLite<br/>文件树快照 · 代码结构摘要"]

    SRC -->|"扫描/增量同步"| DB
    SRC -->|"冲突时以源码为准"| DB

    style SRC fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style DB fill:#fff3e0,stroke:#f57c00,stroke-width:2px
```

**源码是唯一真实源**。db 是源码结构的缓存，用户可能在不使用本 skill 的情况下修改代码，因此 db 信息可能过期。

## 原则

- **被动调用**：本 skill 不会自动触发，仅在外部需要时被调用。
- **源码优先**：db 是缓存，不是真实源。每次查询前应对涉及范围做增量校验。
- **增量同步**：不全量扫描，基于文件修改时间（mtime）+ 文件哈希做增量检测，仅同步变更部分。
- **最小存储**：只存结构信息和导出符号签名，不存储源码内容本身。

## 数据库位置与 Git 策略

- 路径：`{project_root}/.cache/context.db`
- `.cache/` 目录应加入 `.gitignore`（db 是本地运行时产物）

## 核心能力（被动 API）

### 1. init — 初始化

首次在项目中使用时调用。扫描项目文件结构，生成初始快照。

- 扫描：目录树、文件类型、文件大小、修改时间
- 识别：package.json、tsconfig、入口文件等关键配置
- 忽略：node_modules、dist、.git、二进制文件等（遵循 .gitignore）
- 写入：`file_tree` 表 + `project_meta` 表

### 2. sync — 增量同步

对比当前文件系统与 db 中的快照，检测新增/修改/删除的文件，更新 db。

- 基于 mtime + 文件哈希检测变更
- 对变更的代码文件，可提取结构摘要（导出的函数/类/接口签名）

### 3. query — 查询结构

根据路径或关键词查询项目结构信息：

- 项目结构概览（project_meta）
- 某个模块/目录的文件列表与分类
- 某个文件的导出符号摘要

### 4. validate — 校验一致性

对比 db 中的信息与实际源码，标记过期条目：

- 文件已被删除 → 标记为 deleted
- 文件内容已变但摘要未更新 → 标记为 stale

## 数据库 Schema 概要

| 表名 | 用途 |
|------|------|
| `project_meta` | 项目元信息（名称、根路径、monorepo 结构、Node 版本等） |
| `file_tree` | 文件树快照（路径、类型、大小、mtime、hash、状态、分类） |
| `code_summary` | 代码结构摘要（文件→导出的函数/类/接口签名） |

> 完整 Schema（含字段定义与索引）见 → `references/schema.md`

## 向量化扩展（可选升级）

对于大型项目（文件 > 500），可启用向量化扩展实现语义检索。当前版本以关键词全文检索为主（SQLite FTS5），向量化作为未来升级路径。

## Python 脚本

```bash
python scripts/context_db.py init     --root <project_root>
python scripts/context_db.py sync     --root <project_root>
python scripts/context_db.py query    --root <project_root> --scope structure|meta [--module <path>] [--keyword <term>]
python scripts/context_db.py validate --root <project_root>
```

> 脚本实现见 → `scripts/context_db.py`

## 常见问题

- **db 与源码不一致**：调 `validate`标记过期条目，再调 `sync` 更新。源码永远是 truth。
- **db 文件损坏/丢失**：重新 `init` 即可，db 是可重建的缓存。
- **项目太大初始化太慢**：`init` 先只扫描文件树（秒级），代码摘要可延迟到首次查询时按需生成。
