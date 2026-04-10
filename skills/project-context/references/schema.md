# context.db Schema 定义

所有表使用 SQLite，数据库文件位于 `{project_root}/.cache/context.db`。

## project_meta — 项目元信息

```sql
CREATE TABLE IF NOT EXISTS project_meta (
    key   TEXT PRIMARY KEY,   -- 元信息键名
    value TEXT NOT NULL,       -- 元信息值（JSON 或纯文本）
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 常用键：
-- project_name      项目名称
-- root_path         项目根绝对路径
-- monorepo          是否 monorepo（"true"/"false"）
-- monorepo_apps     apps/ 下的应用列表（JSON 数组）
-- monorepo_packages packages/ 下的包列表（JSON 数组）
-- node_version      Node.js 版本
-- pnpm_version      pnpm 版本
-- framework         主框架（Vue/React/NestJS/Spring Boot 等）
-- last_init_at      上次 init 时间
-- last_sync_at      上次 sync 时间
```

## file_tree — 文件树快照

```sql
CREATE TABLE IF NOT EXISTS file_tree (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    path       TEXT NOT NULL UNIQUE,   -- 相对于项目根的路径
    file_type  TEXT NOT NULL,          -- file / directory
    extension  TEXT,                    -- 文件扩展名（.ts, .vue, .java 等）
    size_bytes INTEGER,                -- 文件大小
    mtime      TEXT,                   -- 修改时间（ISO 8601）
    hash       TEXT,                   -- 文件内容 SHA-256（前 8 位即可）
    status     TEXT NOT NULL DEFAULT 'active',  -- active / stale / deleted
    category   TEXT,                   -- source / config / doc / test / asset / other
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_file_tree_path ON file_tree(path);
CREATE INDEX IF NOT EXISTS idx_file_tree_status ON file_tree(status);
CREATE INDEX IF NOT EXISTS idx_file_tree_category ON file_tree(category);
```

### category 分类规则

| category | 匹配规则 |
|----------|---------|
| source | `*.ts, *.tsx, *.vue, *.js, *.jsx, *.java, *.py` 等源码文件 |
| config | `*.json, *.yaml, *.yml, *.toml, *.env*` 且在根目录或 config/ 下 |
| doc | `*.md` 且在 docs/ 或 specs/ 下 |
| test | 路径含 `__tests__/`, `*.test.*`, `*.spec.*` |
| asset | `*.png, *.jpg, *.svg, *.ico, *.woff*` 等静态资源 |
| other | 未匹配以上规则的文件 |

## code_summary — 代码结构摘要

```sql
CREATE TABLE IF NOT EXISTS code_summary (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path  TEXT NOT NULL,           -- 对应 file_tree.path
    symbol     TEXT NOT NULL,           -- 导出的符号名（函数名/类名/接口名/组件名）
    kind       TEXT NOT NULL,           -- function / class / interface / type / component / enum / const
    signature  TEXT,                    -- 签名摘要（如 `async login(phone: string, code: string): Promise<User>`）
    is_export  INTEGER NOT NULL DEFAULT 1,  -- 是否导出（1=导出, 0=内部）
    line_start INTEGER,                -- 起始行号
    line_end   INTEGER,                -- 结束行号
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (file_path) REFERENCES file_tree(path) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_code_summary_file ON code_summary(file_path);
CREATE INDEX IF NOT EXISTS idx_code_summary_symbol ON code_summary(symbol);
CREATE INDEX IF NOT EXISTS idx_code_summary_kind ON code_summary(kind);
```

## dependencies — 文件间依赖关系

记录文件间的 import/require 静态依赖，由 `scripts/dep_extractor.py` 在 sync 时自动解析填充。

```sql
CREATE TABLE IF NOT EXISTS dependencies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL,          -- 发起 import 的文件（项目相对路径）
    target_path TEXT NOT NULL,          -- 被 import 的文件（项目相对路径）
    import_type TEXT NOT NULL,          -- import / require / dynamic_import / re_export
    symbols     TEXT,                   -- 导入的具体符号（JSON 数组，如 ["UserService", "AuthGuard"]）
    is_type_only INTEGER DEFAULT 0,    -- TypeScript 仅类型导入（1=type-only, 0=value）
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (source_path) REFERENCES file_tree(path) ON DELETE CASCADE,
    FOREIGN KEY (target_path) REFERENCES file_tree(path) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dep_source ON dependencies(source_path);
CREATE INDEX IF NOT EXISTS idx_dep_target ON dependencies(target_path);
CREATE UNIQUE INDEX IF NOT EXISTS idx_dep_pair ON dependencies(source_path, target_path);
```

### import_type 取值规则

| import_type | 匹配模式 |
|-------------|---------|
| `import` | ES `import { X } from '...'` / Python `from ... import X` / Java `import ...` |
| `require` | CJS `require('...')` |
| `dynamic_import` | `import('...')` / `__import__('...')` |
| `re_export` | `export { X } from '...'` / `export * from '...'` |

## knowledge_edges — 语义级关系图

记录 agent 在任务执行过程中发现的符号级语义关系。**由 AI agent 在 Deliver 阶段提取**，非脚本生成。

