"""job-change-company-research: job_posting.json の決定的（非LLM）検証ツール。

標準ライブラリのみで、求人情報の取込成果物 job_posting.json を機械検査する。
取り込んだ求人票が、必須項目（schema_version・source_type・fetched_at・
company_name・title）を備え、metrics（年間休日・月平均残業・有給取得率・付与日数）を
仕様どおりの型で持つかを、ERROR（成果物として成立しない欠落・型違反）と WARN
（成立するが情報が不足する点）に分けて報告する。仕様の原本は
references/job-posting-format.md である。

CLI:
    python validate_job_posting.py <job_posting.json> [--json]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_KNOWN_SCHEMA_VERSIONS = ("1.0",)
# 取込の入口。url 以外の入口では source_url を必須にしないため、URL の検査は url のときだけ行う。
SOURCE_TYPES = ("url", "text", "file", "dialogue")
# metrics の4キー。各値は {value(number), quote(非空str)} または null。
METRIC_KEYS = (
    "annual_holidays",
    "monthly_overtime_h",
    "paid_leave_rate",
    "paid_leave_days_granted",
)


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


def _is_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float))


def _is_valid_date(value: Any) -> bool:
    """YYYY-MM-DD 形式かつ実在日付であれば True を返す。"""
    if not isinstance(value, str) or not _DATE_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _validate_required(document: dict, result: ValidationResult) -> None:
    """必須スカラー項目（schema_version・source_type・fetched_at・company_name・title）を検査する。

    source_url は source_type が url のときのみ必須である。
    """
    if not _is_nonempty_str(document.get("schema_version")):
        result.add_error("schema_version", "schema_version は必須（非空）である")
    elif document.get("schema_version") not in _KNOWN_SCHEMA_VERSIONS:
        result.add_warning(
            "schema_version",
            f"schema_version が既知のバージョン（{'/'.join(_KNOWN_SCHEMA_VERSIONS)}）ではない",
        )

    source_type = document.get("source_type")
    if not _is_nonempty_str(source_type):
        result.add_error("source_type", "source_type は必須（非空）である")
    elif source_type not in SOURCE_TYPES:
        result.add_error(
            "source_type",
            f"source_type は {'/'.join(SOURCE_TYPES)} のいずれかである（実値: {source_type!r}）",
        )

    if source_type == "url":
        url = document.get("source_url")
        if not isinstance(url, str) or not url.startswith("http"):
            result.add_error(
                "source_url",
                f"source_url は http で始まる文字列でなければならない（実値: {url!r}）",
            )

    fetched_at = document.get("fetched_at")
    if fetched_at is None or (isinstance(fetched_at, str) and fetched_at.strip() == ""):
        result.add_error("fetched_at", "fetched_at は必須（YYYY-MM-DD）である")
    elif not _is_valid_date(fetched_at):
        result.add_error(
            "fetched_at",
            f"fetched_at は YYYY-MM-DD 形式の実在日付でなければならない（実値: {fetched_at!r}）",
        )

    if not _is_nonempty_str(document.get("company_name")):
        result.add_error("company_name", "company_name は必須（非空）である")
    if not _is_nonempty_str(document.get("title")):
        result.add_error("title", "title は必須（非空）である")


def _validate_metrics(document: dict, result: ValidationResult) -> None:
    """metrics を検査する。

    - metrics 欠落は正常（ERROR・WARN いずれも出さない）。
    - metrics が存在してオブジェクトでない場合は ERROR。
    - 各メトリックは {value(number), quote(非空str)} または null。null は正常。
    - 型違反（value 非数値、quote 空、オブジェクトでも null でもない）は ERROR。
    """
    if "metrics" not in document:
        return
    metrics = document.get("metrics")
    if not isinstance(metrics, dict):
        result.add_error("metrics", "metrics はオブジェクトでなければならない")
        return
    for key in METRIC_KEYS:
        if key not in metrics:
            continue
        entry = metrics[key]
        if entry is None:
            continue
        path = f"metrics.{key}"
        if not isinstance(entry, dict):
            result.add_error(path, "{value, quote} のオブジェクトまたは null でなければならない")
            continue
        if not _is_number(entry.get("value")):
            result.add_error(f"{path}.value", "value は数値でなければならない")
        if not _is_nonempty_str(entry.get("quote")):
            result.add_error(f"{path}.quote", "quote は必須（非空。求人票からの引用）である")


def _validate_optional_shapes(document: dict, result: ValidationResult) -> None:
    """任意の構造化フィールドが存在する場合の明白な型違反を ERROR にする。"""
    for key in ("location", "salary", "working_hours", "requirements"):
        if key in document and document[key] is not None and not isinstance(document[key], dict):
            result.add_error(key, f"{key} はオブジェクトでなければならない")

    for key in ("selection_process", "open_questions", "benefits"):
        if key in document and document[key] is not None and not isinstance(document[key], list):
            result.add_error(key, f"{key} は配列でなければならない")

    benefits = document.get("benefits")
    if isinstance(benefits, list):
        for i, item in enumerate(benefits):
            if not isinstance(item, dict):
                result.add_error(f"benefits[{i}]", "benefits の各要素はオブジェクトでなければならない")
                continue
            if not _is_nonempty_str(item.get("name")):
                result.add_error(f"benefits[{i}].name", "name は必須（非空）である")


def validate(document: Any) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(document, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result

    _validate_required(document, result)
    _validate_metrics(document, result)
    _validate_optional_shapes(document, result)

    return result


def load_posting(path: str) -> Any:
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

    parser = argparse.ArgumentParser(description="job-change-company-research 求人票取込データ検証ツール")
    parser.add_argument("posting_path", help="検証対象の job_posting.json ファイルパス")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    try:
        document = load_posting(args.posting_path)
    except (OSError, json.JSONDecodeError) as exc:
        result = ValidationResult()
        result.add_error(args.posting_path, f"JSON として読み込めない（{exc}）")
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(format_report(result))
        return 1

    result = validate(document)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(result))

    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
