#!/usr/bin/env python3
"""
docs-output: 文档产出管理脚本（模块文档 + 进度记录）

用法:
    python docs_manager.py create   --root <project_root> --module <模块名> --name <文档名> [--title <标题>]
    python docs_manager.py update   --root <project_root> --module <模块名> --name <文档名> --content <内容> [--title <标题>]
    python docs_manager.py progress --root <project_root> --topic <主题> --type <类型> --summary <摘要> [--session-id <ID>] [--files <JSON>] [--decisions <决策>] [--todos <遗留>]
    python docs_manager.py list     --root <project_root>
    python docs_manager.py validate --root <project_root>
    python docs_manager.py archive  --root <project_root> [--older-than <天数>]

同会话追加：首次调用 progress 会返回 session_id，后续用 --session-id 追加到同一文件。
"""

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

DOCS_DIR = "docs"
PROGRESS_DIR = "progress"
ARCHIVE_DIR = "archive"


def get_docs_dir(root: str) -> Path:
    return Path(root).resolve() / DOCS_DIR


def get_progress_dir(root: str) -> Path:
    return Path(root).resolve() / DOCS_DIR / PROGRESS_DIR


def extract_title(filepath: Path) -> str:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
        return ""
    except (OSError, UnicodeDecodeError):
        return ""


def get_git_user(root: str) -> dict:
    """获取 Git 用户信息。"""
    info = {"name": "unknown", "email": ""}
    try:
        name = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True, cwd=root
        ).stdout.strip()
        email = subprocess.run(
            ["git", "config", "user.email"], capture_output=True, text=True, cwd=root
        ).stdout.strip()
        if name:
            info["name"] = name
        if email:
            info["email"] = email
    except (OSError, FileNotFoundError):
        pass
    return info


def make_username(root: str) -> str:
    """从 git config user.name 生成文件名前缀：小写、空格替换为 -。"""
    git_user = get_git_user(root)
    name = git_user["name"]
    return re.sub(r"\s+", "-", name).lower()


def session_hash() -> str:
    """生成 6 位会话 hash。"""
    return secrets.token_hex(3)


def now_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def now_time() -> str:
    """当前时间，精确到秒。"""
    return datetime.now().strftime("%H:%M:%S")


