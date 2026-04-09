# context.db Schema Definition

All tables use SQLite. The database file is located at `{project_root}/.cache/context.db`.

## project_meta — Project Metadata

```sql
CREATE TABLE IF NOT EXISTS project_meta (
    key   TEXT PRIMARY KEY,   -- Metadata key name
    value TEXT NOT NULL,       -- Metadata value (JSON or plain text)
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Common keys:
-- project_name      Project name
-- root_path         Project root absolute path
-- monorepo          Whether monorepo ("true"/"false")
-- monorepo_apps     Application list under apps/ (JSON array)
-- monorepo_packages Package list under packages/ (JSON array)
-- node_version      Node.js version
-- pnpm_version      pnpm version
-- framework         Main framework (Vue/React/NestJS/Spring Boot, etc.)
-- last_init_at      Last init time
-- last_sync_at      Last sync time
```

## file_tree — File Tree Snapshot

```sql
CREATE TABLE IF NOT EXISTS file_tree (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    path       TEXT NOT NULL UNIQUE,   -- Path relative to project root
    file_type  TEXT NOT NULL,          -- file / directory
    extension  TEXT,                    -- File extension (.ts, .vue, .java, etc.)
    size_bytes INTEGER,                -- File size
    mtime      TEXT,                   -- Modification time (ISO 8601)
    hash       TEXT,                   -- File content SHA-256 (first 8 chars suffice)
    status     TEXT NOT NULL DEFAULT 'active',  -- active / stale / deleted
    category   TEXT,                   -- source / config / doc / test / asset / other
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_file_tree_path ON file_tree(path);
CREATE INDEX IF NOT EXISTS idx_file_tree_status ON file_tree(status);
CREATE INDEX IF NOT EXISTS idx_file_tree_category ON file_tree(category);
```

### Category Classification Rules

| category | Matching Rules |
|----------|---------------|
| source | `*.ts, *.tsx, *.vue, *.js, *.jsx, *.java, *.py` and other source files |
| config | `*.json, *.yaml, *.yml, *.toml, *.env*` in root directory or config/ |
| doc | `*.md` under docs/ or specs/ |
| test | Path contains `__tests__/`, `*.test.*`, `*.spec.*` |
| asset | `*.png, *.jpg, *.svg, *.ico, *.woff*` and other static assets |
| other | Files not matching any of the above rules |

## code_summary — Code Structure Summary

```sql
CREATE TABLE IF NOT EXISTS code_summary (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path  TEXT NOT NULL,           -- Corresponds to file_tree.path
    symbol     TEXT NOT NULL,           -- Exported symbol name (function/class/interface/component name)
    kind       TEXT NOT NULL,           -- function / class / interface / type / component / enum / const
    signature  TEXT,                    -- Signature summary (e.g., `async login(phone: string, code: string): Promise<User>`)
    is_export  INTEGER NOT NULL DEFAULT 1,  -- Whether exported (1=exported, 0=internal)
    line_start INTEGER,                -- Start line number
    line_end   INTEGER,                -- End line number
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (file_path) REFERENCES file_tree(path) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_code_summary_file ON code_summary(file_path);
CREATE INDEX IF NOT EXISTS idx_code_summary_symbol ON code_summary(symbol);
CREATE INDEX IF NOT EXISTS idx_code_summary_kind ON code_summary(kind);
```

## dependencies — Inter-File Dependencies

Records import/require static dependencies between files. Automatically populated by `scripts/dep_extractor.py` during sync.

```sql
CREATE TABLE IF NOT EXISTS dependencies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL,          -- File that imports (project-relative path)
    target_path TEXT NOT NULL,          -- File being imported (project-relative path)
    import_type TEXT NOT NULL,          -- import / require / dynamic_import / re_export
    symbols     TEXT,                   -- Imported symbols (JSON array, e.g. ["UserService", "AuthGuard"])
    is_type_only INTEGER DEFAULT 0,    -- TypeScript type-only import (1=type-only, 0=value)
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (source_path) REFERENCES file_tree(path) ON DELETE CASCADE,
    FOREIGN KEY (target_path) REFERENCES file_tree(path) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dep_source ON dependencies(source_path);
CREATE INDEX IF NOT EXISTS idx_dep_target ON dependencies(target_path);
CREATE UNIQUE INDEX IF NOT EXISTS idx_dep_pair ON dependencies(source_path, target_path);
```

