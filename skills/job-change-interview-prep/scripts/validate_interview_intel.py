"""job-change-interview-prep: interview_intel.json の機械的な（非LLM）検証ツール。

標準ライブラリのみで、面接情報リサーチ担当（interview scout）が企業ごとに作成する
companies/{企業スラッグ}/interview_intel.json を機械的に検査する。報告された質問
（reported_questions）・面接形式に関する事実（format_facts）・口コミから読み取れる
傾向（themes）の各配列について、id の形式と重複、出典 URL・エビデンスレベル・引用
の必須性を検査し、search_log で調査経路の記録を強制する。ERROR は成果物として成立
しない欠落・矛盾、WARN は成立するが情報が不足する点を表す。仕様の原本は
references/interview-intel-format.md である。

CLI:
    python validate_interview_intel.py <interview_intel.json> [--json]

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

_SCHEMA_VERSION = "1.0"
_DATE_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
# search_log.fetched_at は YYYY-MM-DD、または日付に時刻が続く ISO 8601 を受ける。
_FETCHED_AT_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}([T ][0-9:.+\-Z]+)?$")

_RQ_ID_PATTERN = re.compile(r"^RQ[0-9]{3,}$")
_FF_ID_PATTERN = re.compile(r"^FF[0-9]{3,}$")
_TH_ID_PATTERN = re.compile(r"^TH[0-9]{3,}$")

_KINDS = ("reported", "inferred")
_GRADES = ("A", "B", "C", "D")


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


def _is_valid_date(value: Any) -> bool:
    """YYYY-MM-DD 形式かつ実在する日付であれば True を返す。"""
    if not isinstance(value, str) or not _DATE_PATTERN.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _is_valid_fetched_at(value: Any) -> bool:
    """YYYY-MM-DD 形式の実在日付、または日付で始まる ISO 8601 であれば True を返す。"""
    if not isinstance(value, str) or not _FETCHED_AT_PATTERN.match(value):
        return False
    try:
        datetime.date.fromisoformat(value[:10])
    except ValueError:
        return False
    return True


def _validate_id(value: Any, pattern: re.Pattern, prefix: str, path: str, seen: set[str], result: ValidationResult) -> None:
    if not _is_nonempty_str(value):
        result.add_error(path, "必須（非空）である")
        return
    if not pattern.match(value):
        result.add_error(path, f"{prefix} に続く3桁以上の数字（{prefix}001 形式）でなければならない（実値: {value!r}）")
        return
    if value in seen:
        result.add_error(path, f"「{value}」が同一配列内で重複している")
        return
    seen.add(value)


def _validate_evidence(entry: dict, path: str, result: ValidationResult) -> None:
    """source_url・grade・quote・accessed という、3配列に共通するエビデンス項目を検査する。"""
    source_url = entry.get("source_url")
    if not (isinstance(source_url, str) and source_url.startswith("http")):
        result.add_error(
            f"{path}.source_url",
            f"source_url は http で始まる文字列でなければならない（実値: {source_url!r}）",
        )

    grade = entry.get("grade")
    if grade not in _GRADES:
        result.add_error(f"{path}.grade", f"grade は {'/'.join(_GRADES)} のいずれかである（実値: {grade!r}）")
    elif grade == "D":
        result.add_warning(f"{path}.grade", "grade が D（個人ブログ・伝聞）である")

    if not _is_nonempty_str(entry.get("quote")):
        result.add_error(f"{path}.quote", "quote は必須（非空）である")

    if "accessed" not in entry or entry.get("accessed") is None:
        result.add_warning(f"{path}.accessed", "accessed が未記載である")
    elif not _is_valid_date(entry["accessed"]):
        result.add_error(
            f"{path}.accessed",
            f"accessed は実在する YYYY-MM-DD 形式の日付でなければならない（実値: {entry['accessed']!r}）",
        )


def _quote_overlaps_question(question: str, quote: str) -> bool:
    q = question.strip()
    quo = quote.strip()
    if not q or not quo:
        return True  # 空文字は question/quote 自体の必須チェックで既に検出している
    return quo in q or q in quo


def _validate_reported_question(entry: Any, path: str, seen: set[str], result: ValidationResult) -> None:
    if not isinstance(entry, dict):
        result.add_error(path, "各要素はオブジェクトでなければならない")
        return

    _validate_id(entry.get("id"), _RQ_ID_PATTERN, "RQ", f"{path}.id", seen, result)

    question = entry.get("question")
    if not _is_nonempty_str(question):
        result.add_error(f"{path}.question", "question は必須（非空）である")

    kind = entry.get("kind")
    if kind not in _KINDS:
        result.add_error(f"{path}.kind", f"kind は {'/'.join(_KINDS)} のいずれかである（実値: {kind!r}）")

    _validate_evidence(entry, path, result)

    quote = entry.get("quote")
    if kind == "reported" and _is_nonempty_str(question) and _is_nonempty_str(quote):
        if not _quote_overlaps_question(question, quote):
            result.add_warning(
                f"{path}.quote",
                "kind が reported の質問は、逐語の質問文と引用（quote）が重なっているべきである",
            )


def _validate_format_fact(entry: Any, path: str, seen: set[str], result: ValidationResult) -> None:
    if not isinstance(entry, dict):
        result.add_error(path, "各要素はオブジェクトでなければならない")
        return

    _validate_id(entry.get("id"), _FF_ID_PATTERN, "FF", f"{path}.id", seen, result)

    if not _is_nonempty_str(entry.get("statement")):
        result.add_error(f"{path}.statement", "statement は必須（非空）である")

    _validate_evidence(entry, path, result)


def _validate_theme(entry: Any, path: str, seen: set[str], result: ValidationResult) -> None:
    if not isinstance(entry, dict):
        result.add_error(path, "各要素はオブジェクトでなければならない")
        return

    _validate_id(entry.get("id"), _TH_ID_PATTERN, "TH", f"{path}.id", seen, result)

    if not _is_nonempty_str(entry.get("theme")):
        result.add_error(f"{path}.theme", "theme は必須（非空）である")
    if not _is_nonempty_str(entry.get("likely_probe")):
        result.add_error(f"{path}.likely_probe", "likely_probe は必須（非空）である")

    _validate_evidence(entry, path, result)


def _validate_array(document: dict, key: str, result: ValidationResult) -> list | None:
    """reported_questions・format_facts・themes 共通: 配列であることを検査し、空なら WARN する。"""
    entries = document.get(key)
    if not isinstance(entries, list):
        result.add_error(key, f"{key} は配列でなければならない")
        return None
    if not entries:
        result.add_warning(key, f"{key} が空である")
    return entries


def _validate_search_log(document: dict, result: ValidationResult) -> None:
    log = document.get("search_log")
    if log is None:
        result.add_error(
            "search_log",
            "search_log は必須である。実行したクエリと取得元を記録しないまま網羅性を主張できない",
        )
        return
    if not isinstance(log, list):
        result.add_error("search_log", "search_log は配列でなければならない")
        return
    if not log:
        result.add_error("search_log", "search_log が空である。実行したクエリを1件以上記録する")

    for i, entry in enumerate(log):
        path = f"search_log[{i}]"
        if not isinstance(entry, dict):
            result.add_error(path, "search_log の各要素はオブジェクトでなければならない")
            continue
        for key in ("query", "source"):
            if not _is_nonempty_str(entry.get(key)):
                result.add_error(f"{path}.{key}", f"{key} は必須（非空）である")
        for key in ("url", "fetched_at", "hit_count", "adopted_count"):
            if key not in entry:
                result.add_error(
                    f"{path}.{key}",
                    f"{key} は必須である。取得できなかった場合は null を書く",
                )
        url = entry.get("url")
        if url is not None and not (isinstance(url, str) and url.startswith("http")):
            result.add_error(
                f"{path}.url",
                f"url は http で始まる文字列または null でなければならない（実値: {url!r}）",
            )
        fetched_at = entry.get("fetched_at")
        if fetched_at is not None and not _is_valid_fetched_at(fetched_at):
            result.add_error(
                f"{path}.fetched_at",
                f"fetched_at は YYYY-MM-DD 形式の実在日付・ISO 8601・null のいずれかである"
                f"（実値: {fetched_at!r}）",
            )
        for key in ("hit_count", "adopted_count"):
            count = entry.get(key)
            if count is None:
                continue
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                result.add_error(
                    f"{path}.{key}",
                    f"{key} は0以上の整数または null でなければならない（実値: {count!r}）",
                )


def _validate_open_questions(document: dict, result: ValidationResult) -> None:
    if "open_questions" not in document:
        return
    entries = document["open_questions"]
    if not isinstance(entries, list):
        result.add_error("open_questions", "open_questions は配列でなければならない")
        return
    for i, item in enumerate(entries):
        if not _is_nonempty_str(item):
            result.add_error(f"open_questions[{i}]", "各要素は非空の文字列でなければならない")


def validate(document: Any) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(document, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result

    version = document.get("schema_version")
    if not _is_nonempty_str(version):
        result.add_error("schema_version", "schema_version は必須（非空）である")
    elif version != _SCHEMA_VERSION:
        result.add_warning(
            "schema_version",
            f"schema_version が既知のバージョン（{_SCHEMA_VERSION}）ではない（実値: {version!r}）",
        )

    if not _is_nonempty_str(document.get("company")):
        result.add_error("company", "company は必須（非空）である")

    role_title = document.get("role_title")
    if "role_title" in document and role_title is not None and not isinstance(role_title, str):
        result.add_error("role_title", "role_title は文字列または null でなければならない")

    researched_at = document.get("researched_at")
    if not _is_nonempty_str(researched_at):
        result.add_error("researched_at", "researched_at は必須（非空）である")
    elif not _is_valid_date(researched_at):
        result.add_error(
            "researched_at",
            f"researched_at は実在する YYYY-MM-DD 形式の日付でなければならない（実値: {researched_at!r}）",
        )

    rq_seen: set[str] = set()
    ff_seen: set[str] = set()
    th_seen: set[str] = set()

    rq_entries = _validate_array(document, "reported_questions", result)
    if rq_entries is not None:
        for i, entry in enumerate(rq_entries):
            _validate_reported_question(entry, f"reported_questions[{i}]", rq_seen, result)

    ff_entries = _validate_array(document, "format_facts", result)
    if ff_entries is not None:
        for i, entry in enumerate(ff_entries):
            _validate_format_fact(entry, f"format_facts[{i}]", ff_seen, result)

    th_entries = _validate_array(document, "themes", result)
    if th_entries is not None:
        for i, entry in enumerate(th_entries):
            _validate_theme(entry, f"themes[{i}]", th_seen, result)

    _validate_search_log(document, result)
    _validate_open_questions(document, result)

    if not _is_nonempty_str(document.get("coverage_notes")):
        result.add_warning("coverage_notes", "coverage_notes が未記載である")

    # 3配列のいずれかが配列でない場合、_validate_array が None を返して形状エラーを既に報告している。
    # ここで None を空として数えると、同じ欠落へ ERROR が二重に付く。
    all_arrays_empty = rq_entries == [] and ff_entries == [] and th_entries == []
    open_questions = document.get("open_questions")
    open_questions_empty = open_questions is None or open_questions == []
    if all_arrays_empty and open_questions_empty:
        result.add_error(
            "(root)",
            "reported_questions・format_facts・themes がすべて空で、open_questions も無い"
            "（成果物が何も語っていない）",
        )

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

    parser = argparse.ArgumentParser(description="job-change-interview-prep 面接情報リサーチ成果物検証ツール")
    parser.add_argument("artifact_path", help="検証対象の interview_intel.json ファイルパス")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    try:
        document = load_json(args.artifact_path)
    except (OSError, ValueError) as exc:
        result = ValidationResult()
        result.add_error(args.artifact_path, f"JSON として読み込めない（{exc}）")
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
