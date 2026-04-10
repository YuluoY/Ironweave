#!/usr/bin/env python3
"""
Phase Chain Guard — 阶段链守卫

在 Plan→Execute→Validate→Deliver 四阶段转换处提供机械化检查点。
每个 phase 的 enter 需要前置 phase 的 gate-pass 作为前提条件。

用法:
    python phase_guard.py enter     --root <project_root> --slice <S1> --phase <plan|execute|validate|deliver>
    python phase_guard.py gate      --root <project_root> --slice <S1> --phase <plan|execute|validate|deliver> --result <pass|fail> [--outputs '<JSON>'] [--detail '<JSON>']
    python phase_guard.py reconcile --root <project_root> --slice <S1>
    python phase_guard.py status    --root <project_root> [--slice <S1>]

检查点逻辑:
    - enter plan:     无前提（首阶段），直接记录
    - enter execute:  要求 plan.gate-pass 已记录
    - enter validate: 要求 execute.gate-pass 已记录
    - enter deliver:  要求 validate.gate-pass 已记录
    - gate:           记录 gate 结果 + 验证产出文件存在性/哈希
    - reconcile:      验证完整链 plan→execute→validate→deliver 的 enter+gate-pass 均存在
    - status:         查询当前阶段状态
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path

DB_REL_PATH = ".cache/context.db"

PHASES = ["plan", "execute", "validate", "deliver"]
PHASE_ORDER = {p: i for i, p in enumerate(PHASES)}

# ── phase_log 表 DDL ─────────────────────────────────────

PHASE_LOG_DDL = """
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
    conn.executescript(PHASE_LOG_DDL)
    return conn


def file_hash(filepath: str) -> str:
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except (OSError, PermissionError):
        return ""


def has_event(conn: sqlite3.Connection, slice_id: str, phase: str, event: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM phase_log WHERE slice_id=? AND phase=? AND event=? LIMIT 1",
        (slice_id, phase, event),
    ).fetchone()
    return row is not None


def prior_phase(phase: str) -> str | None:
    idx = PHASE_ORDER.get(phase)
    if idx is None or idx == 0:
        return None
    return PHASES[idx - 1]


# ── enter 命令 ────────────────────────────────────────────

def cmd_enter(root: str, slice_id: str, phase: str, session_hash: str | None = None):
    if phase not in PHASE_ORDER:
        print(json.dumps({"status": "error", "message": f"Unknown phase: {phase}. Valid: {PHASES}"}))
        return

    root_path = Path(root).resolve()
    conn = get_db(str(root_path))

    # 检查前置条件
    prev = prior_phase(phase)
    if prev is not None:
        if not has_event(conn, slice_id, prev, "gate-pass"):
            conn.close()
            print(json.dumps({
                "status": "blocked",
                "slice": slice_id,
                "phase": phase,
                "reason": f"Prior phase '{prev}' has no gate-pass record. Cannot enter '{phase}'.",
                "required": f"{prev}.gate-pass",
            }))
            return

    # 检查是否已经进入
    if has_event(conn, slice_id, phase, "enter"):
        conn.close()
        print(json.dumps({
            "status": "ok",
            "slice": slice_id,
            "phase": phase,
            "note": "Already entered (idempotent).",
        }))
        return

    # 记录 enter
    conn.execute(
        "INSERT INTO phase_log (slice_id, phase, event, session_hash) VALUES (?, ?, 'enter', ?)",
        (slice_id, phase, session_hash),
    )
    conn.commit()
    conn.close()
    print(json.dumps({"status": "ok", "slice": slice_id, "phase": phase, "event": "enter"}))


# ── gate 命令 ─────────────────────────────────────────────

def cmd_gate(root: str, slice_id: str, phase: str, result: str,
             outputs_json: str | None = None, detail_json: str | None = None,
             session_hash: str | None = None):
    if phase not in PHASE_ORDER:
        print(json.dumps({"status": "error", "message": f"Unknown phase: {phase}. Valid: {PHASES}"}))
        return
    if result not in ("pass", "fail"):
        print(json.dumps({"status": "error", "message": f"Invalid result: {result}. Valid: pass, fail"}))
        return

    root_path = Path(root).resolve()
    conn = get_db(str(root_path))

    # 验证已 enter
    if not has_event(conn, slice_id, phase, "enter"):
        conn.close()
        print(json.dumps({
            "status": "error",
            "message": f"Phase '{phase}' was never entered for slice '{slice_id}'. Call enter first.",
        }))
        return

    # 验证产出文件（如有）
    verified_outputs = []
    if outputs_json:
        try:
            outputs = json.loads(outputs_json)
        except json.JSONDecodeError as e:
            conn.close()
            print(json.dumps({"status": "error", "message": f"Invalid outputs JSON: {e}"}))
            return

        for out in outputs:
            fpath = out.get("path", "")
            full_path = root_path / fpath
            if not full_path.exists():
                verified_outputs.append({"path": fpath, "exists": False, "hash": None})
            else:
                h = file_hash(str(full_path))
                verified_outputs.append({"path": fpath, "exists": True, "hash": h})

    event = f"gate-{result}"

    # 删除旧的 gate 事件（允许 gate-fail 后重新 gate-pass）
    conn.execute(
        "DELETE FROM phase_log WHERE slice_id=? AND phase=? AND event LIKE 'gate-%'",
        (slice_id, phase),
    )

    conn.execute(
        "INSERT INTO phase_log (slice_id, phase, event, outputs, gate_detail, session_hash) VALUES (?, ?, ?, ?, ?, ?)",
        (
            slice_id,
            phase,
            event,
            json.dumps(verified_outputs, ensure_ascii=False) if verified_outputs else None,
            detail_json,
            session_hash,
        ),
    )
    conn.commit()
    conn.close()

    missing = [o for o in verified_outputs if not o["exists"]]
    resp = {"status": "ok", "slice": slice_id, "phase": phase, "event": event}
    if missing:
        resp["warning"] = f"{len(missing)} output file(s) not found on disk"
        resp["missing"] = [o["path"] for o in missing]
    print(json.dumps(resp, ensure_ascii=False))


