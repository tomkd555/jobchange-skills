#!/usr/bin/env python3
"""axis.json の節ごとの到達段階（missing / skeleton / deep）を報告する。

節の一覧と判定条件の原本は references/sections.md にある。合否の判定は hub の
validate_axis.py が担い、本スクリプトは節ごとの段階を報告するだけである。
軸を内包する schema_version 1.x/2.0 の profile.json も同じように読める。
終了コードは 0。読み込めない場合と、職歴だけを持つ 3.0 の profile.json を渡された場合は 1。
--json で構造化出力する。

使い方:
    python axis_sections.py <axis.json>
    python axis_sections.py <axis.json> --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Callable

# 条件と作業特性の語彙は hub の validate_profile.py と共有する（二重管理しない）。
_HUB_SCRIPTS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "job-change-support",
    "scripts",
)
sys.path.insert(0, _HUB_SCRIPTS)

import validate_profile as vp  # noqa: E402

_STATES = ("missing", "skeleton", "deep")


def _is_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _is_num(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def _axis(document: dict) -> dict:
    axis = document.get("job_change_axis")
    return axis if isinstance(axis, dict) else {}


def _is_v2(document: dict) -> bool:
    return vp.schema_version_of(document) == vp._V2_SCHEMA_VERSION


# --- 節ごとの判定 -------------------------------------------------------------


def _reasons_skeleton(d: dict) -> bool:
    reasons = _axis(d).get("reasons")
    return isinstance(reasons, list) and any(_is_str(r) for r in reasons)


def _conditions_skeleton(d: dict) -> bool:
    axis = _axis(d)
    if _is_v2(d):
        conditions = axis.get("conditions")
        return isinstance(conditions, list) and any(isinstance(c, dict) for c in conditions)
    return _nonempty_list(axis.get("must_conditions")) or _nonempty_list(
        axis.get("want_conditions")
    )


def _conditions_deep(d: dict) -> bool:
    if not _is_v2(d):
        return False
    must = vp._must_conditions(_axis(d))
    return bool(must) and all(
        isinstance(c.get("priority"), int) and not isinstance(c.get("priority"), bool)
        for c in must
    )


def _work_character_skeleton(d: dict) -> bool:
    preferences = _axis(d).get("work_character_preferences")
    if not isinstance(preferences, list):
        return False
    traits = [x.get("trait") for x in preferences if isinstance(x, dict)]
    return len(traits) == len(vp._WORK_CHARACTER_TRAITS) and set(traits) == set(
        vp._WORK_CHARACTER_TRAITS
    )


def _score_axes_skeleton(d: dict) -> bool:
    return _nonempty_list(d.get("company_score_axes"))


def _targets_skeleton(d: dict) -> bool:
    targets = d.get("targets")
    if not isinstance(targets, dict):
        return False
    return any(_nonempty_list(targets.get(c)) for c in ("industries", "roles", "companies"))


def _salary_skeleton(d: dict) -> bool:
    salary = d.get("salary")
    return isinstance(salary, dict) and _is_num(salary.get("desired"))


def _salary_deep(d: dict) -> bool:
    return _is_num(d.get("salary", {}).get("current"))


def _same(_: dict) -> bool:
    """deep の条件が skeleton と同じ節に使う。"""
    return True


# (id, initial, needed_by, skeleton, deep)。順序は references/sections.md の表と同じ。
_Check = Callable[[dict], bool]
SECTIONS: list[tuple[str, bool, list[str], _Check, _Check]] = [
    (
        "reasons",
        True,
        ["job-change-documents", "job-change-interview-prep", "job-change-self-analysis"],
        _reasons_skeleton,
        _same,
    ),
    (
        "conditions",
        True,
        ["job-change-job-search", "job-change-fit-assessment"],
        _conditions_skeleton,
        _conditions_deep,
    ),
    (
        "work_character",
        True,
        ["job-change-job-search", "job-change-fit-assessment"],
        _work_character_skeleton,
        _same,
    ),
    (
        "score_axes",
        False,
        ["job-change-fit-assessment", "job-change-company-research"],
        _score_axes_skeleton,
        _same,
    ),
    (
        "targets",
        False,
        ["job-change-company-research", "job-change-job-search"],
        _targets_skeleton,
        _same,
    ),
    ("salary", False, ["job-change-fit-assessment"], _salary_skeleton, _salary_deep),
]

SECTION_IDS = [s[0] for s in SECTIONS]
INITIAL_SECTION_IDS = [s[0] for s in SECTIONS if s[1]]


def section_state(document: Any, section_id: str) -> str:
    """節1つの到達段階を返す。"""
    if not isinstance(document, dict):
        return "missing"
    for sid, _initial, _needed, skeleton, deep in SECTIONS:
        if sid != section_id:
            continue
        if not skeleton(document):
            return "missing"
        return "deep" if deep(document) else "skeleton"
    raise KeyError(section_id)


def report(document: Any) -> dict:
    sections = [
        {
            "id": sid,
            "state": section_state(document, sid),
            "initial": initial,
            "needed_by": needed,
        }
        for sid, initial, needed, _s, _d in SECTIONS
    ]
    initial_complete = all(
        s["state"] in ("skeleton", "deep") for s in sections if s["initial"]
    )
    return {"sections": sections, "initial_complete": initial_complete}


def format_report(result: dict) -> str:
    lines = ["節の到達段階"]
    for s in result["sections"]:
        mark = "初回" if s["initial"] else "  "
        lines.append(f"{s['id']:<15}{s['state']:<10}{mark}  {', '.join(s['needed_by'])}")
    lines.append(
        "初回の範囲: " + ("そろっている" if result["initial_complete"] else "未完")
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="axis.json の節ごとの到達段階を報告する")
    parser.add_argument("axis_path", help="axis.json（または 1.x/2.0 の profile.json）のパス")
    parser.add_argument("--json", action="store_true", help="結果を JSON 形式で出力する")
    args = parser.parse_args(argv)

    try:
        document = vp.load_profile(args.axis_path)
    except (OSError, ValueError) as exc:
        print(f"JSON として読み込めない（{exc}）")
        return 1
    if isinstance(document, dict) and document.get("schema_version") == vp._V3_SCHEMA_VERSION:
        print("schema_version 3.0 は職歴だけを持つ profile.json の版である。axis.json を指定する")
        return 1

    result = report(document)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
