"""job-change-company-research: job_posting.json の機械的な（非LLM）検証ツール。

標準ライブラリのみで、求人情報の取込成果物 job_posting.json を機械的に検査する。
取り込んだ求人票が、必須項目（schema_version・source_type・fetched_at・
company_name・title）を備え、metrics（年間休日・月平均残業・有給取得率・付与日数）と
scope_of_change（2024年4月から明示が義務づけられた3項目）を仕様どおりの型で持つかを、
ERROR（成果物として成立しない欠落・型違反）と WARN（成立するが情報が不足する点）に
分けて報告する。仕様の原本は references/job-posting-format.md である。

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
_KNOWN_SCHEMA_VERSIONS = ("1.0", "1.1")
# scope_of_change が無いのは 1.0 だけである。1.0 を除外する形で書き、後続バージョンを
# 加えたときに検査が黙って外れないようにする。
_SCOPE_EXEMPT_SCHEMA_VERSIONS = ("1.0",)
# 取込の入口。url 以外の入口では source_url を必須にしないため、URL の検査は url のときだけ行う。
SOURCE_TYPES = ("url", "text", "file", "dialogue")
# metrics の4キー。各値は {value(number), quote(非空str)} または null。
METRIC_KEYS = (
    "annual_holidays",
    "monthly_overtime_h",
    "paid_leave_rate",
    "paid_leave_days_granted",
)
# scope_of_change の3キー。2024年4月から求人票への明示が義務づけられた項目に対応する。
SCOPE_KEYS = ("duties", "work_location", "contract_renewal_cap")


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


def _validate_scope_of_change(document: dict, result: ValidationResult) -> None:
    """scope_of_change を検査する。

    - schema_version が 1.0 の場合は検査しない（1.0 にはこのフィールドが無い）。それ以外の
      バージョンでは検査する。
    - 各値は {stated(bool), unlimited(bool), quote(str)} または null。null は求人票に記載が
      無かったことを表す。
    - stated が真のときは quote を非空とする（記載があるなら引用を写せるため）。
    - 3項目とも null（またはフィールド自体が無い）場合は WARN。2024年4月以降の求人票には
      明示義務があり、3項目すべてが未取得であることは取込の不足を疑わせる。
    """
    if document.get("schema_version") in _SCOPE_EXEMPT_SCHEMA_VERSIONS:
        return

    scope = document.get("scope_of_change")
    if scope is None:
        result.add_warning(
            "scope_of_change",
            "業務・就業場所の変更の範囲と有期契約の更新上限が1件も記録されていない"
            "（2024年4月以降の求人票では明示義務がある）",
        )
        return
    if not isinstance(scope, dict):
        result.add_error("scope_of_change", "scope_of_change はオブジェクトでなければならない")
        return

    filled = 0
    for key in SCOPE_KEYS:
        entry = scope.get(key)
        if entry is None:
            continue
        filled += 1
        path = f"scope_of_change.{key}"
        if not isinstance(entry, dict):
            result.add_error(
                path, "{stated, unlimited, quote} のオブジェクトまたは null でなければならない"
            )
            continue
        stated = entry.get("stated")
        if not isinstance(stated, bool):
            result.add_error(f"{path}.stated", "stated は真偽値でなければならない")
        if not isinstance(entry.get("unlimited"), bool):
            result.add_error(f"{path}.unlimited", "unlimited は真偽値でなければならない")
        quote = entry.get("quote")
        if stated is True:
            if not _is_nonempty_str(quote):
                result.add_error(
                    f"{path}.quote", "stated が真のとき quote は必須（非空。求人票からの引用）である"
                )
        elif quote is not None and not isinstance(quote, str):
            result.add_error(f"{path}.quote", "quote は文字列でなければならない")

    if filled == 0:
        result.add_warning(
            "scope_of_change",
            "業務・就業場所の変更の範囲と有期契約の更新上限が1件も記録されていない"
            "（2024年4月以降の求人票では明示義務がある）",
        )


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
    _validate_scope_of_change(document, result)
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
