#!/usr/bin/env python3
"""
dep_extractor: 静态依赖提取器

从源码文件中提取 import/require 语句，解析为结构化依赖记录。
支持 TypeScript/JavaScript、Python、Java。

用法（独立运行 — 仅调试用）:
    python dep_extractor.py --file <source_file> --root <project_root>

通常由 context_db.py deps 子命令批量调用。
"""

import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

# ── TypeScript / JavaScript ───────────────────────────────

# import { X, Y } from '...'
# import X from '...'
# import * as X from '...'
# import type { X } from '...'
_RE_ES_IMPORT = re.compile(
    r"""import\s+"""
    r"""(?P<type>type\s+)?"""               # optional 'type' keyword
    r"""(?:"""
    r"""(?P<symbols>\{[^}]+\})|"""          # named: { X, Y }
    r"""(?:\*\s+as\s+\w+)|"""              # namespace: * as X
    r"""(?P<default>\w+)"""                 # default: X
    r""")"""
    r"""\s+from\s+['"](?P<path>[^'"]+)['"]""",
    re.MULTILINE,
)

# import '...'  (side-effect import)
_RE_ES_SIDE_EFFECT = re.compile(
    r"""import\s+['"](?P<path>[^'"]+)['"]""",
    re.MULTILINE,
)

# const X = require('...')  /  require('...')
_RE_CJS_REQUIRE = re.compile(
    r"""(?:const|let|var)\s+(?:\{[^}]+\}|\w+)\s*=\s*require\s*\(\s*['"](?P<path>[^'"]+)['"]\s*\)""",
    re.MULTILINE,
)

# import('...')  dynamic import
_RE_DYNAMIC_IMPORT = re.compile(
    r"""import\s*\(\s*['"](?P<path>[^'"]+)['"]\s*\)""",
    re.MULTILINE,
)

# export { X } from '...'  /  export * from '...'
_RE_RE_EXPORT = re.compile(
    r"""export\s+(?:(?P<symbols>\{[^}]+\})|\*)\s+from\s+['"](?P<path>[^'"]+)['"]""",
    re.MULTILINE,
)

# ── Python ────────────────────────────────────────────────

# import X  /  import X as Y
_RE_PY_IMPORT = re.compile(
    r"""^import\s+(?P<module>[\w.]+)""",
    re.MULTILINE,
)

# from X import Y  /  from X import *
_RE_PY_FROM_IMPORT = re.compile(
    r"""^from\s+(?P<module>[\w.]+)\s+import\s+(?P<names>[^#\n]+)""",
    re.MULTILINE,
)

# ── Java ──────────────────────────────────────────────────

_RE_JAVA_IMPORT = re.compile(
    r"""^import\s+(?P<static>static\s+)?(?P<path>[\w.*]+)\s*;""",
    re.MULTILINE,
)


# ── 解析逻辑 ─────────────────────────────────────────────

def _parse_symbols(raw: Optional[str]) -> list[str]:
    """Parse '{ X, Y as Z }' into ['X', 'Y']."""
    if not raw:
        return []
    inner = raw.strip("{}").strip()
    return [s.split(" as ")[0].split(" as ")[0].strip() for s in inner.split(",") if s.strip()]


def _resolve_ts_path(import_path: str, source_dir: str, root: str) -> Optional[str]:
    """Resolve a TS/JS import specifier to a project-relative file path.

    Returns None for bare specifiers (node_modules packages).
    """
    if not import_path.startswith(".") and not import_path.startswith("/"):
        return None  # bare specifier → external package

    if import_path.startswith("/"):
        abs_path = os.path.join(root, import_path.lstrip("/"))
    else:
        abs_path = os.path.normpath(os.path.join(source_dir, import_path))

    candidates = [abs_path]
    for ext in (".ts", ".tsx", ".js", ".jsx", ".vue", "/index.ts", "/index.tsx", "/index.js"):
        candidates.append(abs_path + ext)

    for c in candidates:
        if os.path.isfile(c):
            return os.path.relpath(c, root)
    return None


def _resolve_py_module(module: str, source_dir: str, root: str) -> Optional[str]:
    """Resolve a Python module path to a project-relative file path.

    Returns None for external packages.
    """
    parts = module.split(".")
    # Try as relative from source_dir
    rel = os.path.join(source_dir, *parts)
    for candidate in [rel + ".py", os.path.join(rel, "__init__.py")]:
        if os.path.isfile(candidate):
            return os.path.relpath(candidate, root)
    # Try as absolute from root
    abs_rel = os.path.join(root, *parts)
    for candidate in [abs_rel + ".py", os.path.join(abs_rel, "__init__.py")]:
        if os.path.isfile(candidate):
            return os.path.relpath(candidate, root)
    return None


def _resolve_java_import(import_path: str, root: str) -> Optional[str]:
    """Resolve a Java import to a project-relative .java file path."""
    # com.example.service.UserService → src/main/java/com/example/service/UserService.java
    parts = import_path.rstrip(".*").split(".")
    rel = os.path.join(*parts) + ".java"
    for src_root in ("src/main/java", "src"):
        candidate = os.path.join(root, src_root, rel)
        if os.path.isfile(candidate):
            return os.path.relpath(candidate, root)
    return None


