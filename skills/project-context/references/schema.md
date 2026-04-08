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
