#!/usr/bin/env python3
"""
engineering-principles: 工程原则匹配脚本

用法:
    python principles_matcher.py match --root <project_root> [--task <任务描述>] [--format json|markdown]
"""

import argparse
import json
import os
from pathlib import Path

# ── 原则分类定义 ──────────────────────────────────────────────

PRINCIPLES = [
    {
        "id": "clean-code",
        "name": "Clean Code",
        "always": True,
        "condition": None,
        "ref": "quality-checklist.md",
        "summary": "命名规范、函数 ≤ 30 行、避免 magic number、注释解释 why 不解释 what",
    },
    {
        "id": "error-handling",
        "name": "错误处理",
        "always": True,
        "condition": None,
        "ref": "quality-checklist.md",
        "summary": "业务/系统异常分级、不吞异常、边界处统一捕获、入口校验",
    },
    {
        "id": "solid",
        "name": "SOLID 原则",
        "always": False,
        "condition": "oop",
        "ref": "solid-principles.md",
        "summary": "SRP 单一职责, OCP 开闭, LSP 里氏替换, ISP 接口隔离, DIP 依赖倒置",
    },
    {
        "id": "ddd",
        "name": "DDD 分层",
        "always": False,
        "condition": "ddd",
        "ref": "ddd-patterns.md",
        "summary": "聚合、限界上下文、领域服务、值对象、仓储模式",
    },
    {
        "id": "tdd",
        "name": "TDD 测试驱动",
        "always": False,
        "condition": "test-framework",
        "ref": "tdd-workflow.md",
        "summary": "红绿重构循环、测试金字塔、Bug 先写复现测试",
    },
    {
        "id": "bdd",
        "name": "BDD 行为驱动",
        "always": False,
        "condition": "e2e-framework",
        "ref": "tdd-workflow.md",
        "summary": "Gherkin 验收场景、用户行为驱动测试",
    },
    {
        "id": "design-patterns",
        "name": "设计模式",
        "always": False,
        "condition": "oop",
        "ref": "design-patterns.md",
        "summary": "策略、工厂、观察者、适配器——仅在识别到适用信号时引入",
    },
    {
        "id": "testability",
        "name": "可测试性",
        "always": False,
        "condition": "test-framework-or-new",
        "ref": "quality-checklist.md",
        "summary": "依赖注入、纯函数优先、外部依赖接口隔离",
    },
    {
        "id": "performance",
        "name": "性能意识",
        "always": False,
        "condition": "database",
        "ref": "quality-checklist.md",
        "summary": "避免 N+1、检查索引、按需 select、缓存重复计算",
    },
    {
        "id": "security",
        "name": "安全实践",
        "always": False,
        "condition": "user-input",
        "ref": "quality-checklist.md",
        "summary": "参数化查询、XSS 防护、CSRF token、权限校验、敏感数据脱敏",
    },
]

# ── 上下文扫描 ──────────────────────────────────────────────

IGNORE_DIRS = {
    "node_modules", "dist", "build", ".git", "__pycache__",
    ".next", ".nuxt", ".output", "coverage", ".cache", "target",
}

TEST_FRAMEWORK_SIGNALS = [
    "jest.config", "vitest.config", "pytest.ini", "pyproject.toml",
    "conftest.py", "setup.cfg", "__tests__",
]

E2E_SIGNALS = ["cypress", "cypress.config", "playwright.config", "playwright"]

ORM_SIGNALS = ["prisma", "typeorm", "sequelize", "drizzle", "mybatis", "hibernate"]


