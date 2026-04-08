#!/usr/bin/env python3
"""需求澄清文档管理脚本。

负责创建和更新 QA 会话的 Markdown 记录文件，确保多轮问答有稳定的落盘点。
提问逻辑由 Skill 和模型决定，本脚本只做文档管理。

用法：
  # 开始新会话
  python3 qa_session.py start --topic "用户登录功能" --initial-request "我要做一个登录功能"

  # 记录一轮问答
  python3 qa_session.py append-turn \
    --doc-path "docs/qa/login.md" \
    --question "支持哪些登录方式？" \
    --answer "手机号+验证码、邮箱+密码" \
    --confirmed "支持手机号+验证码登录" \
    --confirmed "支持邮箱+密码登录" \
    --open-item "是否需要第三方登录" \
    --current-understanding "核心登录方式已确认，待确认第三方登录和安全策略"

  # 结束会话，生成最终摘要
  python3 qa_session.py finalize \
    --doc-path "docs/qa/login.md" \
    --final-summary "登录功能需求已收敛" \
    --deliverable "需求摘要文档"
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    """把主题转成适合文件名的 slug。"""
    lowered = text.strip().lower()
    lowered = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or "qa-session"


def now_text() -> str:
    """返回本地时间字符串。"""
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def find_output_dir() -> Path:
    """向上查找仓库根目录，返回 docs/qa/ 路径。"""
    current = Path(__file__).resolve()
    for parent in [current, *current.parents]:
        if (parent / ".git").exists() or (parent / ".github").exists():
            target = parent / "docs" / "qa"
            target.mkdir(parents=True, exist_ok=True)
            return target
    # 找不到仓库根，就用当前目录
    target = Path.cwd() / "docs" / "qa"
    target.mkdir(parents=True, exist_ok=True)
    return target


def cmd_start(args: argparse.Namespace) -> None:
    """创建新的 QA 会话文档。"""
    output_dir = find_output_dir()
    slug = slugify(args.topic)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{slug}-{timestamp}.md"
    doc_path = output_dir / filename

    content = f"""---
topic: {args.topic}
created: {now_text()}
status: in-progress
---

# QA 会话：{args.topic}

## 原始需求

{args.initial_request}

## 已确认事项

（暂无）

## 未决问题

（暂无）

## 对话记录

"""
    doc_path.write_text(content, encoding="utf-8")
    print(f"doc_path={doc_path}")


def cmd_append_turn(args: argparse.Namespace) -> None:
    """追加一轮问答记录。"""
    doc_path = Path(args.doc_path)
    if not doc_path.exists():
        raise FileNotFoundError(f"文档不存在：{doc_path}")

    content = doc_path.read_text(encoding="utf-8")

    # 构建本轮记录
    turn_text = f"\n### {now_text()}\n\n"
    turn_text += f"**问题**：{args.question}\n\n"
    turn_text += f"**回答**：{args.answer}\n\n"

    if args.confirmed:
        turn_text += "**新增确认**：\n"
        for item in args.confirmed:
            turn_text += f"- ✅ {item}\n"
        turn_text += "\n"

    if args.open_item:
        turn_text += "**仍待确认**：\n"
        for item in args.open_item:
            turn_text += f"- ❓ {item}\n"
        turn_text += "\n"

    if args.current_understanding:
        turn_text += f"**当前理解**：{args.current_understanding}\n\n"

    if args.draft_output:
        turn_text += f"**草稿产出**：{args.draft_output}\n\n"

    turn_text += "---\n"

    content += turn_text

    # 更新已确认事项汇总
    if args.confirmed:
        confirmed_section = "\n## 已确认事项\n\n"
        # 收集所有已有确认项
        existing = re.findall(r"✅ (.+)", content)
        for item in existing:
            confirmed_section += f"- ✅ {item}\n"
        content = re.sub(
            r"\n## 已确认事项\n\n.*?(?=\n## )",
            confirmed_section + "\n",
            content,
            count=1,
            flags=re.DOTALL,
        )

    # 更新未决问题汇总
    if args.open_item:
        open_section = "\n## 未决问题\n\n"
        for item in args.open_item:
            open_section += f"- ❓ {item}\n"
        content = re.sub(
            r"\n## 未决问题\n\n.*?(?=\n## )",
            open_section + "\n",
            content,
            count=1,
            flags=re.DOTALL,
        )

    doc_path.write_text(content, encoding="utf-8")
    print(f"turn_appended={doc_path}")


def cmd_finalize(args: argparse.Namespace) -> None:
    """结束会话，写入最终摘要。"""
    doc_path = Path(args.doc_path)
    if not doc_path.exists():
        raise FileNotFoundError(f"文档不存在：{doc_path}")

    content = doc_path.read_text(encoding="utf-8")

    # 更新 YAML frontmatter 状态
    content = content.replace("status: in-progress", "status: completed")

    # 追加最终摘要
    finalize_text = f"\n## 最终摘要\n\n"
    finalize_text += f"**完成时间**：{now_text()}\n\n"
    finalize_text += f"**总结**：{args.final_summary}\n\n"
    finalize_text += f"**交付物**：{args.deliverable}\n"

    content += finalize_text
    doc_path.write_text(content, encoding="utf-8")
    print(f"finalized={doc_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="QA 会话文档管理")
    sub = parser.add_subparsers(dest="command", required=True)

    # start
    p_start = sub.add_parser("start", help="创建新会话文档")
    p_start.add_argument("--topic", required=True, help="会话主题")
    p_start.add_argument("--initial-request", required=True, help="用户原始需求")

    # append-turn
    p_append = sub.add_parser("append-turn", help="追加一轮问答")
    p_append.add_argument("--doc-path", required=True, help="文档路径")
    p_append.add_argument("--question", required=True, help="本轮提问")
    p_append.add_argument("--answer", required=True, help="用户回答")
    p_append.add_argument("--confirmed", action="append", help="新增确认事项（可多次）")
    p_append.add_argument("--open-item", action="append", help="仍待确认问题（可多次）")
    p_append.add_argument("--current-understanding", help="当前理解")
    p_append.add_argument("--draft-output", help="草稿产出")

    # finalize
    p_final = sub.add_parser("finalize", help="结束会话")
    p_final.add_argument("--doc-path", required=True, help="文档路径")
    p_final.add_argument("--final-summary", required=True, help="最终总结")
    p_final.add_argument("--deliverable", required=True, help="交付物描述")

    args = parser.parse_args()

    if args.command == "start":
        cmd_start(args)
    elif args.command == "append-turn":
        cmd_append_turn(args)
    elif args.command == "finalize":
        cmd_finalize(args)


if __name__ == "__main__":
    main()
