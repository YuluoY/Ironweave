#!/usr/bin/env python3
"""
project-context: 项目结构感知持久化脚本

用法:
    python context_db.py init        --root <project_root>
    python context_db.py sync        --root <project_root>
    python context_db.py deps        --root <project_root>
    python context_db.py stale-check --root <project_root> [--sample <n>]
    python context_db.py knowledge   --root <project_root> --type edges|flows --data <JSON> [--session <hash>]
    python context_db.py query       --root <project_root> --scope structure|meta [--module <path>] [--keyword <term>] [--limit <n>]
    python context_db.py validate    --root <project_root>
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_REL_PATH = ".cache/context.db"

# ── 忽略规则 ──────────────────────────────────────────────

DEFAULT_IGNORE_DIRS = {
    "node_modules", "dist", "build", ".git", "__pycache__",
    ".next", ".nuxt", ".output", "coverage", ".turbo", ".cache",
    "target", ".gradle", ".idea", ".vscode",
}

DEFAULT_IGNORE_EXTENSIONS = {
    ".lock", ".log", ".map", ".min.js", ".min.css",
    ".woff", ".woff2", ".ttf", ".eot",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".mp4", ".mp3", ".wav",
    ".zip", ".tar", ".gz", ".jar", ".war",
    ".pyc", ".pyo", ".class",
    ".db", ".sqlite", ".sqlite3",
}

# ── 文件分类 ──────────────────────────────────────────────

SOURCE_EXT = {".ts", ".tsx", ".js", ".jsx", ".vue", ".java", ".py", ".go", ".rs", ".rb", ".swift", ".kt"}
CONFIG_EXT = {".json", ".yaml", ".yml", ".toml", ".ini", ".env"}
DOC_EXT = {".md", ".mdx", ".txt", ".rst"}
TEST_PATTERNS = {"__tests__", ".test.", ".spec.", "_test.", "_spec."}
ASSET_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".woff", ".woff2", ".ttf", ".eot"}


def classify_file(rel_path: str, ext: str) -> str:
    parts = rel_path.split("/")
    if any(p in rel_path for p in TEST_PATTERNS):
        return "test"
    if ext in SOURCE_EXT:
        return "source"
    if ext in DOC_EXT and any(d in parts for d in ("docs", "specs", "doc")):
        return "doc"
    if ext in CONFIG_EXT:
        return "config"
    if ext in ASSET_EXT:
        return "asset"
    return "other"


def file_hash(filepath: str) -> str:
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except (OSError, PermissionError):
        return ""


def should_ignore(path: Path, root: Path) -> bool:
    for part in path.relative_to(root).parts:
        if part in DEFAULT_IGNORE_DIRS:
            return True
    if path.is_file() and path.suffix.lower() in DEFAULT_IGNORE_EXTENSIONS:
        return True
    return False


# ── DB 初始化 ─────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS project_meta (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS file_tree (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    path       TEXT NOT NULL UNIQUE,
    file_type  TEXT NOT NULL,
    extension  TEXT,
    size_bytes INTEGER,
    mtime      TEXT,
    hash       TEXT,
    status     TEXT NOT NULL DEFAULT 'active',
    category   TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_ft_path ON file_tree(path);
CREATE INDEX IF NOT EXISTS idx_ft_status ON file_tree(status);

CREATE TABLE IF NOT EXISTS code_summary (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path  TEXT NOT NULL,
    symbol     TEXT NOT NULL,
    kind       TEXT NOT NULL,
    signature  TEXT,
    is_export  INTEGER NOT NULL DEFAULT 1,
    line_start INTEGER,
    line_end   INTEGER,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (file_path) REFERENCES file_tree(path) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_cs_file ON code_summary(file_path);
CREATE INDEX IF NOT EXISTS idx_cs_symbol ON code_summary(symbol);

CREATE TABLE IF NOT EXISTS dependencies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL,
    target_path TEXT NOT NULL,
    import_type TEXT NOT NULL,
    symbols     TEXT,
    is_type_only INTEGER DEFAULT 0,
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (source_path) REFERENCES file_tree(path) ON DELETE CASCADE,
    FOREIGN KEY (target_path) REFERENCES file_tree(path) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_dep_source ON dependencies(source_path);
CREATE INDEX IF NOT EXISTS idx_dep_target ON dependencies(target_path);
CREATE UNIQUE INDEX IF NOT EXISTS idx_dep_pair ON dependencies(source_path, target_path);

CREATE TABLE IF NOT EXISTS knowledge_edges (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file   TEXT NOT NULL,
    source_symbol TEXT,
    target_file   TEXT NOT NULL,
    target_symbol TEXT,
    relation      TEXT NOT NULL,
    context       TEXT,
    confidence    TEXT DEFAULT 'validated',
    session_hash  TEXT,
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

CREATE TABLE IF NOT EXISTS knowledge_flows (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_name    TEXT NOT NULL,
    steps        TEXT NOT NULL,
    description  TEXT,
    confidence   TEXT DEFAULT 'validated',
    session_hash TEXT,
    updated_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_kf_name ON knowledge_flows(flow_name);

CREATE TABLE IF NOT EXISTS phase_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    slice_id     TEXT NOT NULL,
    phase        TEXT NOT NULL,
    event        TEXT NOT NULL,
    outputs      TEXT,
    gate_detail  TEXT,
    session_hash TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_pl_slice ON phase_log(slice_id);
CREATE INDEX IF NOT EXISTS idx_pl_lookup ON phase_log(slice_id, phase, event);

"""


