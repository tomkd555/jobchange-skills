"""job-change-posting-check: 求人票の確認記録（posting-check.json）の機械的な（非LLM）検証ツール。

標準ライブラリのみで、1 件の求人票と企業の公開数値を記録した posting-check.json を検査する。
項目の id・型・単位・列挙値は field_catalog.py が読む辞書（field-catalog.md）から取り、
このファイルに定数のコピーを持たない。仕様の原本は references/posting-check-format.md である。

CLI:
    python validate_posting_check.py <posting-check.json> [--json]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from field_catalog import Catalog, check_value_object, is_date, load_catalog  # noqa: E402
from validate_company_index import SLUG_PATTERN, ValidationResult  # noqa: E402

KNOWN_SCHEMA_VERSIONS = ("1.0",)
SOURCE_TYPES = ("url", "text", "scout", "search")
_URL_SOURCE_TYPES = ("url", "search")
_POSTING_ID_RE = re.compile(r"^(?P<slug>.+)-(?P<date>[0-9]{8})-(?P<seq>[0-9]{2})$")

# posting-check.json の節名と辞書の section 名の対応
_CATALOG_SECTION = {"job": "posting", "company": "company"}

# 仕様の「Always write」の一覧。ここに無い項目は書かなくてよい。
ALWAYS_WRITE_JOB = (
    "company_name", "job_title", "industry", "employment_type", "work_location", "remote_policy",
    "salary_min", "salary_max", "salary_basis", "fixed_overtime_included", "fixed_overtime_hours",
    "scheduled_hours", "annual_holidays", "monthly_overtime_h", "paid_leave_rate",
    "scope_of_change_duties", "scope_of_change_location", "contract_renewal_cap",
    "requirements_must", "requirements_want", "selection_process", "posted_at",
)
ALWAYS_WRITE_COMPANY = (
    "legal_entity_name", "employee_count", "avg_age", "avg_tenure_years", "avg_annual_salary",
    "revenue_growth", "operating_margin", "equity_ratio", "labor_violation_listed",
    "labor_violation_date",
)
# 値が null だと法定記載事項の欠落を示す項目
LEGAL_JOB_FIELDS = ("scope_of_change_duties", "scope_of_change_location", "posted_at")


def parse_posting_id(posting_id: Any) -> tuple[str, str, str] | None:
    """求人 ID を (スラッグ, YYYYMMDD, 連番) に分ける。形式に合わなければ None。"""
    if not isinstance(posting_id, str):
        return None
    m = _POSTING_ID_RE.match(posting_id)
    if not m or not SLUG_PATTERN.match(m.group("slug")):
        return None
    return m.group("slug"), m.group("date"), m.group("seq")


def _check_entries(section: str, document: dict, catalog: Catalog, result: ValidationResult) -> None:
    body = document.get(section)
    if not isinstance(body, dict):
        result.add_error(section, f"{section} はオブジェクトで必須である")
        return
    for field_id, entry in body.items():
        path = f"{section}.{field_id}"
        field_ = catalog.fields.get(field_id)
        if field_ is None:
            result.add_error(path, "辞書に無い項目である")
            continue
        if field_.section != _CATALOG_SECTION[section]:
            result.add_error(path, f"{field_id} は {field_.section} の項目であり、{section} には書けない")
            continue
        if isinstance(entry, list):
            if section == "job":
                result.add_error(path, "job の値は配列にせず、オブジェクト 1 つで書く")
                continue
            entries = entry
        else:
            entries = [entry]
        for i, obj in enumerate(entries):
            where = f"{path}[{i}]" if isinstance(entry, list) else path
            for msg in check_value_object(field_, obj, catalog):
                result.add_error(where, msg)
            if not isinstance(obj, dict) or obj.get("value") is None:
                continue
            grade = obj.get("grade")
            if grade in catalog.enums.get("grade", {}) and grade != "A":
                result.add_warning(where, f"grade が {grade} である（確認は公式の出典に限るので A で書く）")
    required = ALWAYS_WRITE_JOB if section == "job" else ALWAYS_WRITE_COMPANY
    for field_id in required:
        if field_id not in body:
            result.add_warning(f"{section}.{field_id}", "必ず書く項目が無い（見つからなければ value を null にして書く）")


def _value_of(entry: Any) -> Any:
    return entry.get("value") if isinstance(entry, dict) else None


def validate(document: Any, catalog: Catalog | None = None) -> ValidationResult:
    result = ValidationResult()
    if not isinstance(document, dict):
        result.add_error("$", "ルートはオブジェクトでなければならない")
        return result
    catalog = catalog or load_catalog()

    version = document.get("schema_version")
    if not isinstance(version, str):
        result.add_error("schema_version", "schema_version は文字列で必須である")
    elif version not in KNOWN_SCHEMA_VERSIONS:
        result.add_warning("schema_version", f"未知の schema_version である: {version}")

    fetched_at = document.get("fetched_at")
    if not is_date(fetched_at):
        result.add_error("fetched_at", "fetched_at は YYYY-MM-DD の実在する日付で必須である")

    parts = parse_posting_id(document.get("posting_id"))
    if parts is None:
        result.add_error("posting_id", "posting_id は {企業スラッグ}-{YYYYMMDD}-{NN} の形で書く")
    else:
        slug, ymd, _ = parts
        if document.get("company_slug") != slug:
            result.add_error("company_slug", "company_slug は posting_id のスラッグ部分と一致させる")
        if is_date(fetched_at) and fetched_at.replace("-", "") != ymd:
            result.add_error("posting_id", "posting_id の日付部分は fetched_at と一致させる")
    if not isinstance(document.get("company_slug"), str):
        result.add_error("company_slug", "company_slug は文字列で必須である")

    source_type = document.get("source_type")
    source_url = document.get("source_url")
    if source_type not in SOURCE_TYPES:
        result.add_error("source_type", f"source_type は {', '.join(SOURCE_TYPES)} のいずれかで書く")
    elif source_type in _URL_SOURCE_TYPES and not (isinstance(source_url, str) and source_url.startswith("http")):
        result.add_error("source_url", f"source_type が {source_type} のとき、source_url は http で始まる URL で必須である")
    if source_url is not None and not isinstance(source_url, str):
        result.add_error("source_url", "source_url は文字列か null で書く")

    _check_entries("job", document, catalog, result)
    _check_entries("company", document, catalog, result)

    job = document.get("job") if isinstance(document.get("job"), dict) else {}
    for field_id in LEGAL_JOB_FIELDS:
        if isinstance(job.get(field_id), dict) and job[field_id].get("value") is None:
            result.add_warning(f"job.{field_id}", "求人票に法定の記載事項が無い（要確認として示す）")
    if _value_of(job.get("employment_type")) in ("contract", "temporary") \
            and isinstance(job.get("contract_renewal_cap"), dict) and _value_of(job["contract_renewal_cap"]) is None:
        result.add_warning("job.contract_renewal_cap", "有期の雇用形態なのに更新上限の記載が無い（要確認として示す）")

    questions = document.get("open_questions")
    if not isinstance(questions, list):
        result.add_error("open_questions", "open_questions は配列で必須である")
    elif any(not isinstance(q, str) for q in questions):
        result.add_error("open_questions", "open_questions は文字列のみを含まなければならない")
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
    parser = argparse.ArgumentParser(description="posting-check.json を検証する")
    parser.add_argument("path")
    parser.add_argument("--json", action="store_true", help="結果を JSON で出力する")
    args = parser.parse_args(argv)
    try:
        document = load_json(args.path)
    except (OSError, json.JSONDecodeError) as e:
        result = ValidationResult()
        result.add_error("$", f"JSON として読めない: {e}")
    else:
        result = validate(document)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(result, args.path))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