# ── reconcile 命令 ────────────────────────────────────────

def cmd_reconcile(root: str, slice_id: str):
    root_path = Path(root).resolve()
    conn = get_db(str(root_path))

    chain = []
    complete = True

    for phase in PHASES:
        entered = has_event(conn, slice_id, phase, "enter")
        gate_passed = has_event(conn, slice_id, phase, "gate-pass")
        gate_failed = has_event(conn, slice_id, phase, "gate-fail")

        status = "ok" if entered and gate_passed else "missing"
        if gate_failed and not gate_passed:
            status = "failed"
        elif not entered:
            status = "not-entered"

        chain.append({
            "phase": phase,
            "entered": entered,
            "gate_passed": gate_passed,
            "gate_failed": gate_failed,
            "status": status,
        })
        if status != "ok":
            complete = False

    conn.close()

    # 找到第一个断点
    first_gap = None
    for c in chain:
        if c["status"] != "ok":
            first_gap = c["phase"]
            break

    print(json.dumps({
        "status": "ok",
        "slice": slice_id,
        "complete": complete,
        "chain": chain,
        "first_gap": first_gap,
    }, ensure_ascii=False))


# ── status 命令 ───────────────────────────────────────────

def cmd_status(root: str, slice_id: str | None = None):
    root_path = Path(root).resolve()
    conn = get_db(str(root_path))

    if slice_id:
        # 单个 slice 的状态
        rows = conn.execute(
            "SELECT phase, event, created_at FROM phase_log WHERE slice_id=? ORDER BY created_at",
            (slice_id,),
        ).fetchall()

        current_phase = None
        for phase in PHASES:
            if has_event(conn, slice_id, phase, "enter"):
                current_phase = phase
                if has_event(conn, slice_id, phase, "gate-pass"):
                    continue
                else:
                    break

        events = [{"phase": r["phase"], "event": r["event"], "at": r["created_at"]} for r in rows]
        conn.close()
        print(json.dumps({
            "status": "ok",
            "slice": slice_id,
            "current_phase": current_phase,
            "events": events,
        }, ensure_ascii=False))
    else:
        # 所有 slice 的状态
        slices = conn.execute(
            "SELECT DISTINCT slice_id FROM phase_log ORDER BY slice_id"
        ).fetchall()

        result = []
        for s in slices:
            sid = s["slice_id"]
            current = None
            for phase in PHASES:
                if has_event(conn, sid, phase, "enter"):
                    current = phase
                    if has_event(conn, sid, phase, "gate-pass"):
                        continue
                    else:
                        break
            gate_pass_count = conn.execute(
                "SELECT COUNT(*) as c FROM phase_log WHERE slice_id=? AND event='gate-pass'",
                (sid,),
            ).fetchone()["c"]
            result.append({
                "slice": sid,
                "current_phase": current,
                "gates_passed": gate_pass_count,
                "complete": gate_pass_count == len(PHASES),
            })

        conn.close()
        print(json.dumps({"status": "ok", "slices": result}, ensure_ascii=False))


# ── CLI 入口 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Phase Chain Guard — 阶段链守卫")
    sub = parser.add_subparsers(dest="command", required=True)

    # enter
    p_enter = sub.add_parser("enter", help="进入阶段（检查前置条件）")
    p_enter.add_argument("--root", required=True, help="项目根目录")
    p_enter.add_argument("--slice", required=True, help="Slice ID (如 S1)")
    p_enter.add_argument("--phase", required=True, choices=PHASES, help="目标阶段")
    p_enter.add_argument("--session", default=None, help="会话标识（可选）")

    # gate
    p_gate = sub.add_parser("gate", help="记录阶段卡点结果")
    p_gate.add_argument("--root", required=True)
    p_gate.add_argument("--slice", required=True)
    p_gate.add_argument("--phase", required=True, choices=PHASES)
    p_gate.add_argument("--result", required=True, choices=["pass", "fail"])
    p_gate.add_argument("--outputs", default=None, help='产出文件 JSON: [{"path":"..."}]')
    p_gate.add_argument("--detail", default=None, help="Gate 检查详情 JSON")
    p_gate.add_argument("--session", default=None)

    # reconcile
    p_rec = sub.add_parser("reconcile", help="验证完整阶段链")
    p_rec.add_argument("--root", required=True)
    p_rec.add_argument("--slice", required=True)

    # status
    p_status = sub.add_parser("status", help="查询阶段状态")
    p_status.add_argument("--root", required=True)
    p_status.add_argument("--slice", default=None, help="指定 Slice（不指定则查全部）")

    args = parser.parse_args()

    if args.command == "enter":
        cmd_enter(args.root, args.slice, args.phase, getattr(args, "session", None))
    elif args.command == "gate":
        cmd_gate(args.root, args.slice, args.phase, args.result,
                 getattr(args, "outputs", None), getattr(args, "detail", None),
                 getattr(args, "session", None))
    elif args.command == "reconcile":
        cmd_reconcile(args.root, args.slice)
    elif args.command == "status":
        cmd_status(args.root, getattr(args, "slice", None))


if __name__ == "__main__":
    main()