def scan_context(root: str) -> dict:
    """扫描项目上下文。"""
    ctx = {
        "has_project": False,
        "total_files": 0,
        "modules": [],
        "language": "unknown",
        "framework": "unknown",
        "has_test_framework": False,
        "has_e2e": False,
        "has_orm": False,
        "has_layered_structure": False,
        "is_new_project": False,
        "project_size": "unknown",
    }

    root_path = Path(root).resolve()
    if not root_path.exists():
        return ctx
    ctx["has_project"] = True

    # 计算文件数量
    file_count = 0
    has_src = False
    has_tests = False
    dir_names = set()

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        rel = Path(dirpath).relative_to(root_path)
        dir_names.add(str(rel))

        for fname in filenames:
            file_count += 1

    ctx["total_files"] = file_count

    # 项目规模
    if file_count == 0:
        ctx["is_new_project"] = True
        ctx["project_size"] = "new"
    elif file_count < 50:
        ctx["project_size"] = "small"
    elif file_count < 500:
        ctx["project_size"] = "medium"
    else:
        ctx["project_size"] = "large"

    # 语言/框架检测
    root_files = [f.name for f in root_path.iterdir() if f.is_file()]

    if "package.json" in root_files:
        ctx["language"] = "typescript/javascript"
        pkg_path = root_path / "package.json"
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

            if "next" in deps:
                ctx["framework"] = "Next.js"
            elif "nuxt" in deps or "@nuxt/kit" in deps:
                ctx["framework"] = "Nuxt"
            elif "@nestjs/core" in deps:
                ctx["framework"] = "NestJS"
            elif "vue" in deps:
                ctx["framework"] = "Vue"
            elif "react" in deps:
                ctx["framework"] = "React"
            elif "express" in deps:
                ctx["framework"] = "Express"

            # 测试框架
            for test_dep in ["jest", "vitest", "@jest/core", "mocha", "ava"]:
                if test_dep in deps:
                    ctx["has_test_framework"] = True
                    break

            # E2E
            for e2e_dep in ["cypress", "@playwright/test", "playwright"]:
                if e2e_dep in deps:
                    ctx["has_e2e"] = True
                    break

            # ORM
            for orm_dep in ["typeorm", "prisma", "@prisma/client", "sequelize", "drizzle-orm"]:
                if orm_dep in deps:
                    ctx["has_orm"] = True
                    break

        except (json.JSONDecodeError, OSError):
            pass

    elif "pom.xml" in root_files or "build.gradle" in root_files:
        ctx["language"] = "java"
        ctx["framework"] = "Spring Boot"
        ctx["has_test_framework"] = True  # Java 项目通常自带 JUnit
        ctx["has_orm"] = True

    elif "pyproject.toml" in root_files or "setup.py" in root_files:
        ctx["language"] = "python"

    # 分层结构检测
    layer_indicators = {"controller", "service", "repository", "domain", "infrastructure", "application"}
    for d in dir_names:
        parts = d.lower().split("/")
        if layer_indicators.intersection(parts):
            ctx["has_layered_structure"] = True
            break

    # 测试目录检测（补充）
    for test_dir in ["__tests__", "test", "tests", "spec"]:
        if (root_path / test_dir).exists() or (root_path / "src" / test_dir).exists():
            ctx["has_test_framework"] = True
            break

    # 模块识别
    src = root_path / "src"
    if src.exists():
        ctx["modules"] = sorted([
            d.name for d in src.iterdir()
            if d.is_dir() and d.name not in IGNORE_DIRS
        ])

    return ctx


# ── 原则匹配 ──────────────────────────────────────────────

TASK_SECURITY_KEYWORDS = [
    "登录", "注册", "认证", "auth", "密码", "password",
    "api", "接口", "表单", "输入", "input",
]

TASK_DB_KEYWORDS = [
    "数据库", "database", "查询", "query", "表", "table",
    "sql", "orm", "crud", "列表", "分页",
]


