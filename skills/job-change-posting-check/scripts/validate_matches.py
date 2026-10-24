"""job-change-posting-check: 条件との照合記録（matches/{求人 ID}.json）の機械的な（非LLM）検証ツール。

標準ライブラリのみで、1 件の求人確認と利用者の条件（wishes.json）の照合記録を検査する。
項目の id と照合結果の列挙値は hub の field_catalog.py が読む辞書から取る。
仕様の原本は references/matches-format.md である。

CLI:
    python validate_matches.py <matches.json> --wishes <wishes.json> [--posting-check <posting-check.json>] [--json]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any

_HUB_SCRIPTS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "job-change-support",
    "scripts",
)
if _HUB_SCRIPTS not in sys.path:
    sys.path.insert(0, _HUB_SCRIPTS)

from field_catalog import Catalog, is_date, load_catalog  # noqa: E402
from validate_company_index import ValidationResult  # noqa: E402

# 同じ階層の validate_posting_check を読む。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_posting_check import parse_posting_id  # noqa: E402

KNOWN_SCHEMA_VERSIONS = ("1.0",)
_CONDITION_ID_RE = re.compile(r"^c[0-9]{3}$")


def _null_only_fields(posting_check: dict) -> set[str]:
    """posting-check の全エントリで value が null の項目 id を返す。"""
    nulls: dict[str, list[bool]] = {}
    for section in ("job", "company"):
        body = posting_check.get(section)
        if not isinstance(body, dict):
            continue
        for field_id, entry in body.items():
            entries = entry if isinstance(entry, list) else [entry]
            nulls.setdefault(field_id, []).extend(
                isinstance(e, dict) and e.get("value") is None for e in entries
            )
    return {fid for fid, flags in nulls.items() if flags and all(flags)}


def validate(
    document: Any, wishes: Any, posting_check: Any = None, catalog: Catalog | None = None
) -> ValidationResult:
    result = ValidationResult()
    if not isinstance(document, dict):
        result.add_error("$", "ルートはオブジェクトでなければならない")
        return result
    catalog = catalog or load_catalog()
    result_values = catalog.enum_values("match_result")

    version = document.get("schema_version")
    if not isinstance(version, str):
        result.add_error("schema_version", "schema_version は文字列で必須である")
    elif version not in KNOWN_SCHEMA_VERSIONS:
        result.add_warning("schema_version", f"未知の schema_version である: {version}")

    if parse_posting_id(document.get("posting_id")) is None:
        result.add_error("posting_id", "posting_id は {企業スラッグ}-{YYYYMMDD}-{NN} の形で書く")
    elif isinstance(posting_check, dict) and posting_check.get("posting_id") != document["posting_id"]:
        result.add_error("posting_id", "posting_id が posting-check.json の posting_id と異なる")

    if not is_date(document.get("checked_at")):
        result.add_error("checked_at", "checked_at は YYYY-MM-DD の実在する日付で必須である")

    conditions: dict[str, dict] = {}
    raw = wishes.get("conditions") if isinstance(wishes, dict) else None
    for c in raw if isinstance(raw, list) else []:
        if isinstance(c, dict) and isinstance(c.get("id"), str):
            conditions[c["id"]] = c

    match = document.get("match")
    seen: set[str] = set()
    if not isinstance(match, list):
        result.add_error("match", "match は配列で必須である")
        match = []
    for i, el in enumerate(match):
        path = f"match[{i}]"
        if not isinstance(el, dict):
            result.add_error(path, "match の要素はオブジェクトで書く")
            continue
        cid = el.get("condition_id")
        if not isinstance(cid, str) or not _CONDITION_ID_RE.match(cid):
            result.add_error(f"{path}.condition_id", "condition_id は c と 3 桁の数字で書く")
        else:
            if cid in seen:
                result.add_error(f"{path}.condition_id", f"condition_id が重複している: {cid}")
            seen.add(cid)
            if cid not in conditions:
                result.add_error(f"{path}.condition_id", f"wishes.json に無い condition_id である: {cid}")
            elif conditions[cid].get("active") is False:
                result.add_warning(f"{path}.condition_id", f"{cid} は無効（active が false）の条件を指している")
        res = el.get("result")
        if res not in result_values:
            result.add_error(f"{path}.result", f"result は {', '.join(result_values)} のいずれかで書く")
        basis = el.get("basis_field_id")
        if res in ("meets", "not_meets") and (basis is None or basis not in catalog.fields):
            result.add_error(f"{path}.basis_field_id", f"result が {res} のとき、basis_field_id は辞書の項目 id で必須である")
        elif basis is not None and basis not in catalog.fields:
            result.add_error(f"{path}.basis_field_id", "basis_field_id が辞書に無い")
        note = el.get("note")
        if not isinstance(note, str) or not note.strip():
            result.add_error(f"{path}.note", "note は空でない文字列で必須である")

    for cid, c in conditions.items():
        if c.get("active") is True and c.get("level") in ("must", "want") and cid not in seen:
            result.add_warning("match", f"有効な {c['level']} 条件 {cid} の照合が無い")

    unknowns = document.get("unknowns")
    if not isinstance(unknowns, list) or any(not isinstance(u, str) for u in unknowns):
        result.add_error("unknowns", "unknowns は文字列の配列で必須である")
        return result
    for u in unknowns:
        if u not in catalog.fields:
            result.add_error("unknowns", f"辞書に無い項目 id である: {u}")
    if isinstance(posting_check, dict):
        expected = _null_only_fields(posting_check)
        for u in unknowns:
            if u in catalog.fields and u not in expected:
                result.add_error("unknowns", f"{u} は posting-check.json に非 null の値があるので unknowns に入れない")
        for u in sorted(expected - set(unknowns)):
            result.add_error("unknowns", f"{u} は posting-check.json で値が全て null なので unknowns に入れる")
    return result


def load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def format_report(result: ValidationResult, path: str) -> str:
    lines = [f"検証対象: {path}"]
    lines += result.errors + result.warnings
    lines.append(f"結果: {'PASS' if result.ok else 'FAIL'}（ERROR {len(result.errors)} 件、WARN {len(result.warnings)} 件）")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="matches/{求人 ID}.json を検証する")
    parser.add_argument("path")
    parser.add_argument("--wishes", required=True, help="条件表 wishes.json")
    parser.add_argument("--posting-check", help="照合元の posting-check.json")
    parser.add_argument("--json", action="store_true", help="結果を JSON で出力する")
    args = parser.parse_args(argv)
    try:
        document = load_json(args.path)
        wishes = load_json(args.wishes)
        posting_check = load_json(args.posting_check) if args.posting_check else None
    except (OSError, json.JSONDecodeError) as e:
        result = ValidationResult()
        result.add_error("$", f"JSON として読めない: {e}")
    else:
        result = validate(document, wishes, posting_check)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(result, args.path))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