def now_datetime() -> str:
    """当前日期时间，精确到秒。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def scan_modules(docs_dir: Path) -> dict[str, list[dict]]:
    """扫描模块文档（排除 progress/）。"""
    modules: dict[str, list[dict]] = {}
    if not docs_dir.exists():
        return modules

    for item in sorted(docs_dir.iterdir()):
        if item.is_dir() and item.name != PROGRESS_DIR:
            docs = []
            for md in sorted(item.rglob("*.md")):
                title = extract_title(md)
                rel = str(md.relative_to(docs_dir))
                docs.append({"name": md.stem, "file": rel, "title": title})
            if docs:
                modules[item.name] = docs

    return modules


def scan_progress(progress_dir: Path, days: int | None = None) -> list[dict]:
    """扫描进度记录。"""
    results = []
    if not progress_dir.exists():
        return results

    cutoff = None
    if days is not None:
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    for date_dir in sorted(progress_dir.iterdir(), reverse=True):
        if not date_dir.is_dir() or date_dir.name == ARCHIVE_DIR:
            continue
        if cutoff and date_dir.name < cutoff:
            continue
        for md in sorted(date_dir.iterdir()):
            if md.suffix == ".md":
                title = extract_title(md)
                # 解析 {username}_{hash}.md
                stem = md.stem
                parts = stem.rsplit("_", 1)
                username = parts[0] if len(parts) == 2 else ""
                file_hash = parts[1] if len(parts) == 2 else stem
                results.append({
                    "date": date_dir.name,
                    "username": username,
                    "session_id": file_hash,
                    "title": title,
                    "file": f"{PROGRESS_DIR}/{date_dir.name}/{md.name}",
                })

    return results


# ── 命令实现 ──────────────────────────────────────────────

def cmd_create(root: str, module: str, name: str, title: str | None = None):
    docs_dir = get_docs_dir(root)
    module_dir = docs_dir / module
    module_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{name}.md"
    filepath = module_dir / filename

    if filepath.exists():
        print(json.dumps({"status": "error", "message": f"File already exists: {module}/{filename}"}, ensure_ascii=False))
        return

    doc_title = title or name
    content = f"# {doc_title}\n\n"
    filepath.write_text(content, encoding="utf-8")

    print(json.dumps({
        "status": "ok",
        "file": f"{module}/{filename}",
        "module": module,
        "path": str(filepath),
    }, ensure_ascii=False))


def _build_header(username: str, h: str, git_user: dict) -> str:
    """构建进度文件头部（仅在新建文件时写入一次）。"""
    developer = f"{git_user['name']} <{git_user['email']}>" if git_user["email"] else git_user["name"]
    return (
        f"# 会话进度：{username}_{h}\n\n"
        f"> {developer} \u00b7 {now_datetime()} 起\n"
    )


def _build_entry(topic: str, record_type: str, summary: str,
                 files_text: str | None, decisions: str | None,
                 todos: str | None) -> str:
    """构建单个进度条目。类型合并到标题，仅包含有内容的段落。"""
    time_str = now_time()
    parts = [
        f"\n---\n\n"
        f"## [{time_str}] {topic} \u00b7 {record_type}\n\n"
        f"{summary}\n"
    ]
    if files_text:
        parts.append(f"\n{files_text}\n")
    if decisions:
        parts.append(f"\n> **决策**: {decisions}\n")
    if todos:
        parts.append(f"\n> **遗留**: {todos}\n")
    return "".join(parts)


def _parse_files(files: str | None) -> str | None:
    """解析变更文件参数。无内容返回 None。"""
    if not files:
        return None
    try:
        file_list = json.loads(files)
        return "\n".join(f"- `{f['path']}` — {f.get('reason', '')}" for f in file_list)
    except (json.JSONDecodeError, KeyError, TypeError):
        return files


def cmd_progress(root: str, topic: str, record_type: str, summary: str,
                 session_id: str | None = None,
                 files: str | None = None, decisions: str | None = None,
                 todos: str | None = None):
    progress_dir = get_progress_dir(root)
    date = now_date()
    date_dir = progress_dir / date
    date_dir.mkdir(parents=True, exist_ok=True)

    username = make_username(root)
    git_user = get_git_user(root)
    files_text = _parse_files(files)

    entry = _build_entry(
        topic=topic,
        record_type=record_type,
        summary=summary,
        files_text=files_text,
        decisions=decisions,
        todos=todos,
    )

    if session_id:
        # ── 追加到已有会话文件 ──
        filepath = date_dir / f"{username}_{session_id}.md"
        if not filepath.exists():
            print(json.dumps({
                "status": "error",
                "message": f"Session file not found: {filepath.name}. Use without --session-id to start a new session.",
            }, ensure_ascii=False))
            return
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(entry)
        h = session_id
    else:
        # ── 新建会话文件 ──
        h = session_hash()
        filepath = date_dir / f"{username}_{h}.md"
        while filepath.exists():
            h = session_hash()
            filepath = date_dir / f"{username}_{h}.md"
        header = _build_header(username, h, git_user)
        filepath.write_text(header + entry, encoding="utf-8")

    developer = f"{git_user['name']} <{git_user['email']}>" if git_user["email"] else git_user["name"]
    print(json.dumps({
        "status": "ok",
        "session_id": h,
        "file": f"{PROGRESS_DIR}/{date}/{username}_{h}.md",
        "developer": developer,
        "path": str(filepath),
    }, ensure_ascii=False))


def cmd_list(root: str):
    docs_dir = get_docs_dir(root)
    modules = scan_modules(docs_dir)
    progress = scan_progress(get_progress_dir(root), days=30)

    total_modules = sum(len(docs) for docs in modules.values())
    print(json.dumps({
        "status": "ok",
        "modules": modules,
        "module_docs_total": total_modules,
        "recent_progress": progress,
        "progress_count": len(progress),
    }, ensure_ascii=False))


def cmd_validate(root: str):
    docs_dir = get_docs_dir(root)
    if not docs_dir.exists():
        print(json.dumps({"status": "error", "message": "docs/ directory does not exist"}))
        return

    issues = []
    kebab = re.compile(r"^[a-z0-9\u4e00-\u9fff]+(-[a-z0-9\u4e00-\u9fff]+)*$")

    # 根目录散落文件
    for item in docs_dir.iterdir():
        if item.is_file() and item.suffix == ".md":
            issues.append({
                "type": "root_file",
                "file": item.name,
                "message": "文件应放入模块子目录",
            })

    # 空模块目录
    modules = scan_modules(docs_dir)
    for item in docs_dir.iterdir():
        if item.is_dir() and item.name not in (PROGRESS_DIR,) and item.name not in modules:
            issues.append({"type": "empty_module", "module": item.name})

    # 命名检查
    for module_name, docs in modules.items():
        if not kebab.match(module_name):
            issues.append({"type": "naming", "module": module_name, "message": "模块名应使用 kebab-case"})
        for doc in docs:
            stem = Path(doc["file"]).stem
            if not kebab.match(stem):
                issues.append({"type": "naming", "file": doc["file"], "message": "文件名应使用 kebab-case"})

    total = sum(len(docs) for docs in modules.values())
    print(json.dumps({
        "status": "ok" if not issues else "warning",
        "total_docs": total,
        "issues": issues,
    }, ensure_ascii=False))


def cmd_archive(root: str, older_than: int = 30):
    progress_dir = get_progress_dir(root)
    if not progress_dir.exists():
        print(json.dumps({"status": "error", "message": "progress/ directory does not exist"}))
        return

    cutoff = (datetime.now(timezone.utc) - timedelta(days=older_than)).strftime("%Y-%m-%d")
    archived = 0

    for date_dir in sorted(progress_dir.iterdir()):
        if not date_dir.is_dir() or date_dir.name == ARCHIVE_DIR:
            continue
        if date_dir.name >= cutoff:
            continue

        month = date_dir.name[:7]
        archive_month = progress_dir / ARCHIVE_DIR / month
        archive_month.mkdir(parents=True, exist_ok=True)

        dest = archive_month / date_dir.name
        shutil.move(str(date_dir), str(dest))
        archived += 1

    print(json.dumps({"status": "ok", "archived_days": archived, "cutoff": cutoff}))


def cmd_update(root: str, module: str, name: str, content: str, title: str | None = None):
    """创建或更新模块文档，内容由参数提供。"""
    docs_dir = get_docs_dir(root)
    module_dir = docs_dir / module
    module_dir.mkdir(parents=True, exist_ok=True)

    filepath = module_dir / f"{name}.md"
    doc_title = title or name
    is_new = not filepath.exists()

    full_content = f"# {doc_title}\n\n{content}\n"
    filepath.write_text(full_content, encoding="utf-8")

    print(json.dumps({
        "status": "ok",
        "action": "created" if is_new else "updated",
        "file": f"{module}/{name}.md",
        "module": module,
        "path": str(filepath),
    }, ensure_ascii=False))


# ── CLI 入口 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="docs-output: 文档产出管理")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="创建模块文档")
    p_create.add_argument("--root", required=True, help="项目根目录路径")
    p_create.add_argument("--module", required=True, help="模块名称")
    p_create.add_argument("--name", required=True, help="文档名称（不含扩展名）")
    p_create.add_argument("--title", default=None, help="文档一级标题（默认使用 name）")

    p_update = sub.add_parser("update", help="创建或更新模块文档（含内容）")
    p_update.add_argument("--root", required=True, help="项目根目录路径")
    p_update.add_argument("--module", required=True, help="模块名称")
    p_update.add_argument("--name", required=True, help="文档名称（不含扩展名）")
    p_update.add_argument("--content", required=True, help="文档正文内容（Markdown）")
    p_update.add_argument("--title", default=None, help="文档一级标题（默认使用 name）")

    p_progress = sub.add_parser("progress", help="记录会话进度")
    p_progress.add_argument("--root", required=True)
    p_progress.add_argument("--topic", required=True, help="主题")
    p_progress.add_argument("--type", required=True, dest="record_type",
                            choices=["需求开发", "Bug修复", "技术方案", "重构", "其他"])
    p_progress.add_argument("--summary", required=True, help="任务摘要")
    p_progress.add_argument("--session-id", default=None, dest="session_id",
                            help="已有会话ID（追加到同一文件），不传则新建会话")
    p_progress.add_argument("--files", default=None, help="变更文件JSON数组")
    p_progress.add_argument("--decisions", default=None, help="决策记录")
    p_progress.add_argument("--todos", default=None, help="遗留问题")

    p_list = sub.add_parser("list", help="列出文档和进度")
    p_list.add_argument("--root", required=True)

    p_val = sub.add_parser("validate", help="校验目录健康状态")
    p_val.add_argument("--root", required=True)

    p_archive = sub.add_parser("archive", help="归档旧进度记录")
    p_archive.add_argument("--root", required=True)
    p_archive.add_argument("--older-than", type=int, default=30, dest="older_than",
                           help="归档N天前的记录（默认30）")

    args = parser.parse_args()

    if args.command == "create":
        cmd_create(args.root, args.module, args.name, getattr(args, "title", None))
    elif args.command == "update":
        cmd_update(args.root, args.module, args.name, args.content, getattr(args, "title", None))
    elif args.command == "progress":
        cmd_progress(args.root, args.topic, args.record_type, args.summary,
                     session_id=getattr(args, "session_id", None),
                     files=getattr(args, "files", None),
                     decisions=getattr(args, "decisions", None),
                     todos=getattr(args, "todos", None))
    elif args.command == "list":
        cmd_list(args.root)
    elif args.command == "validate":
        cmd_validate(args.root)
    elif args.command == "archive":
        cmd_archive(args.root, args.older_than)


if __name__ == "__main__":
    main()