def extract_ts_js(content: str, source_dir: str, root: str) -> list[dict]:
    """Extract dependencies from TypeScript/JavaScript source."""
    deps = []

    for m in _RE_ES_IMPORT.finditer(content):
        is_type = bool(m.group("type"))
        symbols = _parse_symbols(m.group("symbols"))
        if m.group("default"):
            symbols.append(m.group("default"))
        target = _resolve_ts_path(m.group("path"), source_dir, root)
        if target:
            deps.append({
                "target_path": target,
                "import_type": "import",
                "symbols": symbols or None,
                "is_type_only": 1 if is_type else 0,
            })

    for m in _RE_ES_SIDE_EFFECT.finditer(content):
        # Skip if already matched by _RE_ES_IMPORT
        target = _resolve_ts_path(m.group("path"), source_dir, root)
        if target:
            deps.append({
                "target_path": target,
                "import_type": "import",
                "symbols": None,
                "is_type_only": 0,
            })

    for m in _RE_CJS_REQUIRE.finditer(content):
        target = _resolve_ts_path(m.group("path"), source_dir, root)
        if target:
            deps.append({
                "target_path": target,
                "import_type": "require",
                "symbols": None,
                "is_type_only": 0,
            })

    for m in _RE_DYNAMIC_IMPORT.finditer(content):
        target = _resolve_ts_path(m.group("path"), source_dir, root)
        if target:
            deps.append({
                "target_path": target,
                "import_type": "dynamic_import",
                "symbols": None,
                "is_type_only": 0,
            })

    for m in _RE_RE_EXPORT.finditer(content):
        symbols = _parse_symbols(m.group("symbols"))
        target = _resolve_ts_path(m.group("path"), source_dir, root)
        if target:
            deps.append({
                "target_path": target,
                "import_type": "re_export",
                "symbols": symbols or None,
                "is_type_only": 0,
            })

    return deps


def extract_python(content: str, source_dir: str, root: str) -> list[dict]:
    """Extract dependencies from Python source using ast fallback to regex."""
    deps = []

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target = _resolve_py_module(alias.name, source_dir, root)
                    if target:
                        deps.append({
                            "target_path": target,
                            "import_type": "import",
                            "symbols": None,
                            "is_type_only": 0,
                        })
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    names = [a.name for a in node.names if a.name != "*"]
                    target = _resolve_py_module(node.module, source_dir, root)
                    if target:
                        deps.append({
                            "target_path": target,
                            "import_type": "import",
                            "symbols": names or None,
                            "is_type_only": 0,
                        })
    except SyntaxError:
        # Fallback to regex
        for m in _RE_PY_IMPORT.finditer(content):
            target = _resolve_py_module(m.group("module"), source_dir, root)
            if target:
                deps.append({
                    "target_path": target,
                    "import_type": "import",
                    "symbols": None,
                    "is_type_only": 0,
                })
        for m in _RE_PY_FROM_IMPORT.finditer(content):
            names = [n.strip().split(" as ")[0] for n in m.group("names").split(",") if n.strip() and n.strip() != "*"]
            target = _resolve_py_module(m.group("module"), source_dir, root)
            if target:
                deps.append({
                    "target_path": target,
                    "import_type": "import",
                    "symbols": names or None,
                    "is_type_only": 0,
                })

    return deps


def extract_java(content: str, root: str) -> list[dict]:
    """Extract dependencies from Java source."""
    deps = []
    for m in _RE_JAVA_IMPORT.finditer(content):
        target = _resolve_java_import(m.group("path"), root)
        if target:
            deps.append({
                "target_path": target,
                "import_type": "import",
                "symbols": None,
                "is_type_only": 0,
            })
    return deps


# ── 入口 ─────────────────────────────────────────────────

LANG_MAP = {
    ".ts": "ts", ".tsx": "ts", ".js": "ts", ".jsx": "ts",
    ".vue": "ts",  # <script> block treated as TS
    ".py": "python",
    ".java": "java",
}


def extract_file(file_path: str, root: str) -> list[dict]:
    """Extract all dependencies from a single file.

    Returns list of dicts with keys: target_path, import_type, symbols, is_type_only.
    """
    ext = os.path.splitext(file_path)[1].lower()
    lang = LANG_MAP.get(ext)
    if not lang:
        return []

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except (OSError, PermissionError):
        return []

    source_dir = os.path.dirname(os.path.abspath(file_path))

    if lang == "ts":
        return extract_ts_js(content, source_dir, root)
    elif lang == "python":
        return extract_python(content, source_dir, root)
    elif lang == "java":
        return extract_java(content, root)
    return []


# ── CLI（调试用）─────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="dep_extractor: 静态依赖提取")
    parser.add_argument("--file", required=True, help="源文件路径")
    parser.add_argument("--root", required=True, help="项目根目录")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    deps = extract_file(args.file, root)
    source_rel = os.path.relpath(args.file, root)

    result = []
    for d in deps:
        result.append({
            "source_path": source_rel,
            **d,
            "symbols": json.dumps(d["symbols"]) if d["symbols"] else None,
        })

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
