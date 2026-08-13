"""job-change-support: 企業スラッグ一覧（company_index.json）の決定的（非LLM）検証ツール。

標準ライブラリのみで、転職支援スキル群が企業名とスラッグの対応を単一の原本として持つ
company_index.json を機械検査する。各サブスキル（企業研究・応募書類・面接対策・試験対策）が
同じ企業を常に同じスラッグへ解決できるかを、ERROR（一覧として成立しない欠落・衝突）と
WARN（成立するが情報が不足する点）に分けて報告する。仕様の原本は
references/company-index-format.md である。

CLI:
    python validate_company_index.py <company_index.json> [--json]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any

SLUG_PATTERN = re.compile(
    r"^([A-Z]_)?"
    r"[0-9A-Za-z぀-ヿ㐀-鿿＀-￯]"
    r"[0-9A-Za-z぀-ヿ㐀-鿿＀-￯-]*$"
)
_VALID_STATUSES = ("active", "closed")
_SCORE_MIN = 0
_SCORE_MAX = 100


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


def _validate_entry(slug: str, entry: dict, result: ValidationResult) -> None:
    path = f"companies.{slug}"
    if not _is_nonempty_str(entry.get("name")):
        result.add_error(f"{path}.name", "name は必須（非空）である")

    aliases = entry.get("aliases")
    if not isinstance(aliases, list):
        result.add_error(f"{path}.aliases", "aliases は配列でなければならない")
    else:
        if any(not isinstance(a, str) for a in aliases):
            result.add_error(f"{path}.aliases", "aliases は文字列のみを含まなければならない")
        str_aliases = [a for a in aliases if isinstance(a, str)]
        if len(set(str_aliases)) != len(str_aliases):
            result.add_warning(f"{path}.aliases", "同一エントリ内で aliases が重複している")
        name = entry.get("name")
        if _is_nonempty_str(name) and name in str_aliases:
            result.add_warning(f"{path}.aliases", "name と同一の alias が含まれている")

    if not _is_nonempty_str(entry.get("created")):
        result.add_warning(f"{path}.created", "created が未設定である")

    if "status" in entry:
        status = entry.get("status")
        if not isinstance(status, str) or status not in _VALID_STATUSES:
            result.add_error(
                f"{path}.status",
                f"status は {'/'.join(_VALID_STATUSES)} のいずれかでなければならない",
            )

    if "score" in entry:
        score = entry.get("score")
        if isinstance(score, bool) or not isinstance(score, int) or not _SCORE_MIN <= score <= _SCORE_MAX:
            result.add_error(
                f"{path}.score",
                f"score は{_SCORE_MIN}以上{_SCORE_MAX}以下の整数でなければならない",
            )


def _entry_identifiers(entry: dict) -> set[str]:
    identifiers: set[str] = set()
    name = entry.get("name")
    if _is_nonempty_str(name):
        identifiers.add(name)
    aliases = entry.get("aliases")
    if isinstance(aliases, list):
        for alias in aliases:
            if _is_nonempty_str(alias):
                identifiers.add(alias)
    return identifiers


def _validate_cross_slug_uniqueness(companies: dict, result: ValidationResult) -> None:
    owners: dict[str, set[str]] = {}
    for slug, entry in companies.items():
        if not isinstance(entry, dict):
            continue
        for identifier in _entry_identifiers(entry):
            owners.setdefault(identifier, set()).add(slug)
    for identifier, slugs in sorted(owners.items()):
        if len(slugs) > 1:
            slug_list = "、".join(sorted(slugs))
            result.add_error(
                "companies",
                f"識別子「{identifier}」が複数のスラッグ（{slug_list}）に割り当てられている",
            )


def validate(document: Any) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(document, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result

    if document.get("schema_version") is None:
        result.add_error("schema_version", "schema_version は必須である")

    companies = document.get("companies")
    if not isinstance(companies, dict):
        result.add_error("companies", "companies はオブジェクトが必須である")
        return result

    for slug, entry in companies.items():
        path = f"companies.{slug}"
        if not SLUG_PATTERN.match(slug):
            result.add_error(
                path,
                "スラッグは「任意の接頭辞（大文字1字＋_）＋本体（英数字・ハイフン・日本語文字）」で、"
                "本体の先頭はハイフン不可・空白や記号は不可である",
            )
        if not isinstance(entry, dict):
            result.add_error(path, "各エントリはオブジェクトでなければならない")
            continue
        _validate_entry(slug, entry, result)

    _validate_cross_slug_uniqueness(companies, result)

    return result


def load_index(path: str) -> Any:
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

    parser = argparse.ArgumentParser(description="job-change-support 企業スラッグ一覧検証ツール")
    parser.add_argument("index_path", help="検証対象の company_index.json ファイルパス")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    try:
        document = load_index(args.index_path)
    except (OSError, json.JSONDecodeError) as exc:
        result = ValidationResult()
        result.add_error(args.index_path, f"JSON として読み込めない（{exc}）")
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