### import_type Values

| import_type | Matching Pattern |
|-------------|-----------------|
| `import` | ES `import { X } from '...'` / Python `from ... import X` / Java `import ...` |
| `require` | CJS `require('...')` |
| `dynamic_import` | `import('...')` / `__import__('...')` |
| `re_export` | `export { X } from '...'` / `export * from '...'` |

## knowledge_edges — Semantic Relationship Graph

Records symbol-level semantic relationships discovered by the agent during task execution. **Extracted by the AI agent during the Deliver phase**, not script-generated.

```sql
CREATE TABLE IF NOT EXISTS knowledge_edges (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file   TEXT NOT NULL,        -- Source file path
    source_symbol TEXT,                 -- Source symbol (function/class name, NULL = file-level)
    target_file   TEXT NOT NULL,        -- Target file path
    target_symbol TEXT,                 -- Target symbol
    relation      TEXT NOT NULL,        -- Relationship type (see table below)
    context       TEXT,                 -- One-sentence relationship context
                                       -- e.g. "Validates phone uniqueness before registration"
    confidence    TEXT DEFAULT 'validated',  -- validated / inferred
    session_hash  TEXT,                 -- Session identifier that produced this knowledge
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

### relation Values

| relation | Meaning | Example |
|----------|---------|---------|
| `calls` | Function/method invocation | `UserService.register()` calls `AuthService.validate()` |
| `extends` | Inheritance | `AdminUser` extends `BaseUser` |
| `implements` | Interface implementation | `UserServiceImpl` implements `IUserService` |
| `triggers` | Event triggering | `OrderService.create()` triggers `InventoryEvent` |
| `reads` | Data read | `ReportService` reads `analytics_table` |
| `writes` | Data write | `UserService.register()` writes `user_table` |
| `validates` | Validation dependency | `CreateUserDTO` validates via `PhoneValidator` |
| `delegates` | Delegation/proxy | `Controller` delegates to `Service` |

### confidence Meaning

| Value | Meaning |
|-------|---------|
| `validated` | Task completed and user **did not challenge** the result — implicit confirmation that the relationship is valid |
| `inferred` | Agent inferred the relationship but it was not verified through actual execution |

## knowledge_flows — Business Flow Chains

Records cross-module business process chains discovered by the agent. **Extracted by the AI agent during the Deliver phase**.

```sql
CREATE TABLE IF NOT EXISTS knowledge_flows (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_name    TEXT NOT NULL,         -- Flow name (e.g. "User Registration Flow")
    steps        TEXT NOT NULL,         -- JSON array: [{"file":"...","symbol":"...","action":"..."}]
    description  TEXT,                  -- Natural language description
    confidence   TEXT DEFAULT 'validated',
    session_hash TEXT,
    updated_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_kf_name ON knowledge_flows(flow_name);
```

### steps JSON Format

```json
[
  {"file": "src/auth/auth.controller.ts", "symbol": "login", "action": "Receives login request"},
  {"file": "src/auth/auth.service.ts", "symbol": "validateCredentials", "action": "Validates credentials"},
  {"file": "src/auth/token.service.ts", "symbol": "generateTokenPair", "action": "Generates dual tokens"},
  {"file": "src/cache/redis.service.ts", "symbol": "setRefreshToken", "action": "Stores refresh token"}
]
```

## FTS5 Full-Text Search (Optional)

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS fts_code_summary USING fts5(
    file_path, symbol, signature, kind,
    content=code_summary,
    content_rowid=id
);
```

## Vector Extension (Future Upgrade, Not Enabled Currently)

```sql
-- Requires sqlite-vss extension
-- CREATE VIRTUAL TABLE IF NOT EXISTS vss_code_summary USING vss0(
--     embedding(384)   -- MiniLM dimensions
-- );
```
