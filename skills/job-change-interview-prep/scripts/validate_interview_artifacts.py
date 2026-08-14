"""job-change-interview-prep: 面接対策の成果物3ファイルの機械的な（非LLM）検証ツール。

標準ライブラリのみで、interview_questions.json・interview_answers.json・
interview_evaluation.json を機械的に検査する。検査する種別はトップレベルのキー
（questions / answers / evaluations）で判別する。degraded と degraded_reason の整合、
question_id の形式と重複、および質問ファイルとの相互参照を、ERROR（成果物として
成立しない欠落・矛盾）と WARN（成立するが情報が不足する点）に分けて報告する。
仕様の原本は references/interview-format.md である。

CLI:
    python validate_interview_artifacts.py <artifact.json> [--json] [--questions <interview_questions.json>]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any

QUESTION_ID_PATTERN = re.compile(r"^Q[0-9]{3,}$")
DATE_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")

# 質問類型の語彙の原本は references/question-bank.md（外資系の2類型は
# references/foreign-interviews.md）にある。
_CATEGORIES = (
    "転職理由",
    "志望動機",
    "自己PR",
    "実績深掘り",
    "弱み",
    "逆質問",
    "ビヘイビアラル",
    "ケース",
)

# 3段階のアンカーの原本は references/evaluation-rubric.md にある。
_SCORE_LEVELS = ("充足", "一部", "不足")
_SCORE_EXCLUDED = "対象外"
_CORE_SCORE_KEYS = ("star", "specificity", "consistency")

# トップレベルのキーと成果物の種別の対応。
_KIND_BY_KEY = {
    "questions": "questions",
    "answers": "answers",
    "evaluations": "evaluation",
}


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


def detect_kind(document: Any) -> str | None:
    """トップレベルのキーから成果物の種別を判別する。判別できない場合は None を返す。"""
    if not isinstance(document, dict):
        return None
    kinds = [kind for key, kind in _KIND_BY_KEY.items() if key in document]
    return kinds[0] if len(kinds) == 1 else None


def question_ids(document: Any) -> set[str]:
    """interview_questions.json から質問 id の集合を取り出す（相互参照の照合先）。"""
    ids: set[str] = set()
    if not isinstance(document, dict):
        return ids
    entries = document.get("questions")
    if not isinstance(entries, list):
        return ids
    for entry in entries:
        if isinstance(entry, dict) and _is_nonempty_str(entry.get("id")):
            ids.add(entry["id"])
    return ids


def _validate_degraded(document: dict, result: ValidationResult) -> bool | None:
    """degraded と degraded_reason の整合を検査し、degraded の値を返す。"""
    degraded = document.get("degraded")
    if not isinstance(degraded, bool):
        result.add_error("degraded", "degraded は真偽値が必須である")
        degraded = None

    if "degraded_reason" not in document:
        result.add_error("degraded_reason", "degraded_reason は必須である")
        return degraded

    reason = document.get("degraded_reason")
    if degraded is True and not _is_nonempty_str(reason):
        result.add_error("degraded_reason", "degraded が true のときは理由の文字列（非空）が必須である")
    elif degraded is False and reason is not None:
        result.add_error("degraded_reason", "degraded が false のときは null でなければならない")
    return degraded


def _validate_question_id(
    value: Any, path: str, seen: set[str], known_ids: set[str] | None, result: ValidationResult
) -> None:
    if not _is_nonempty_str(value):
        result.add_error(path, "必須（非空）である")
        return
    if not QUESTION_ID_PATTERN.match(value):
        result.add_error(path, "Q に続く3桁以上の数字（Q001 形式）でなければならない")
        return
    if value in seen:
        result.add_error(path, f"「{value}」が同一ファイル内で重複している")
        return
    seen.add(value)
    if known_ids is not None and value not in known_ids:
        result.add_error(path, f"「{value}」に対応する質問が interview_questions.json に存在しない")


def _validate_question(entry: Any, path: str, seen: set[str], result: ValidationResult) -> None:
    if not isinstance(entry, dict):
        result.add_error(path, "各要素はオブジェクトでなければならない")
        return

    _validate_question_id(entry.get("id"), f"{path}.id", seen, None, result)

    category = entry.get("category")
    if not _is_nonempty_str(category):
        result.add_error(f"{path}.category", "category は必須（非空）である")
    elif category not in _CATEGORIES:
        result.add_warning(
            f"{path}.category",
            f"既知の質問類型（{'/'.join(_CATEGORIES)}）ではない（実値: {category!r}）",
        )

    for key in ("question", "interviewer_intent", "basis"):
        if not _is_nonempty_str(entry.get(key)):
            result.add_error(f"{path}.{key}", f"{key} は必須（非空）である")


def _validate_answer(
    entry: Any, path: str, seen: set[str], known_ids: set[str] | None, result: ValidationResult
) -> None:
    if not isinstance(entry, dict):
        result.add_error(path, "各要素はオブジェクトでなければならない")
        return

    _validate_question_id(entry.get("question_id"), f"{path}.question_id", seen, known_ids, result)

    if not _is_nonempty_str(entry.get("answer")):
        result.add_error(f"{path}.answer", "answer は必須（非空）である")

    answered_at = entry.get("answered_at")
    if not _is_nonempty_str(answered_at):
        result.add_error(f"{path}.answered_at", "answered_at は必須（非空）である")
    elif not DATE_PATTERN.match(answered_at):
        result.add_error(f"{path}.answered_at", "answered_at は YYYY-MM-DD 形式でなければならない")


def _validate_scores(scores: Any, path: str, degraded: bool | None, result: ValidationResult) -> None:
    if not isinstance(scores, dict):
        result.add_error(path, "scores はオブジェクトが必須である")
        return

    levels = "/".join(_SCORE_LEVELS)
    for key in _CORE_SCORE_KEYS:
        if scores.get(key) not in _SCORE_LEVELS:
            result.add_error(f"{path}.{key}", f"{levels} のいずれかが必須である")

    company_fit = scores.get("company_fit")
    fit_path = f"{path}.company_fit"
    if degraded is True:
        if company_fit is not None and company_fit != _SCORE_EXCLUDED:
            result.add_error(
                fit_path,
                f"degraded が true のときは「{_SCORE_EXCLUDED}」または欠落でなければならない",
            )
    elif company_fit == _SCORE_EXCLUDED:
        result.add_error(
            fit_path,
            f"degraded が true でなければ企業理解の観点を「{_SCORE_EXCLUDED}」にできない",
        )
    elif company_fit not in _SCORE_LEVELS:
        result.add_error(fit_path, f"{levels} のいずれかが必須である")


def _validate_evaluation(
    entry: Any,
    path: str,
    seen: set[str],
    known_ids: set[str] | None,
    degraded: bool | None,
    result: ValidationResult,
) -> None:
    if not isinstance(entry, dict):
        result.add_error(path, "各要素はオブジェクトでなければならない")
        return

    _validate_question_id(entry.get("question_id"), f"{path}.question_id", seen, known_ids, result)
    _validate_scores(entry.get("scores"), f"{path}.scores", degraded, result)

    for key in ("feedback", "improvement"):
        if not _is_nonempty_str(entry.get(key)):
            result.add_error(f"{path}.{key}", f"{key} は必須（非空）である")


def _entries(document: dict, key: str, result: ValidationResult) -> list | None:
    entries = document.get(key)
    if not isinstance(entries, list):
        result.add_error(key, f"{key} は配列でなければならない")
        return None
    if not entries:
        result.add_warning(key, f"{key} が空である")
    return entries


def validate(document: Any, questions: Any = None) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(document, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result

    kind = detect_kind(document)
    if kind is None:
        result.add_error(
            "(root)",
            "questions・answers・evaluations のいずれか1つだけをトップレベルに持たなければならない"
            "（成果物の種別を判別できない）",
        )
        return result

    known_ids = question_ids(questions) if questions is not None else None
    seen: set[str] = set()

    if kind == "questions":
        _validate_degraded(document, result)
        entries = _entries(document, "questions", result)
        if entries is not None:
            for i, entry in enumerate(entries):
                _validate_question(entry, f"questions[{i}]", seen, result)
        return result

    if kind == "answers":
        entries = _entries(document, "answers", result)
        if entries is not None:
            for i, entry in enumerate(entries):
                _validate_answer(entry, f"answers[{i}]", seen, known_ids, result)
        return result

    degraded = _validate_degraded(document, result)
    entries = _entries(document, "evaluations", result)
    if entries is not None:
        for i, entry in enumerate(entries):
            _validate_evaluation(entry, f"evaluations[{i}]", seen, known_ids, degraded, result)
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

    parser = argparse.ArgumentParser(description="job-change-interview-prep 面接対策成果物検証ツール")
    parser.add_argument(
        "artifact_path",
        help="検証対象の interview_questions.json / interview_answers.json / interview_evaluation.json",
    )
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    parser.add_argument(
        "--questions",
        help="interview_questions.json のパス。question_id が質問側に実在するかを検査する",
    )
    args = parser.parse_args(argv)

    def _load(path: str, label: str) -> tuple[Any, ValidationResult | None]:
        try:
            return load_json(path), None
        except (OSError, json.JSONDecodeError) as exc:
            failure = ValidationResult()
            failure.add_error(path, f"{label}を読み込めない（{exc}）")
            return None, failure

    document, failure = _load(args.artifact_path, "検証対象")
    questions = None
    if failure is None and args.questions:
        questions, failure = _load(args.questions, "interview_questions.json")
    if failure is not None:
        if args.json:
            print(json.dumps(failure.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(format_report(failure))
        return 1

    result = validate(document, questions=questions)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(result))

    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
