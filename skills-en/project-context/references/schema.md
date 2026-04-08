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