def get_db(root: str) -> sqlite3.Connection:
    db_path = os.path.join(root, DB_REL_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_SQL)
    return conn


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ── 命令实现 ──────────────────────────────────────────────

def cmd_init(root: str):
    root_path = Path(root).resolve()
    conn = get_db(str(root_path))

    # 确保 .gitignore 包含 .ai/
    gitignore = root_path / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".ai/" not in content:
            with open(gitignore, "a") as f:
                f.write("\n# AI context database\n.ai/\n")

    # 扫描文件树
    count = 0
    for item in root_path.rglob("*"):
        if should_ignore(item, root_path):
            continue
        rel = str(item.relative_to(root_path))
        ft = "directory" if item.is_dir() else "file"
        ext = item.suffix.lower() if item.is_file() else None
        size = item.stat().st_size if item.is_file() else None
        mtime = datetime.fromtimestamp(item.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds")
        h = file_hash(str(item)) if item.is_file() else None
        cat = classify_file(rel, ext or "") if item.is_file() else None

        conn.execute(
            """INSERT INTO file_tree (path, file_type, extension, size_bytes, mtime, hash, category, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(path) DO UPDATE SET
                 file_type=excluded.file_type, extension=excluded.extension,
                 size_bytes=excluded.size_bytes, mtime=excluded.mtime,
                 hash=excluded.hash, category=excluded.category,
                 status='active', updated_at=excluded.updated_at""",
            (rel, ft, ext, size, mtime, h, cat, now_iso()),
        )
        count += 1

    # 写入元信息
    meta = {
        "project_name": root_path.name,
        "root_path": str(root_path),
        "last_init_at": now_iso(),
    }
    # 检测 monorepo
    if (root_path / "pnpm-workspace.yaml").exists():
        meta["monorepo"] = "true"
        apps = [d.name for d in (root_path / "apps").iterdir() if d.is_dir()] if (root_path / "apps").exists() else []
        pkgs = [d.name for d in (root_path / "packages").iterdir() if d.is_dir()] if (root_path / "packages").exists() else []
        meta["monorepo_apps"] = json.dumps(apps)
        meta["monorepo_packages"] = json.dumps(pkgs)

    # 检测 Node/pnpm 版本
    pkg_json = root_path / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text())
            if "engines" in pkg and "node" in pkg["engines"]:
                meta["node_version"] = pkg["engines"]["node"]
            if "packageManager" in pkg:
                meta["pnpm_version"] = pkg["packageManager"]
        except (json.JSONDecodeError, KeyError):
            pass

    for k, v in meta.items():
        conn.execute(
            "INSERT INTO project_meta (key, value, updated_at) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
            (k, v, now_iso()),
        )

    conn.commit()
    conn.close()
    print(json.dumps({"status": "ok", "files_scanned": count, "db_path": str(root_path / DB_REL_PATH)}))


