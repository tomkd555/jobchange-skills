"""job-change-support: 条件シート（wishes.json）の機械的な（非LLM）検証ツール。

標準ライブラリのみで、利用者の条件シート wishes.json を検査する。項目 id・型・単位・列挙値は
field_catalog.py を通して references/field-catalog.md から読み、このファイルに定数を持たない。
仕様の原本は references/wishes-format.md である。

CLI:
    python validate_wishes.py <wishes.json> [--json]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from field_catalog import Catalog, is_date, load_catalog  # noqa: E402

CONDITION_ID_PATTERN = re.compile(r"^c[0-9]{3}$")
DECISION_ID_PATTERN = re.compile(r"^[0-9]{8}-[0-9a-z][0-9a-z-]*$")
KNOWN_SCHEMA_VERSIONS = ("1.0",)
REQUIRED_CONDITION_KEYS = ("id", "kind", "field_id", "text", "level", "source", "created", "updated", "active")
REQUIRED_HISTORY_KEYS = ("date", "condition_id", "field", "before", "after", "reason")
# 求人検索が必須として記録する 2 種類の kind。
EXPECTED_ACTIVE_KINDS = ("salary_min", "remote")


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, path: str, message: str) -> None:
        self.errors.append(f"[ERROR] {path}: {message}")

    def add_warning(self, path: str, message: str) -> None:
        self.warnings.append(f"[WARN] {path}: {message}")

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {
            "status": "PASS" if self.ok else "FAIL",
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }


def _is_nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _check_condition_value(cond: dict, path: str, catalog: Catalog, result: ValidationResult) -> None:
    field_id = cond.get("field_id")
    operator = cond.get("operator")
    value = cond.get("value")
    spec = catalog.fields.get(field_id) if isinstance(field_id, str) else None

    if operator is not None and operator not in catalog.enums.get("operator", {}):
        result.add_error(f"{path}.operator", f"operator は {', '.join(catalog.enums.get('operator', {}))} か null で書く")
    if value is not None and operator is None:
        result.add_error(f"{path}.operator", "value があるのに operator が null である")
    if value is None and operator is not None:
        result.add_error(f"{path}.value", "operator があるのに value が null である")

    if spec is None:
        return
    if value is not None:
        # in 演算子の許容集合は配列で書く。string_list 型でない項目では要素ごとに型を見る。
        per_item = isinstance(value, list) and spec.type != "string_list"
        for item in value if per_item else [value]:
            message = spec.check_value(item, catalog)
            if message:
                result.add_error(f"{path}.value", message)
                break
        if per_item and not value:
            result.add_error(f"{path}.value", "許容集合の配列が空である")
    if cond.get("unit") != spec.unit:
        result.add_error(f"{path}.unit", f"unit は辞書の単位 {spec.unit!r} で書く（{cond.get('unit')!r} になっている）")


def _validate_condition(index: int, cond: Any, seen_ids: set[str], catalog: Catalog, result: ValidationResult) -> None:
    path = f"conditions[{index}]"
    if not isinstance(cond, dict):
        result.add_error(path, "条件はオブジェクトで書く")
        return
    for key in REQUIRED_CONDITION_KEYS:
        if key not in cond:
            result.add_error(f"{path}.{key}", f"{key} は必須である")

    cid = cond.get("id")
    if "id" in cond:
        if not isinstance(cid, str) or not CONDITION_ID_PATTERN.match(cid):
            result.add_error(f"{path}.id", "id は c と 3 桁の数字で書く（例 c001）")
        elif cid in seen_ids:
            result.add_error(f"{path}.id", f"id {cid} が重複している")
        else:
            seen_ids.add(cid)

    for key, enum_name in (("kind", "condition_kind"), ("level", "level")):
        if key in cond and cond[key] not in catalog.enums.get(enum_name, {}):
            result.add_error(f"{path}.{key}", f"{key} は {', '.join(catalog.enums.get(enum_name, {}))} のいずれかで書く")

    field_id = cond.get("field_id")
    if "field_id" in cond and (not isinstance(field_id, str) or field_id not in catalog.fields):
        result.add_error(f"{path}.field_id", f"field_id {field_id!r} が辞書にない")

    for key in ("text", "source"):
        if key in cond and not _is_nonempty_str(cond[key]):
            result.add_error(f"{path}.{key}", f"{key} は空でない文字列で書く")

    _check_condition_value(cond, path, catalog, result)

    if field_id == "custom" and not _is_nonempty_str(cond.get("how_to_judge")):
        result.add_error(f"{path}.how_to_judge", "field_id が custom の条件は how_to_judge を空にできない")

    if "active" in cond and not isinstance(cond["active"], bool):
        result.add_error(f"{path}.active", "active は真偽値で書く")

    created, updated = cond.get("created"), cond.get("updated")
    for key, val in (("created", created), ("updated", updated)):
        if key in cond and not is_date(val):
            result.add_error(f"{path}.{key}", f"{key} は YYYY-MM-DD の実在する日付で書く")
    if is_date(created) and is_date(updated) and updated < created:
        result.add_error(f"{path}.updated", "updated が created より前である")


def _validate_history(index: int, entry: Any, condition_ids: set[str], result: ValidationResult) -> None:
    path = f"history[{index}]"
    if not isinstance(entry, dict):
        result.add_error(path, "履歴の要素はオブジェクトで書く")
        return
    for key in REQUIRED_HISTORY_KEYS:
        if key not in entry:
            result.add_error(f"{path}.{key}", f"{key} は必須である")
    if "date" in entry and not is_date(entry["date"]):
        result.add_error(f"{path}.date", "date は YYYY-MM-DD の実在する日付で書く")
    if "condition_id" in entry and entry["condition_id"] not in condition_ids:
        result.add_error(f"{path}.condition_id", f"condition_id {entry['condition_id']!r} が conditions にない")
    if "field" in entry and not _is_nonempty_str(entry["field"]):
        result.add_error(f"{path}.field", "field は空でない文字列で書く")
    if "reason" in entry and not _is_nonempty_str(entry["reason"]):
        result.add_error(f"{path}.reason", "reason は空にできない")


def validate(document: Any, catalog: Catalog | None = None) -> ValidationResult:
    result = ValidationResult()
    catalog = catalog or load_catalog()

    if not isinstance(document, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result

    version = document.get("schema_version")
    if not isinstance(version, str):
        result.add_error("schema_version", "schema_version は文字列で必須である")
    elif version not in KNOWN_SCHEMA_VERSIONS:
        result.add_warning("schema_version", f"schema_version が既知のバージョン（{'/'.join(KNOWN_SCHEMA_VERSIONS)}）ではない（実値: {version!r}）")

    if not is_date(document.get("updated")):
        result.add_error("updated", "updated は YYYY-MM-DD の実在する日付で必須である")

    conditions = document.get("conditions")
    history = document.get("history")
    used_in = document.get("used_in")
    for key, val in (("conditions", conditions), ("history", history), ("used_in", used_in)):
        if not isinstance(val, list):
            result.add_error(key, f"{key} は配列で必須である")

    condition_ids: set[str] = set()
    if isinstance(conditions, list):
        if not conditions:
            result.add_warning("conditions", "conditions が空である")
        for i, cond in enumerate(conditions):
            _validate_condition(i, cond, condition_ids, catalog, result)
            if isinstance(cond, dict) and cond.get("level") == "must" and cond.get("active") is False:
                result.add_warning(f"conditions[{i}].active", f"必須条件 {cond.get('id')} が無効になっている（誤って外していないか確認する）")
        active_kinds = {c.get("kind") for c in conditions if isinstance(c, dict) and c.get("active") is True}
        for kind in EXPECTED_ACTIVE_KINDS:
            if kind not in active_kinds:
                result.add_warning("conditions", f"有効な条件に kind {kind} がない（求人検索は必須として記録する）")

    if isinstance(history, list):
        for i, entry in enumerate(history):
            _validate_history(i, entry, condition_ids, result)

    if isinstance(used_in, list):
        for i, item in enumerate(used_in):
            if not isinstance(item, str) or not DECISION_ID_PATTERN.match(item):
                result.add_error(f"used_in[{i}]", "意思決定 id は {YYYYMMDD}-{小文字・数字・ハイフンの語} で書く")

    return result


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def format_report(result: ValidationResult) -> str:
    status = "PASS" if result.ok else "FAIL"
    lines = [f"検証結果: {status}（ERROR {len(result.errors)}件 / WARN {len(result.warnings)}件）"]
    lines.extend(result.errors)
    lines.extend(result.warnings)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="job-change-support 条件シート検証ツール")
    parser.add_argument("wishes_path", help="検証対象の wishes.json ファイルパス")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    try:
        document = load_json(args.wishes_path)
    except (OSError, ValueError) as exc:
        result = ValidationResult()
        result.add_error(args.wishes_path, f"JSON として読み込めない（{exc}）")
    else:
        result = validate(document)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
