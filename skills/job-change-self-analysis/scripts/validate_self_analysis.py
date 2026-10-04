"""job-change-self-analysis: 自己分析成果物（self_analysis.json）の機械的な（非LLM）検証ツール。

標準ライブラリのみで、自己分析の原本である self_analysis.json を機械的に検査する。
面接対策・志望動機の深化（job-change-interview-prep / job-change-documents）が
読める成果物として成立しているかを、ERROR（成果物として成立しない欠落・矛盾）と
WARN（成立するが情報が不足し成果物の質を下げる点）に分けて報告する。仕様の原本は
references/self-analysis-format.md である。

CLI:
    python validate_self_analysis.py <self_analysis.json> [--json]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any


# others_feedback[].source_type の値域。
# 語彙の原本は references/self-analysis-format.md の others_feedback 節にある。
SOURCE_TYPES = ("上司", "同僚", "部下", "顧客", "友人・家族", "評価面談")

# schema_version の既知の値。これ以外は WARN。
_KNOWN_SCHEMA_VERSIONS = ("1.0", "1.1")

# personality.markers[].construct の値域。原本は references/personality-guide.md の
# 「構成概念の語彙」表（表の順序どおり）。
PERSONALITY_CONSTRUCTS = (
    "conscientiousness",
    "emotional_stability",
    "extraversion",
    "agreeableness",
    "openness",
    "honesty_humility",
    "grit",
    "self_efficacy",
    "planning_style",
    "collaboration_style",
    "change_orientation",
    "decision_style",
    "feedback_timing",
    "stress_trigger",
    "recovery_style",
)

# personality.presentation の型ラベル検出用パターン（「〜型です」「〜タイプである」等）。
# 「判断の型である」のように直前が「の」の場合は、構成概念の名称の一部であって分類ラベルではないため除外する。
# 除外は「型」だけに掛け、「タイプ」には掛けない。「計画重視のタイプです」のような分類ラベルは
# 「の」が前にあっても WARN の対象のままにする。
_TYPE_LABEL_RE = re.compile(r"((?<!の)型|タイプ)(です|である|だ|と言え|に当た|に分類)")


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


def _has_any_nonempty_str(values: Any) -> bool:
    return isinstance(values, list) and any(_is_nonempty_str(v) for v in values)


def _check_id(entry: dict, path: str, seen: set[str], result: ValidationResult) -> None:
    """id の欠落を ERROR、重複を WARN として報告し、有効な id を seen へ加える。

    id が欠落したまま集合へ入らないと、その要素を指す参照が「実在しない id」として
    検出されず、参照整合の検査そのものが意味を失う。このため id は必須とする。
    """
    value = entry.get("id")
    if not _is_nonempty_str(value):
        result.add_error(f"{path}.id", "id は必須（非空の文字列）である")
        return
    if value in seen:
        result.add_warning(f"{path}.id", f"id '{value}' が重複している")
    seen.add(value)


def _validate_behavioral_episodes(document: dict, result: ValidationResult) -> set[str]:
    """id と situation・action・result の欠落を検査し、参照整合用の episode_id 集合を返す。"""
    episodes = document.get("behavioral_episodes")
    episode_ids: set[str] = set()
    if not isinstance(episodes, list) or not episodes:
        result.add_error(
            "behavioral_episodes", "behavioral_episodes は1件以上必要である"
        )
        return episode_ids
    for i, entry in enumerate(episodes):
        path = f"behavioral_episodes[{i}]"
        if not isinstance(entry, dict):
            result.add_error(path, "エピソードの各要素はオブジェクトでなければならない")
            continue
        _check_id(entry, path, episode_ids, result)
        for key in ("situation", "action", "result"):
            if not _is_nonempty_str(entry.get(key)):
                result.add_error(f"{path}.{key}", f"{key} は必須（非空）である")
    return episode_ids


def _validate_others_feedback(document: dict, result: ValidationResult) -> set[str]:
    """id と source_type を検査し、参照整合用の feedback_id 集合を返す。"""
    feedback = document.get("others_feedback")
    feedback_ids: set[str] = set()
    if not isinstance(feedback, list):
        return feedback_ids
    for i, entry in enumerate(feedback):
        path = f"others_feedback[{i}]"
        if not isinstance(entry, dict):
            result.add_error(
                path, "others_feedback の各要素はオブジェクトでなければならない"
            )
            continue
        _check_id(entry, path, feedback_ids, result)
        source_type = entry.get("source_type")
        if source_type is not None and source_type not in SOURCE_TYPES:
            result.add_warning(
                f"{path}.source_type",
                f"source_type '{source_type}' が規定の値域（{'・'.join(SOURCE_TYPES)}）にない",
            )
    return feedback_ids


def _check_ref_ids(
    ref_ids: Any, valid_ids: set[str], path: str, label: str, result: ValidationResult
) -> None:
    if not isinstance(ref_ids, list):
        return
    for ref_id in ref_ids:
        if _is_nonempty_str(ref_id) and ref_id not in valid_ids:
            result.add_error(
                path, f"参照する{label} '{ref_id}' が実在しない（参照整合エラー）"
            )


def _validate_personality(
    document: dict,
    result: ValidationResult,
    episode_ids: set[str],
    feedback_ids: set[str],
) -> tuple[set[str], set[str]]:
    """personality を検証する。

    strengths[].constructs の裏付け判定に使う
    (自己申告のある構成概念の集合, うちエピソードか他者証言に対応づいている構成概念の集合)
    を返す。personality が無い（1.0 文書）場合は両方とも空集合になる。
    """
    constructs_present: set[str] = set()
    constructs_evidenced: set[str] = set()

    personality = document.get("personality")
    if personality is None:
        return constructs_present, constructs_evidenced
    if not isinstance(personality, dict):
        result.add_error("personality", "personality はオブジェクトでなければならない")
        return constructs_present, constructs_evidenced

    markers = personality.get("markers")
    if not isinstance(markers, list):
        result.add_error("personality.markers", "markers は配列（0件可）でなければならない")
    else:
        marker_ids: set[str] = set()
        for i, entry in enumerate(markers):
            path = f"personality.markers[{i}]"
            if not isinstance(entry, dict):
                result.add_error(path, "markers の各要素はオブジェクトでなければならない")
                continue
            _check_id(entry, path, marker_ids, result)

            construct = entry.get("construct")
            if not _is_nonempty_str(construct):
                result.add_error(f"{path}.construct", "construct は必須（非空）である")
                construct_valid = False
            elif construct not in PERSONALITY_CONSTRUCTS:
                result.add_error(
                    f"{path}.construct", f"construct '{construct}' が構成概念の語彙にない"
                )
                construct_valid = False
            else:
                construct_valid = True
                constructs_present.add(construct)

            if not _is_nonempty_str(entry.get("response")):
                result.add_error(f"{path}.response", "response は必須（非空）である")

            options = entry.get("options")
            response = entry.get("response")
            if options is not None:
                if (
                    not isinstance(options, list)
                    or not (2 <= len(options) <= 4)
                    or not all(_is_nonempty_str(o) for o in options)
                ):
                    result.add_error(
                        f"{path}.options",
                        "options は2〜4件の非空文字列の配列でなければならない",
                    )
                elif _is_nonempty_str(response) and response not in options:
                    result.add_error(
                        f"{path}.response", "response が options のいずれとも一致しない"
                    )

            linked_episode_ids = entry.get("linked_episode_ids")
            fb_refs = entry.get("feedback_ids")
            _check_ref_ids(
                linked_episode_ids,
                episode_ids,
                f"{path}.linked_episode_ids",
                "episode_id",
                result,
            )
            _check_ref_ids(fb_refs, feedback_ids, f"{path}.feedback_ids", "feedback_id", result)

            has_evidence = _has_any_nonempty_str(linked_episode_ids) or _has_any_nonempty_str(
                fb_refs
            )
            if not has_evidence:
                result.add_warning(
                    path,
                    "自己申告だけの記録である（エピソードにも他者証言にも対応づいていない）",
                )
            elif construct_valid:
                constructs_evidenced.add(construct)

    presentation = personality.get("presentation")
    if presentation is not None:
        if not isinstance(presentation, str):
            result.add_error("personality.presentation", "presentation は文字列でなければならない")
        elif _TYPE_LABEL_RE.search(presentation):
            result.add_warning("personality.presentation", "型やタイプの名称で分類している")

    return constructs_present, constructs_evidenced


def _validate_strengths(
    document: dict,
    result: ValidationResult,
    episode_ids: set[str],
    feedback_ids: set[str],
    constructs_present: set[str],
    constructs_evidenced: set[str],
) -> None:
    strengths = document.get("strengths")
    if not isinstance(strengths, list):
        return
    for i, entry in enumerate(strengths):
        path = f"strengths[{i}]"
        if not isinstance(entry, dict):
            result.add_error(path, "strengths の各要素はオブジェクトでなければならない")
            continue
        if not _is_nonempty_str(entry.get("statement")):
            result.add_error(f"{path}.statement", "statement は必須（非空）である")
        ep_refs = entry.get("episode_ids")
        fb_refs = entry.get("feedback_ids")
        if not _has_any_nonempty_str(ep_refs) and not _has_any_nonempty_str(fb_refs):
            result.add_error(
                path,
                "episode_ids と feedback_ids が両方空である（内省単独の強みは不可）",
            )
        _check_ref_ids(ep_refs, episode_ids, f"{path}.episode_ids", "episode_id", result)
        _check_ref_ids(fb_refs, feedback_ids, f"{path}.feedback_ids", "feedback_id", result)

        constructs = entry.get("constructs")
        if constructs is not None:
            if not isinstance(constructs, list) or not all(
                isinstance(c, str) for c in constructs
            ):
                result.add_error(
                    f"{path}.constructs", "constructs は文字列の配列でなければならない"
                )
            else:
                for construct in constructs:
                    if construct not in PERSONALITY_CONSTRUCTS:
                        result.add_error(
                            f"{path}.constructs",
                            f"construct '{construct}' が構成概念の語彙にない",
                        )
                    elif construct in constructs_present and construct not in constructs_evidenced:
                        result.add_warning(
                            f"{path}.constructs",
                            f"構成概念 '{construct}' の自己申告が強みの根拠に紛れ込んでいないかを確かめる",
                        )


def _validate_values(
    document: dict, result: ValidationResult, episode_ids: set[str]
) -> None:
    values = document.get("values")
    if not isinstance(values, list):
        return
    for i, entry in enumerate(values):
        if not isinstance(entry, dict):
            continue
        _check_ref_ids(
            entry.get("evidence_episode_ids"),
            episode_ids,
            f"values[{i}].evidence_episode_ids",
            "episode_id",
            result,
        )


def _validate_career_adaptability(
    document: dict, result: ValidationResult, episode_ids: set[str]
) -> None:
    adaptability = document.get("career_adaptability")
    if not isinstance(adaptability, dict):
        return
    for dimension in ("concern", "control", "curiosity", "confidence"):
        entry = adaptability.get(dimension)
        if not isinstance(entry, dict):
            continue
        _check_ref_ids(
            entry.get("evidence_episode_ids"),
            episode_ids,
            f"career_adaptability.{dimension}.evidence_episode_ids",
            "episode_id",
            result,
        )


def _validate_career_narrative(document: dict, result: ValidationResult) -> None:
    narrative = document.get("career_narrative")
    if not isinstance(narrative, dict):
        result.add_error("career_narrative", "career_narrative はオブジェクトが必須である")
        return
    if not _is_nonempty_str(narrative.get("life_theme")):
        result.add_error("career_narrative.life_theme", "life_theme は必須（非空）である")
    if not _is_nonempty_str(narrative.get("consistent_motivation")):
        result.add_error(
            "career_narrative.consistent_motivation",
            "consistent_motivation は必須（非空）である",
        )


def _validate_reason_for_change(document: dict, result: ValidationResult) -> None:
    reason = document.get("reason_for_change")
    if not isinstance(reason, dict):
        result.add_error("reason_for_change", "reason_for_change はオブジェクトが必須である")
        return
    if not _has_any_nonempty_str(reason.get("raw_reasons")):
        result.add_error(
            "reason_for_change.raw_reasons", "raw_reasons は1件以上必要である"
        )
    if not _is_nonempty_str(reason.get("constructive_version")):
        result.add_error(
            "reason_for_change.constructive_version",
            "constructive_version は必須（非空）である",
        )


def _warn_others_feedback(document: dict, result: ValidationResult) -> None:
    feedback = document.get("others_feedback")
    if not isinstance(feedback, list) or not feedback:
        result.add_warning(
            "others_feedback",
            "他者フィードバックが0件である。他者視点の収集を推奨する",
        )


def _warn_metric(document: dict, result: ValidationResult) -> None:
    episodes = document.get("behavioral_episodes")
    if not isinstance(episodes, list):
        return
    has_metric = any(
        isinstance(e, dict) and _is_nonempty_str(e.get("metric")) for e in episodes
    )
    if not has_metric:
        result.add_warning(
            "behavioral_episodes[].metric",
            "定量的な実績（metric）が1件もない。可能な範囲で数値を metric に入れることを推奨する",
        )


def _warn_updated_at(document: dict, result: ValidationResult) -> None:
    if not _is_nonempty_str(document.get("updated_at")):
        result.add_warning("updated_at", "updated_at が未設定である")


def _warn_schema_version(document: dict, result: ValidationResult) -> None:
    version = document.get("schema_version")
    if _is_nonempty_str(version) and version not in _KNOWN_SCHEMA_VERSIONS:
        result.add_warning(
            "schema_version",
            f"schema_version '{version}' が既知の値（{'・'.join(_KNOWN_SCHEMA_VERSIONS)}）にない",
        )


def _warn_interests(document: dict, result: ValidationResult) -> None:
    interests = document.get("interests")
    if not isinstance(interests, dict):
        result.add_warning("interests", "interests が未記入である")
        return
    if not _has_any_nonempty_str(interests.get("domains")) and not _has_any_nonempty_str(
        interests.get("concrete_topics")
    ):
        result.add_warning("interests", "interests が未記入である")


def _warn_values(document: dict, result: ValidationResult) -> None:
    values = document.get("values")
    if not isinstance(values, list) or not values:
        result.add_warning("values", "values が未記入である")


def _warn_constructive_version(document: dict, result: ValidationResult) -> None:
    reason = document.get("reason_for_change")
    if not isinstance(reason, dict):
        return
    constructive = reason.get("constructive_version")
    raw_reasons = reason.get("raw_reasons")
    if not _is_nonempty_str(constructive) or not isinstance(raw_reasons, list):
        return
    constructive_stripped = constructive.strip()
    if any(
        _is_nonempty_str(r) and r.strip() == constructive_stripped for r in raw_reasons
    ):
        result.add_warning(
            "reason_for_change.constructive_version",
            "constructive_version が raw_reasons と同一文字列のままである（建設的な言い換えができていない）",
        )


def validate(document: Any) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(document, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result

    if not _is_nonempty_str(document.get("schema_version")):
        result.add_error("schema_version", "schema_version は必須（非空）である")

    episode_ids = _validate_behavioral_episodes(document, result)
    feedback_ids = _validate_others_feedback(document, result)
    constructs_present, constructs_evidenced = _validate_personality(
        document, result, episode_ids, feedback_ids
    )

    _validate_strengths(
        document, result, episode_ids, feedback_ids, constructs_present, constructs_evidenced
    )
    _validate_values(document, result, episode_ids)
    _validate_career_adaptability(document, result, episode_ids)
    _validate_career_narrative(document, result)
    _validate_reason_for_change(document, result)

    _warn_others_feedback(document, result)
    _warn_metric(document, result)
    _warn_updated_at(document, result)
    _warn_interests(document, result)
    _warn_values(document, result)
    _warn_constructive_version(document, result)
    _warn_schema_version(document, result)

    return result


def load_self_analysis(path: str) -> Any:
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

    parser = argparse.ArgumentParser(description="job-change-self-analysis 自己分析検証ツール")
    parser.add_argument("self_analysis_path", help="検証対象の self_analysis.json ファイルパス")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    try:
        document = load_self_analysis(args.self_analysis_path)
    except (OSError, ValueError) as exc:
        result = ValidationResult()
        result.add_error(args.self_analysis_path, f"JSON として読み込めない（{exc}）")
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
