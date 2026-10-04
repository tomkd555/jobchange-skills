"""job-change-exam-prep: 検査種別の調査結果（exam_assessment.json）の機械的な（非LLM）検証ツール。

標準ライブラリのみで、選考試験調査担当（job-change-exam-scout）が書き出す
exam_assessment.json を機械的に検査する。出典なしの断定と、レベルAの根拠を持たない
「確定」を構造的に防ぐことが主眼であり、ERROR（成果物として成立しない・ルール違反）と
WARN（成立するが不足する点）に分けて報告する。仕様の原本は
references/exam-assessment-format.md である。

CLI:
    python validate_exam_assessment.py <exam_assessment.json> [--json]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any

# 検査名の語彙の原本は references/assessment-catalog.md にある。
# カタログが扱わない検査を企業が使う場合があるため、一覧外の名称は WARN として通す。
_KNOWN_TYPES = (
    "SPI3",
    "玉手箱",
    "GAB",
    "CAB",
    "TG-WEB",
    "TAL",
    "内田クレペリン検査",
    "性格検査",
    "HireVue",
    "pymetrics",
    "英語オンラインテスト",
    "ケース面接",
    "フェルミ推定",
)
# エビデンスレベルの語彙の原本は job-change-company-research の
# references/evidence-grading.md にある。
_VALID_GRADES = ("A", "B", "C", "D")
# confidence の語彙の原本は references/exam-assessment-format.md にある。
_VALID_CONFIDENCE = ("確定", "推定")
# 「確定」を名乗るために必要なエビデンスレベル。
_CONFIRMING_GRADE = "A"


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


def _validate_str_list(value: Any, path: str, result: ValidationResult) -> None:
    """非空の文字列だけを含む配列であることを検査する。"""
    if not isinstance(value, list):
        result.add_error(path, "配列でなければならない")
        return
    for i, item in enumerate(value):
        if not _is_nonempty_str(item):
            result.add_error(f"{path}[{i}]", "非空の文字列でなければならない")


def _validate_evidence(entry: Any, path: str, result: ValidationResult) -> str | None:
    """根拠1件を検査し、正当な grade があればそれを返す。"""
    if not isinstance(entry, dict):
        result.add_error(path, "各根拠はオブジェクトでなければならない")
        return None

    source_url = entry.get("source_url")
    if not _is_nonempty_str(source_url) or not source_url.startswith("http"):
        result.add_error(f"{path}.source_url", "source_url は http で始まる文字列が必須である")

    grade = entry.get("grade")
    if grade not in _VALID_GRADES:
        result.add_error(
            f"{path}.grade",
            f"grade は {'/'.join(_VALID_GRADES)} のいずれかでなければならない",
        )
        grade = None

    if not _is_nonempty_str(entry.get("quote")):
        result.add_error(f"{path}.quote", "quote は必須（非空）である")

    return grade


def _validate_assessment(entry: Any, path: str, result: ValidationResult) -> None:
    if not isinstance(entry, dict):
        result.add_error(path, "各要素はオブジェクトでなければならない")
        return

    exam_type = entry.get("type")
    if not _is_nonempty_str(exam_type):
        result.add_error(f"{path}.type", "type は必須（非空）である")
    elif exam_type not in _KNOWN_TYPES:
        result.add_warning(
            f"{path}.type",
            f"assessment-catalog.md が扱う検査名ではない（実値: {exam_type!r}）",
        )

    if not _is_nonempty_str(entry.get("stage")):
        result.add_warning(f"{path}.stage", "stage が未設定である")

    grades: list[str] = []
    evidence = entry.get("evidence")
    if not isinstance(evidence, list):
        result.add_error(f"{path}.evidence", "evidence は配列が必須である")
    elif not evidence:
        result.add_error(f"{path}.evidence", "evidence は1件以上必要である（出典のない断定を認めない）")
    else:
        for i, item in enumerate(evidence):
            grade = _validate_evidence(item, f"{path}.evidence[{i}]", result)
            if grade is not None:
                grades.append(grade)

    confidence = entry.get("confidence")
    if confidence not in _VALID_CONFIDENCE:
        result.add_error(
            f"{path}.confidence",
            f"confidence は {'/'.join(_VALID_CONFIDENCE)} のいずれかでなければならない",
        )
    elif confidence == "確定" and _CONFIRMING_GRADE not in grades:
        result.add_error(
            f"{path}.confidence",
            f"「確定」はレベル {_CONFIRMING_GRADE} の根拠を1件以上必要とする",
        )
    elif confidence == "推定" and isinstance(evidence, list) and len(evidence) == 1:
        result.add_warning(
            f"{path}.evidence",
            "根拠が1件のみである。対策計画でその限界を明示する",
        )

    if not _is_nonempty_str(entry.get("format_notes")):
        result.add_warning(f"{path}.format_notes", "format_notes が未設定である")

    recommendations = entry.get("prep_recommendations")
    _validate_str_list(recommendations, f"{path}.prep_recommendations", result)
    if isinstance(recommendations, list) and not recommendations:
        result.add_warning(f"{path}.prep_recommendations", "推奨対策が1件も無い")


def validate(document: Any) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(document, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result

    if not _is_nonempty_str(document.get("company")):
        result.add_error("company", "company は必須（非空）である")

    open_questions = document.get("open_questions")
    _validate_str_list(open_questions, "open_questions", result)

    assessments = document.get("assessments")
    if not isinstance(assessments, list):
        result.add_error("assessments", "assessments は配列が必須である")
        return result

    if not assessments:
        result.add_warning("assessments", "検査種別を1件も特定できていない")
        if isinstance(open_questions, list) and not open_questions:
            result.add_error(
                "assessments",
                "assessments が空で open_questions も空である（未特定の事情を残していない）",
            )

    for i, entry in enumerate(assessments):
        _validate_assessment(entry, f"assessments[{i}]", result)

    return result


def load_assessment(path: str) -> Any:
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

    parser = argparse.ArgumentParser(description="job-change-exam-prep 検査種別調査結果の検証ツール")
    parser.add_argument("assessment_path", help="検証対象の exam_assessment.json ファイルパス")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    try:
        document = load_assessment(args.assessment_path)
    except (OSError, ValueError) as exc:
        result = ValidationResult()
        result.add_error(args.assessment_path, f"JSON として読み込めない（{exc}）")
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