def cmd_sync(root: str):
    root_path = Path(root).resolve()
    conn = get_db(str(root_path))

    # 获取 db 中所有 active 文件
    db_files = {}
    for row in conn.execute("SELECT path, mtime, hash FROM file_tree WHERE status='active' AND file_type='file'"):
        db_files[row["path"]] = (row["mtime"], row["hash"])

    added, modified, deleted = 0, 0, 0
    seen = set()

    for item in root_path.rglob("*"):
        if should_ignore(item, root_path) or item.is_dir():
            continue
        rel = str(item.relative_to(root_path))
        seen.add(rel)
        ext = item.suffix.lower()
        mtime = datetime.fromtimestamp(item.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds")

        if rel not in db_files:
            # 新文件
            h = file_hash(str(item))
            cat = classify_file(rel, ext)
            conn.execute(
                """INSERT INTO file_tree (path, file_type, extension, size_bytes, mtime, hash, category, updated_at)
                   VALUES (?, 'file', ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(path) DO UPDATE SET
                     status='active', mtime=excluded.mtime, hash=excluded.hash,
                     size_bytes=excluded.size_bytes, category=excluded.category, updated_at=excluded.updated_at""",
                (rel, ext, item.stat().st_size, mtime, h, cat, now_iso()),
            )
            added += 1
        elif db_files[rel][0] != mtime:
            # mtime 变了，检查 hash
            h = file_hash(str(item))
            if h != db_files[rel][1]:
                cat = classify_file(rel, ext)
                conn.execute(
                    "UPDATE file_tree SET mtime=?, hash=?, size_bytes=?, category=?, status='active', updated_at=? WHERE path=?",
                    (mtime, h, item.stat().st_size, cat, now_iso(), rel),
                )
                modified += 1

    # 标记已删除
    for path in db_files:
        if path not in seen:
            conn.execute("UPDATE file_tree SET status='deleted', updated_at=? WHERE path=?", (now_iso(), path))
            deleted += 1

    conn.execute(
        "INSERT INTO project_meta (key, value, updated_at) VALUES ('last_sync_at', ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
        (now_iso(), now_iso()),
    )

    conn.commit()
    conn.close()
    print(json.dumps({"status": "ok", "added": added, "modified": modified, "deleted": deleted}))


def cmd_query(root: str, scope: str, module: str | None = None, keyword: str | None = None, limit: int = 50):
    root_path = Path(root).resolve()
    conn = get_db(str(root_path))
    results = []

    if scope == "structure":
        sql = "SELECT path, file_type, extension, category, size_bytes FROM file_tree WHERE status='active'"
        params: list = []
        if module:
            sql += " AND path LIKE ?"
            params.append(f"{module}%")
        sql += " ORDER BY path LIMIT ?"
        params.append(limit)
        results = [dict(r) for r in conn.execute(sql, params)]

    elif scope == "meta":
        results = [dict(r) for r in conn.execute("SELECT key, value FROM project_meta ORDER BY key")]

    conn.close()
    print(json.dumps({"status": "ok", "scope": scope, "count": len(results), "results": results}, ensure_ascii=False))


def cmd_validate(root: str):
    root_path = Path(root).resolve()
    conn = get_db(str(root_path))

    stale, deleted, ok = 0, 0, 0
    for row in conn.execute("SELECT path, hash FROM file_tree WHERE status='active' AND file_type='file'"):
        full = root_path / row["path"]
        if not full.exists():
            conn.execute("UPDATE file_tree SET status='deleted', updated_at=? WHERE path=?", (now_iso(), row["path"]))
            deleted += 1
        else:
            current_hash = file_hash(str(full))
            if current_hash != row["hash"]:
                conn.execute("UPDATE file_tree SET status='stale', updated_at=? WHERE path=?", (now_iso(), row["path"]))
                stale += 1
            else:
                ok += 1

    conn.commit()
    conn.close()
    print(json.dumps({"status": "ok", "consistent": ok, "stale": stale, "deleted": deleted}))


def cmd_deps(root: str):
    """扫描所有源码文件，提取静态依赖写入 dependencies 表。"""
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent))
    from dep_extractor import extract_file

    root_path = Path(root).resolve()
    conn = get_db(str(root_path))

    # 获取所有 active 源码文件
    source_files = conn.execute(
        "SELECT path FROM file_tree WHERE status='active' AND file_type='file' AND category='source'"
    ).fetchall()

    inserted, skipped = 0, 0
    # 清除旧数据再全量写入（依赖关系随 sync 变化）
    conn.execute("DELETE FROM dependencies")

    for row in source_files:
        full_path = str(root_path / row["path"])
        deps = extract_file(full_path, str(root_path))
        for d in deps:
            # 只记录 target 在项目内有 file_tree 记录的依赖
            exists = conn.execute("SELECT 1 FROM file_tree WHERE path=? AND status='active'", (d["target_path"],)).fetchone()
            if not exists:
                skipped += 1
                continue
            symbols_json = json.dumps(d["symbols"]) if d["symbols"] else None
            conn.execute(
                """INSERT INTO dependencies (source_path, target_path, import_type, symbols, is_type_only, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(source_path, target_path) DO UPDATE SET
                     import_type=excluded.import_type, symbols=excluded.symbols,
                     is_type_only=excluded.is_type_only, updated_at=excluded.updated_at""",
                (row["path"], d["target_path"], d["import_type"], symbols_json, d["is_type_only"], now_iso()),
            )
            inserted += 1

    conn.commit()
    conn.close()
    print(json.dumps({"status": "ok", "dependencies_inserted": inserted, "external_skipped": skipped}))