```sql
CREATE TABLE IF NOT EXISTS knowledge_edges (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file   TEXT NOT NULL,        -- 源文件路径
    source_symbol TEXT,                 -- 源符号（函数名/类名，NULL 表示文件级）
    target_file   TEXT NOT NULL,        -- 目标文件路径
    target_symbol TEXT,                 -- 目标符号
    relation      TEXT NOT NULL,        -- 关系类型（见下表）
    context       TEXT,                 -- 一句话描述关系语境
                                       -- 如 "注册前先校验手机号唯一性"
    confidence    TEXT DEFAULT 'validated',  -- validated / inferred
    session_hash  TEXT,                 -- 产生此知识的会话标识
    updated_at    TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (source_file) REFERENCES file_tree(path) ON DELETE CASCADE,
    FOREIGN KEY (target_file) REFERENCES file_tree(path) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ke_source ON knowledge_edges(source_file);
CREATE INDEX IF NOT EXISTS idx_ke_target ON knowledge_edges(target_file);
CREATE INDEX IF NOT EXISTS idx_ke_relation ON knowledge_edges(relation);
CREATE UNIQUE INDEX IF NOT EXISTS idx_ke_unique ON knowledge_edges(
    source_file, COALESCE(source_symbol, ''), target_file, COALESCE(target_symbol, ''), relation
);
```

### relation 取值规则

| relation | 含义 | 示例 |
|----------|------|------|
| `calls` | 函数/方法调用 | `UserService.register()` calls `AuthService.validate()` |
| `extends` | 继承 | `AdminUser` extends `BaseUser` |
| `implements` | 接口实现 | `UserServiceImpl` implements `IUserService` |
| `triggers` | 事件触发 | `OrderService.create()` triggers `InventoryEvent` |
| `reads` | 数据读取 | `ReportService` reads `analytics_table` |
| `writes` | 数据写入 | `UserService.register()` writes `user_table` |
| `validates` | 校验依赖 | `CreateUserDTO` validates via `PhoneValidator` |
| `delegates` | 委托/代理 | `Controller` delegates to `Service` |

### confidence 含义

| 值 | 含义 |
|----|------|
| `validated` | 任务完成且用户**未质疑**结果——隐式确认关系有效 |
| `inferred` | agent 推理得出但未经实际执行验证 |

## knowledge_flows — 业务流链路

记录 agent 发现的跨模块业务流程链路。**由 AI agent 在 Deliver 阶段提取**。

```sql
CREATE TABLE IF NOT EXISTS knowledge_flows (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_name    TEXT NOT NULL,         -- 流程名（如 "用户注册流程"）
    steps        TEXT NOT NULL,         -- JSON 数组：[{"file":"...","symbol":"...","action":"..."}]
    description  TEXT,                  -- 自然语言描述
    confidence   TEXT DEFAULT 'validated',
    session_hash TEXT,
    updated_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_kf_name ON knowledge_flows(flow_name);
```

### steps JSON 格式

```json
[
  {"file": "src/auth/auth.controller.ts", "symbol": "login", "action": "接收登录请求"},
  {"file": "src/auth/auth.service.ts", "symbol": "validateCredentials", "action": "校验凭证"},
  {"file": "src/auth/token.service.ts", "symbol": "generateTokenPair", "action": "生成双 Token"},
  {"file": "src/cache/redis.service.ts", "symbol": "setRefreshToken", "action": "存储刷新令牌"}
]
```

## phase_log — 阶段链守卫日志

记录 Plan→Execute→Validate→Deliver 四阶段的 enter/gate 事件，提供机械化检查点。由 `scripts/phase_guard.py` 管理。

```sql
CREATE TABLE IF NOT EXISTS phase_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    slice_id     TEXT NOT NULL,         -- Slice 标识（如 "S1", "S2"）
    phase        TEXT NOT NULL,         -- plan / execute / validate / deliver
    event        TEXT NOT NULL,         -- enter / gate-pass / gate-fail
    outputs      TEXT,                  -- JSON 数组：[{"path":"...","exists":true,"hash":"..."}]
    gate_detail  TEXT,                  -- JSON：Gate 检查详情（如各检查项通过/失败）
    session_hash TEXT,                  -- 产生此记录的会话标识
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_pl_slice ON phase_log(slice_id);
CREATE INDEX IF NOT EXISTS idx_pl_lookup ON phase_log(slice_id, phase, event);
```

### event 取值规则

| event | 含义 | 写入时机 |
|-------|------|---------|
| `enter` | 进入该阶段 | phase_guard.py enter —— 验证前置 phase 的 gate-pass 后写入 |
| `gate-pass` | 阶段卡点通过 | phase_guard.py gate --result pass —— 验证产出文件存在后写入 |
| `gate-fail` | 阶段卡点未通过 | phase_guard.py gate --result fail —— 触发回流 |

### 阶段依赖链

```
plan.enter → plan.gate-pass → execute.enter → execute.gate-pass → validate.enter → validate.gate-pass → deliver.enter → deliver.gate-pass
```

- `execute.enter` 要求 `plan.gate-pass` 已存在
- `validate.enter` 要求 `execute.gate-pass` 已存在
- `deliver.enter` 要求 `validate.gate-pass` 已存在
- `plan.enter` 无前置条件（首阶段）

## FTS5 全文检索（可选启用）

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS fts_code_summary USING fts5(
    file_path, symbol, signature, kind,
    content=code_summary,
    content_rowid=id
);
```

## 向量化扩展（未来升级，当前不启用）

```sql
-- 需要安装 sqlite-vss 扩展
-- CREATE VIRTUAL TABLE IF NOT EXISTS vss_code_summary USING vss0(
--     embedding(384)   -- MiniLM 维度
-- );
```
