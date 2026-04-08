#!/usr/bin/env python3
"""
task-difficulty: 任务难度评估脚本

用法:
    python difficulty_scorer.py assess --input <任务描述> [--root <project_root>] [--format json|markdown]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ── 维度定义 ──────────────────────────────────────────────

DIMENSIONS = [
    {"key": "scope", "name": "范围", "weight": 0.30},
    {"key": "depth", "name": "深度", "weight": 0.25},
    {"key": "coupling", "name": "耦合", "weight": 0.20},
    {"key": "risk", "name": "风险", "weight": 0.15},
    {"key": "cognition", "name": "认知", "weight": 0.10},
]

LEVEL_RANGES = [
    (1.0, 2.0, "L1", "琐碎"),
    (2.1, 4.0, "L2", "简单"),
    (4.1, 6.0, "L3", "中等"),
    (6.1, 8.0, "L4", "复杂"),
    (8.1, 10.0, "L5", "重大"),
]

THROTTLE_BIAS = 0.5


def score_to_level(score: float) -> tuple[str, str]:
    """将加权分映射为等级。"""
    for low, high, level, label in LEVEL_RANGES:
        if low <= score <= high:
            return level, label
    return "L5", "重大"


def level_label(level: str) -> str:
    for _, _, lv, label in LEVEL_RANGES:
        if lv == level:
            return label
    return ""


def should_exempt_throttle(scores: dict[str, int]) -> bool:
    """豁免偏置判定：范围≤2 且 深度≤2 且 耦合≤2 且 风险≤3。"""
    return (
        scores.get("scope", 0) <= 2
        and scores.get("depth", 0) <= 2
        and scores.get("coupling", 0) <= 2
        and scores.get("risk", 0) <= 3
    )


def compute_weighted(scores: dict[str, int]) -> float:
    total = 0.0
    for dim in DIMENSIONS:
        total += scores.get(dim["key"], 5) * dim["weight"]
    return round(total, 2)


# ── 上下文探索 ──────────────────────────────────────────────

def explore_context(root: str, task_text: str) -> dict:
    """探索项目上下文，提取与任务相关的结构信息。"""
    context = {
        "has_project": False,
        "total_files": 0,
        "modules": [],
        "config_files": [],
        "test_coverage": False,
        "keywords_found": [],
    }

    root_path = Path(root).resolve()
    if not root_path.exists():
        return context

    context["has_project"] = True

    ignore_dirs = {
        "node_modules", "dist", "build", ".git", "__pycache__",
        ".next", ".nuxt", ".output", "coverage", ".cache",
    }

    # 提取任务中的关键词
    words = set(re.findall(r"[a-zA-Z\u4e00-\u9fff]{2,}", task_text.lower()))

    files = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        rel_dir = Path(dirpath).relative_to(root_path)

        for fname in filenames:
            rel = str(rel_dir / fname)
            files.append(rel)

            # 检查文件名/路径是否与任务关键词相关
            fname_lower = fname.lower()
            for w in words:
                if w in fname_lower or w in str(rel_dir).lower():
                    context["keywords_found"].append({"keyword": w, "file": rel})

    context["total_files"] = len(files)

    # 识别模块（src/ 下的一级目录）
    src_path = root_path / "src"
    if src_path.exists():
        context["modules"] = [
            d.name for d in src_path.iterdir()
            if d.is_dir() and d.name not in ignore_dirs
        ]

    # 识别配置文件
    for f in root_path.iterdir():
        if f.is_file() and f.suffix in (".json", ".yaml", ".yml", ".toml"):
            context["config_files"].append(f.name)

    # 检查测试覆盖
    for test_pattern in ["__tests__", "test", "tests", "spec"]:
        if (root_path / test_pattern).exists():
            context["test_coverage"] = True
            break

    # 去重
    seen = set()
    unique = []
    for kf in context["keywords_found"]:
        key = f"{kf['keyword']}:{kf['file']}"
        if key not in seen:
            seen.add(key)
            unique.append(kf)
    context["keywords_found"] = unique[:20]

    return context


# ── 启发式预评分 ──────────────────────────────────────────────

# 关键词与难度倾向的映射
HIGH_COMPLEXITY_SIGNALS = [
    "迁移", "migration", "升级", "upgrade", "重构", "refactor",
    "权限", "permission", "auth", "安全", "security",
    "支付", "payment", "加密", "encrypt",
    "微服务", "microservice", "分布式", "distributed",
    "性能", "performance", "并发", "concurrent",
    "数据库", "database", "schema", "索引", "index",
]

LOW_COMPLEXITY_SIGNALS = [
    "文案", "文字", "typo", "拼写",
    "样式", "style", "颜色", "color",
    "注释", "comment", "文档", "readme",
    "版本号", "version",
]


def heuristic_scores(task_text: str, context: dict) -> dict:
    """基于启发式规则生成初始评分建议（供模型参考或作为无模型降级）。"""
    text_lower = task_text.lower()

    scores = {"scope": 3, "depth": 3, "coupling": 3, "risk": 3, "cognition": 3}

    # 高复杂度信号
    high_hits = sum(1 for s in HIGH_COMPLEXITY_SIGNALS if s in text_lower)
    if high_hits >= 4:
        for k in scores:
            scores[k] = min(10, scores[k] + 4)
    elif high_hits >= 2:
        for k in scores:
            scores[k] = min(10, scores[k] + 2)
    elif high_hits == 1:
        for k in scores:
            scores[k] = min(10, scores[k] + 1)

    # 低复杂度信号
    low_hits = sum(1 for s in LOW_COMPLEXITY_SIGNALS if s in text_lower)
    if low_hits >= 2 and high_hits == 0:
        for k in scores:
            scores[k] = max(1, scores[k] - 2)
    elif low_hits == 1 and high_hits == 0:
        for k in scores:
            scores[k] = max(1, scores[k] - 1)

    # 上下文修正
    if context.get("has_project"):
        total = context.get("total_files", 0)
        if total > 500:
            scores["scope"] = min(10, scores["scope"] + 1)
        if total > 1000:
            scores["scope"] = min(10, scores["scope"] + 1)
        keywords = context.get("keywords_found", [])
        if len(keywords) > 10:
            scores["coupling"] = min(10, scores["coupling"] + 1)

    # 信息不足修正（无项目上下文）
    if not context.get("has_project"):
        for k in scores:
            scores[k] = min(10, scores[k] + 1)

    # 任务描述太短 → 信息不足
    if len(task_text.strip()) < 20:
        scores["cognition"] = min(10, scores["cognition"] + 1)
        scores["scope"] = min(10, scores["scope"] + 1)

    return scores


# ── 输出格式化 ──────────────────────────────────────────────

def format_markdown(result: dict) -> str:
    lines = [
        "# 难度评估报告",
        "",
        "## 基本信息",
        "",
        f"- **任务**: {result['task']}",
        f"- **原始评级**: {result['raw_level']} ({level_label(result['raw_level'])})",
        f"- **最终评级**: {result['final_level']} ({level_label(result['final_level'])})",
        f"- **上浮说明**: {result['throttle_reason']}",
        "",
        "## 评分明细",
        "",
        "| 维度 | 分数(1-10) | 权重 |",
        "|------|----------|------|",
    ]

    for dim in DIMENSIONS:
        score = result["scores"].get(dim["key"], 0)
        lines.append(f"| {dim['name']} | {score} | {int(dim['weight']*100)}% |")

    lines.append(f"| **加权** | **{result['weighted_score']}** | |")
    lines.append("")

    if result.get("context_summary"):
        lines.append("## 上下文分析")
        lines.append("")
        ctx = result["context_summary"]
        if ctx.get("total_files"):
            lines.append(f"- 项目文件总数: {ctx['total_files']}")
        if ctx.get("modules"):
            lines.append(f"- 识别模块: {', '.join(ctx['modules'])}")
        if ctx.get("keywords_found"):
            kw_list = [f"`{k['file']}`" for k in ctx["keywords_found"][:5]]
            lines.append(f"- 关联文件: {', '.join(kw_list)}")
        lines.append("")

    return "\n".join(lines)


def format_json(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)


# ── 命令实现 ──────────────────────────────────────────────

def cmd_assess(task_input: str, root: str | None = None, fmt: str = "markdown"):
    # 1. 追溯上下文
    context = {}
    if root:
        context = explore_context(root, task_input)

    # 2. 启发式评分
    scores = heuristic_scores(task_input, context)

    # 3. 计算加权分和等级
    weighted = compute_weighted(scores)
    raw_level, _ = score_to_level(weighted)

    # 4. 节流阀偏置
    if should_exempt_throttle(scores):
        final_weighted = weighted
        throttle_reason = "豁免偏置：范围/深度/耦合均低，风险可控"
    else:
        final_weighted = min(10.0, weighted + THROTTLE_BIAS)
        throttle_reason = f"加权分 +{THROTTLE_BIAS} 偏置：{weighted} → {final_weighted}"

    final_level, _ = score_to_level(final_weighted)

    result = {
        "task": task_input,
        "scores": scores,
        "weighted_score": weighted,
        "final_weighted": final_weighted,
        "raw_level": raw_level,
        "final_level": final_level,
        "throttle_reason": throttle_reason,
        "context_summary": {
            "total_files": context.get("total_files", 0),
            "modules": context.get("modules", []),
            "keywords_found": context.get("keywords_found", []),
            "has_project": context.get("has_project", False),
        } if context else None,
    }

    if fmt == "json":
        print(format_json(result))
    else:
        print(format_markdown(result))


# ── CLI 入口 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="task-difficulty: 任务难度评估")
    sub = parser.add_subparsers(dest="command", required=True)

    p_assess = sub.add_parser("assess", help="评估任务难度")
    p_assess.add_argument("--input", required=True, help="任务描述文本")
    p_assess.add_argument("--root", default=None, help="项目根目录（提供后会自动追溯上下文）")
    p_assess.add_argument("--format", default="markdown", choices=["json", "markdown"],
                          help="输出格式（默认 markdown）")

    args = parser.parse_args()

    if args.command == "assess":
        cmd_assess(args.input, args.root, args.format)


if __name__ == "__main__":
    main()
