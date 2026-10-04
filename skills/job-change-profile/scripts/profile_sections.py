#!/usr/bin/env python3
"""profile.json の節ごとの到達段階（missing / skeleton / deep）を報告する。

profile.json は職歴の事実（基本情報・職歴・実績・スキル）を持つ。転職の軸の節は
job-change-axis の axis_sections.py が報告する。
節の一覧と判定条件の原本は references/sections.md にある。合否の判定は hub の
validate_profile.py が担い、本スクリプトは節ごとの段階を報告するだけである。
終了コードは常に 0（読み込めない場合だけ 1）。--json で構造化出力する。

使い方:
    python profile_sections.py <profile.json>
    python profile_sections.py <profile.json> --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Callable

# period の解析は hub の validate_profile.py と共有する（二重管理しない）。
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


def _entries(profile: dict) -> list[dict]:
    career = profile.get("career_history")
    if not isinstance(career, list):
        return []
    return [e for e in career if isinstance(e, dict)]


def _complete(entry: dict) -> bool:
    return all(_is_str(entry.get(k)) for k in ("company", "period", "role"))


# --- 節ごとの判定 -------------------------------------------------------------


def _basic_skeleton(p: dict) -> bool:
    basic = p.get("basic")
    return isinstance(basic, dict) and _is_str(basic.get("current_role"))


def _basic_deep(p: dict) -> bool:
    basic = p.get("basic", {})
    return (
        _is_num(basic.get("years_of_experience"))
        and _is_str(basic.get("location"))
        and _nonempty_list(basic.get("education"))
    )


def _career_skeleton(p: dict) -> bool:
    return any(_complete(e) for e in _entries(p))


def _career_deep(p: dict) -> bool:
    entries = _entries(p)
    return bool(entries) and all(
        _complete(e) and vp._parse_period(e.get("period")) is not None for e in entries
    )


def _achievements_skeleton(p: dict) -> bool:
    return any(
        _nonempty_list(e.get("responsibilities")) or _nonempty_list(e.get("achievements"))
        for e in _entries(p)
    )


def _achievements_deep(p: dict) -> bool:
    entries = _entries(p)
    if not entries or not all(_nonempty_list(e.get("responsibilities")) for e in entries):
        return False
    return any(
        isinstance(a, dict) and _is_str(a.get("metric"))
        for e in entries
        for a in (e.get("achievements") or [])
    )


def _skills_skeleton(p: dict) -> bool:
    skills = p.get("skills")
    if not isinstance(skills, dict):
        return False
    return any(
        _nonempty_list(skills.get(c))
        for c in ("technical", "business", "languages", "certifications", "portable")
    )


def _skills_deep(p: dict) -> bool:
    skills = p.get("skills", {})
    return (
        _nonempty_list(skills.get("technical")) or _nonempty_list(skills.get("business"))
    ) and _nonempty_list(skills.get("portable"))


# (id, initial, needed_by, skeleton, deep)。順序は references/sections.md の表と同じ。
_Check = Callable[[dict], bool]
SECTIONS: list[tuple[str, bool, list[str], _Check, _Check]] = [
    ("basic", True, ["job-change-documents"], _basic_skeleton, _basic_deep),
    ("career", True, ["*"], _career_skeleton, _career_deep),
    (
        "achievements",
        False,
        ["job-change-documents", "job-change-self-analysis"],
        _achievements_skeleton,
        _achievements_deep,
    ),
    (
        "skills",
        False,
        ["job-change-documents", "job-change-fit-assessment"],
        _skills_skeleton,
        _skills_deep,
    ),
]

SECTION_IDS = [s[0] for s in SECTIONS]
INITIAL_SECTION_IDS = [s[0] for s in SECTIONS if s[1]]


def section_state(profile: Any, section_id: str) -> str:
    """節1つの到達段階を返す。"""
    if not isinstance(profile, dict):
        return "missing"
    for sid, _initial, _needed, skeleton, deep in SECTIONS:
        if sid != section_id:
            continue
        if not skeleton(profile):
            return "missing"
        return "deep" if deep(profile) else "skeleton"
    raise KeyError(section_id)


def report(profile: Any) -> dict:
    sections = [
        {
            "id": sid,
            "state": section_state(profile, sid),
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

    parser = argparse.ArgumentParser(description="profile.json の節ごとの到達段階を報告する")
    parser.add_argument("profile_path", help="profile.json のパス")
    parser.add_argument("--json", action="store_true", help="結果を JSON 形式で出力する")
    args = parser.parse_args(argv)

    try:
        profile = vp.load_profile(args.profile_path)
    except (OSError, ValueError) as exc:
        print(f"JSON として読み込めない（{exc}）")
        return 1

    result = report(profile)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