def match_principles(ctx: dict, task: str | None = None) -> dict:
    """根据上下文匹配适用原则。"""
    always_applicable = []
    detected_applicable = []
    skipped = []

    task_lower = (task or "").lower()

    for p in PRINCIPLES:
        if p["always"]:
            always_applicable.append({
                "id": p["id"],
                "name": p["name"],
                "summary": p["summary"],
                "ref": p["ref"],
            })
            continue

        cond = p["condition"]
        applicable = False
        reason = ""

        if cond == "oop":
            if ctx.get("language") in ("typescript/javascript", "java", "python"):
                applicable = True
                reason = f"检测到 OOP 语言: {ctx['language']}"
            else:
                reason = "未检测到 OOP 语言"

        elif cond == "ddd":
            if ctx.get("has_layered_structure") and ctx.get("project_size") in ("medium", "large"):
                applicable = True
                reason = "检测到分层结构且项目规模 ≥ 中型"
            elif ctx.get("project_size") == "large" and len(ctx.get("modules", [])) >= 3:
                applicable = True
                reason = f"大型项目，{len(ctx['modules'])} 个模块"
            else:
                reason = "项目规模不足或无分层结构"

        elif cond == "test-framework":
            if ctx.get("has_test_framework"):
                applicable = True
                reason = "检测到测试框架"
            else:
                reason = "未检测到测试框架"

        elif cond == "e2e-framework":
            if ctx.get("has_e2e"):
                applicable = True
                reason = "检测到 E2E 框架"
            else:
                reason = "未检测到 E2E 框架（cypress/playwright）"

        elif cond == "test-framework-or-new":
            if ctx.get("has_test_framework") or ctx.get("is_new_project"):
                applicable = True
                reason = "有测试框架" if ctx.get("has_test_framework") else "新项目（推荐）"
            else:
                reason = "无测试框架且非新项目"

        elif cond == "database":
            if ctx.get("has_orm"):
                applicable = True
                reason = "检测到 ORM/数据库依赖"
            elif any(kw in task_lower for kw in TASK_DB_KEYWORDS):
                applicable = True
                reason = "任务描述涉及数据库操作"
            else:
                reason = "未检测到数据库相关内容"

        elif cond == "user-input":
            if any(kw in task_lower for kw in TASK_SECURITY_KEYWORDS):
                applicable = True
                reason = "任务描述涉及用户输入/认证"
            else:
                reason = "任务描述未涉及用户输入/安全相关"

        if applicable:
            detected_applicable.append({
                "id": p["id"],
                "name": p["name"],
                "summary": p["summary"],
                "ref": p["ref"],
                "reason": reason,
            })
        else:
            skipped.append({
                "id": p["id"],
                "name": p["name"],
                "reason": reason,
            })

    return {
        "always": always_applicable,
        "detected": detected_applicable,
        "skipped": skipped,
    }


# ── 输出格式化 ──────────────────────────────────────────────

def format_markdown(ctx: dict, matched: dict, task: str | None) -> str:
    lines = [
        "# 工程原则匹配报告",
        "",
        "## 项目上下文",
        f"- 语言/框架: {ctx.get('language', 'unknown')} + {ctx.get('framework', 'unknown')}",
        f"- 测试框架: {'已配置' if ctx.get('has_test_framework') else '未检测到'}",
        f"- E2E 框架: {'已配置' if ctx.get('has_e2e') else '未检测到'}",
        f"- 项目规模: {ctx.get('project_size', 'unknown')}（{ctx.get('total_files', 0)} 文件）",
        f"- 分层结构: {'是' if ctx.get('has_layered_structure') else '否'}",
        f"- ORM/数据库: {'是' if ctx.get('has_orm') else '否'}",
    ]

    if task:
        lines.append(f"- 当前任务: {task}")
    lines.append("")

    lines.append("## 适用原则")
    lines.append("")
    lines.append("### ✅ 始终适用")
    for p in matched["always"]:
        lines.append(f"- **{p['name']}**: {p['summary']}")
    lines.append("")

    if matched["detected"]:
        lines.append("### ✅ 经检测适用")
        for p in matched["detected"]:
            lines.append(f"- **{p['name']}**: {p['summary']}（{p['reason']}）")
        lines.append("")

    if matched["skipped"]:
        lines.append("### ⏭️ 不适用")
        for p in matched["skipped"]:
            lines.append(f"- **{p['name']}**: {p['reason']}")
        lines.append("")

    # 简短约束清单
    lines.append("## 约束清单（编码时参考）")
    lines.append("")
    lines.append("```")
    for p in matched["always"]:
        lines.append(f"- {p['name']}: {p['summary'].split('、')[0]}")
    for p in matched["detected"]:
        lines.append(f"- {p['name']}: {p['summary'].split('、')[0]}")
    lines.append("```")

    return "\n".join(lines)


def format_json(ctx: dict, matched: dict) -> str:
    return json.dumps({"context": ctx, "principles": matched}, ensure_ascii=False, indent=2)


# ── CLI ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="engineering-principles: 工程原则匹配")
    sub = parser.add_subparsers(dest="command", required=True)

    p_match = sub.add_parser("match", help="匹配适用原则")
    p_match.add_argument("--root", required=True, help="项目根目录")
    p_match.add_argument("--task", default=None, help="当前任务描述")
    p_match.add_argument("--format", default="markdown", choices=["json", "markdown"])

    args = parser.parse_args()

    if args.command == "match":
        ctx = scan_context(args.root)
        matched = match_principles(ctx, args.task)

        if args.format == "json":
            print(format_json(ctx, matched))
        else:
            print(format_markdown(ctx, matched, args.task))


if __name__ == "__main__":
    main()