def cmd_stale_check(root: str, sample_size: int = 20):
    """抽样检测 db 是否过期。如果 >20% 文件 stale/deleted，建议执行 sync。"""
    import random

    root_path = Path(root).resolve()
    conn = get_db(str(root_path))

    rows = conn.execute(
        "SELECT path, mtime, hash FROM file_tree WHERE status='active' AND file_type='file'"
    ).fetchall()

    if not rows:
        conn.close()
        print(json.dumps({"status": "ok", "recommendation": "empty", "total": 0}))
        return

    sample = random.sample(rows, min(sample_size, len(rows)))
    stale_count = 0

    for row in sample:
        full = root_path / row["path"]
        if not full.exists():
            stale_count += 1
        else:
            current_mtime = datetime.fromtimestamp(
                full.stat().st_mtime, tz=timezone.utc
            ).isoformat(timespec="seconds")
            if current_mtime != row["mtime"]:
                stale_count += 1

    stale_ratio = stale_count / len(sample)
    recommendation = "sync" if stale_ratio > 0.2 else "ok"

    conn.close()
    print(json.dumps({
        "status": "ok",
        "sampled": len(sample),
        "stale_in_sample": stale_count,
        "stale_ratio": round(stale_ratio, 2),
        "recommendation": recommendation,
    }))


def cmd_knowledge(root: str, knowledge_type: str, data: str, session_hash_val: str | None = None):
    """插入知识记录（edges 或 flows）。

    --type edges --data '[{"source_file":"...", "source_symbol":"...", "target_file":"...", "target_symbol":"...", "relation":"calls", "context":"..."}]'
    --type flows --data '[{"flow_name":"...", "steps":[...], "description":"..."}]'
    """
    root_path = Path(root).resolve()
    conn = get_db(str(root_path))

    try:
        records = json.loads(data)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON: {e}"}))
        return

    if not isinstance(records, list):
        records = [records]

    inserted = 0
    ts = now_iso()

    if knowledge_type == "edges":
        valid_relations = {"calls", "extends", "implements", "triggers", "reads", "writes", "validates", "delegates"}
        for r in records:
            relation = r.get("relation", "")
            if relation not in valid_relations:
                continue
            conn.execute(
                """INSERT OR REPLACE INTO knowledge_edges
                   (source_file, source_symbol, target_file, target_symbol, relation, context, confidence, session_hash, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    r.get("source_file", ""),
                    r.get("source_symbol"),
                    r.get("target_file", ""),
                    r.get("target_symbol"),
                    relation,
                    r.get("context"),
                    r.get("confidence", "validated"),
                    session_hash_val,
                    ts,
                ),
            )
            inserted += 1

    elif knowledge_type == "flows":
        for r in records:
            steps = r.get("steps", [])
            if isinstance(steps, list):
                steps = json.dumps(steps, ensure_ascii=False)
            conn.execute(
                """INSERT OR REPLACE INTO knowledge_flows
                   (flow_name, steps, description, confidence, session_hash, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    r.get("flow_name", ""),
                    steps,
                    r.get("description"),
                    r.get("confidence", "validated"),
                    session_hash_val,
                    ts,
                ),
            )
            inserted += 1
    else:
        print(json.dumps({"status": "error", "message": f"Unknown type: {knowledge_type}. Use 'edges' or 'flows'."}))
        return

    conn.commit()
    conn.close()
    print(json.dumps({"status": "ok", "type": knowledge_type, "inserted": inserted}))


# ── CLI 入口 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="project-context: 项目上下文持久化管理")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="初始化项目上下文数据库")
    p_init.add_argument("--root", required=True, help="项目根目录路径")

    p_sync = sub.add_parser("sync", help="增量同步文件变更")
    p_sync.add_argument("--root", required=True, help="项目根目录路径")

    p_query = sub.add_parser("query", help="查询项目结构信息")
    p_query.add_argument("--root", required=True)
    p_query.add_argument("--scope", required=True, choices=["structure", "meta"])
    p_query.add_argument("--module", default=None, help="限定模块/目录路径")
    p_query.add_argument("--keyword", default=None, help="关键词过滤")
    p_query.add_argument("--limit", type=int, default=50)

    p_val = sub.add_parser("validate", help="校验 db 与源码一致性")
    p_val.add_argument("--root", required=True)

    p_deps = sub.add_parser("deps", help="扫描源码提取静态依赖")
    p_deps.add_argument("--root", required=True)

    p_stale = sub.add_parser("stale-check", help="抽样检测 db 新鲜度")
    p_stale.add_argument("--root", required=True)
    p_stale.add_argument("--sample", type=int, default=20, help="抽样文件数（默认 20）")

    p_know = sub.add_parser("knowledge", help="插入知识记录（edges/flows）")
    p_know.add_argument("--root", required=True)
    p_know.add_argument("--type", required=True, dest="knowledge_type", choices=["edges", "flows"])
    p_know.add_argument("--data", required=True, help="JSON 数组：edges=[{source_file,relation,...}] / flows=[{flow_name,steps,...}]")
    p_know.add_argument("--session", default=None, dest="session_hash", help="会话标识（可选）")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args.root)
    elif args.command == "sync":
        cmd_sync(args.root)
    elif args.command == "query":
        cmd_query(args.root, args.scope, getattr(args, "module", None), getattr(args, "keyword", None), getattr(args, "limit", 50))
    elif args.command == "validate":
        cmd_validate(args.root)
    elif args.command == "deps":
        cmd_deps(args.root)
    elif args.command == "stale-check":
        cmd_stale_check(args.root, getattr(args, "sample", 20))
    elif args.command == "knowledge":
        cmd_knowledge(args.root, args.knowledge_type, args.data, getattr(args, "session_hash", None))


if __name__ == "__main__":
    main()
