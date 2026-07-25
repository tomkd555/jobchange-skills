"""job-change-support: 利用者プロファイル（profile.json）の決定的（非LLM）検証ツール。

標準ライブラリのみで、転職支援スキル群の原本である profile.json を機械検査する。
プロファイルが後続のサブスキル（企業研究・応募書類・面接対策・試験対策）の前提を
満たすかを、ERROR（プロファイルとして成立しない欠落）と WARN（成立するが情報が
不足し成果物の質を下げる点）に分けて報告する。仕様の原本は
references/profile-format.md である。

CLI:
    python validate_profile.py <profile.json> [--json]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any

_PERIOD_RE = re.compile(r"^(\d{4})-(\d{2})〜(?:(\d{4})-(\d{2})|現在)$")
_ONGOING_SENTINEL = 999912  # "〜現在" の終端を表す、実在しえない大きな月インデックス
_PORTABLE_CATEGORIES = ("対課題", "対人")
_KNOWN_SCHEMA_VERSIONS = ("1.0", "1.1", "2.0")
_V1_SCHEMA_VERSIONS = ("1.0", "1.1")
_V2_SCHEMA_VERSION = "2.0"

# 語彙の原本は references/screening-axes.md にある。
_SCREENING_AXES = (
    "remote_certainty",
    "overtime_hours",
    "annual_holidays",
    "oncall_load",
    "hands_on_ratio",
    "coordination_ratio",
    "experience_distance",
    "salary_condition",
)
_WORK_CHARACTER_TRAITS = (
    "hands_on",
    "build_ops_ratio",
    "low_coordination",
    "full_remote_guaranteed",
    "no_oncall",
    "clear_completion",
    "solo_completable",
    "short_feedback",
)
_CONDITION_LEVELS = ("must", "want")
_CONDITION_OPERATORS = (">=", "<=", "==", "in", "qualitative")
_CONDITION_VERIFICATIONS = ("posting", "research", "interview", "unverifiable")
_DESIRE_LEVELS = ("must", "important", "neutral", "not_required")
_CONDITION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_MUST_CONDITION_SOFT_LIMIT = 4


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


def _parse_period(value: Any) -> tuple[int, int] | None:
    """period文字列を (開始月インデックス, 終了月インデックス) に変換する。

    形式は YYYY-MM〜YYYY-MM または YYYY-MM〜現在。解析できない場合は None を返す。
    """
    if not isinstance(value, str):
        return None
    m = _PERIOD_RE.match(value)
    if not m:
        return None
    y1, mo1 = int(m.group(1)), int(m.group(2))
    if not (1 <= mo1 <= 12):
        return None
    start = y1 * 12 + mo1
    if m.group(3) is not None:
        y2, mo2 = int(m.group(3)), int(m.group(4))
        if not (1 <= mo2 <= 12):
            return None
        end = y2 * 12 + mo2
    else:
        end = _ONGOING_SENTINEL
    return start, end


def _validate_basic(profile: dict, result: ValidationResult) -> None:
    basic = profile.get("basic")
    if not isinstance(basic, dict):
        result.add_error("basic", "basic はオブジェクトが必須である")
        return
    if not _is_nonempty_str(basic.get("current_role")):
        result.add_error("basic.current_role", "current_role は必須（非空）である")


def _validate_career_history(profile: dict, result: ValidationResult) -> None:
    career = profile.get("career_history")
    if not isinstance(career, list) or not career:
        result.add_error("career_history", "career_history は1件以上必要である")
        return
    for i, entry in enumerate(career):
        path = f"career_history[{i}]"
        if not isinstance(entry, dict):
            result.add_error(path, "職歴の各要素はオブジェクトでなければならない")
            continue
        for key in ("company", "period", "role"):
            if not _is_nonempty_str(entry.get(key)):
                result.add_error(f"{path}.{key}", f"{key} は必須（非空）である")


def _validate_job_change_axis(profile: dict, result: ValidationResult) -> None:
    axis = profile.get("job_change_axis")
    if not isinstance(axis, dict):
        result.add_error("job_change_axis", "job_change_axis はオブジェクトが必須である")
        return
    reasons = axis.get("reasons")
    if not isinstance(reasons, list) or not any(_is_nonempty_str(r) for r in reasons):
        result.add_error(
            "job_change_axis.reasons",
            "reasons は転職理由を1件以上持たなければならない",
        )


def _warn_achievements(profile: dict, result: ValidationResult) -> None:
    career = profile.get("career_history")
    if not isinstance(career, list):
        return
    has_metric = False
    for entry in career:
        if not isinstance(entry, dict):
            continue
        achievements = entry.get("achievements")
        if not isinstance(achievements, list):
            continue
        for ach in achievements:
            if isinstance(ach, dict) and _is_nonempty_str(ach.get("metric")):
                has_metric = True
                break
        if has_metric:
            break
    if not has_metric:
        result.add_warning(
            "career_history[].achievements",
            "定量的な実績（metric）が1件もない。可能な範囲で数値を metric に入れることを推奨する",
        )


def _warn_skills(profile: dict, result: ValidationResult) -> None:
    skills = profile.get("skills")
    if not isinstance(skills, dict):
        result.add_warning("skills", "skills が未記入である")
        return
    categories = ("technical", "business", "languages", "certifications")
    if not any(isinstance(skills.get(c), list) and skills.get(c) for c in categories):
        result.add_warning("skills", "skills の全カテゴリが空である")


def _warn_targets(profile: dict, result: ValidationResult) -> None:
    targets = profile.get("targets")
    if not isinstance(targets, dict):
        result.add_warning("targets", "targets が未記入である")
        return
    categories = ("industries", "roles", "companies")
    if not any(isinstance(targets.get(c), list) and targets.get(c) for c in categories):
        result.add_warning("targets", "targets の全カテゴリが空である")


def _warn_updated_at(profile: dict, result: ValidationResult) -> None:
    if not _is_nonempty_str(profile.get("updated_at")):
        result.add_warning("updated_at", "updated_at が未設定である")


def _warn_schema_version_known(profile: dict, result: ValidationResult) -> None:
    """W1: schema_version が既知のバージョン（1.0/1.1）以外である。"""
    version = profile.get("schema_version")
    if _is_nonempty_str(version) and version not in _KNOWN_SCHEMA_VERSIONS:
        result.add_warning(
            "schema_version",
            f"schema_version が既知のバージョン（{'/'.join(_KNOWN_SCHEMA_VERSIONS)}）ではない",
        )


def _warn_career_history_period_format(profile: dict, result: ValidationResult) -> None:
    """W2: career_history[].period が YYYY-MM〜YYYY-MM / YYYY-MM〜現在 の形式でない。"""
    career = profile.get("career_history")
    if not isinstance(career, list):
        return
    for i, entry in enumerate(career):
        if not isinstance(entry, dict):
            continue
        period = entry.get("period")
        if not _is_nonempty_str(period):
            continue  # 欠落・空は ERROR 側が既に報告する
        if _parse_period(period) is None:
            result.add_warning(
                f"career_history[{i}].period",
                "period が既定の形式（YYYY-MM〜YYYY-MM または YYYY-MM〜現在）と一致しない",
            )


def _warn_career_gaps(profile: dict, result: ValidationResult) -> None:
    """W3: 全 period が解析可能な場合に限り、6ヶ月以上の空白で career_gaps 未記載のものを検出する。"""
    career = profile.get("career_history")
    if not isinstance(career, list) or len(career) < 2:
        return

    parsed: list[tuple[int, int, str]] = []
    for entry in career:
        if not isinstance(entry, dict):
            return  # 解析不能。W3 は判定しない
        period = entry.get("period")
        span = _parse_period(period)
        if span is None:
            return  # 解析不能な period が1件でもあれば W3 は判定しない
        parsed.append((span[0], span[1], period))

    ordered = sorted(parsed, key=lambda item: item[0])
    gaps: list[tuple[int, int, str, str]] = []
    for prev, nxt in zip(ordered, ordered[1:]):
        gap_months = nxt[0] - prev[1] - 1
        if gap_months >= 6:
            gaps.append((prev[1] + 1, nxt[0] - 1, prev[2], nxt[2]))
    if not gaps:
        return

    covered_ranges: list[tuple[int, int]] = []
    career_gaps = profile.get("career_gaps")
    if isinstance(career_gaps, list):
        for g in career_gaps:
            if not isinstance(g, dict):
                continue
            span = _parse_period(g.get("period"))
            if span is not None:
                covered_ranges.append(span)

    for gap_start, gap_end, prev_period, next_period in gaps:
        covered = any(
            cov_start <= gap_end and cov_end >= gap_start
            for cov_start, cov_end in covered_ranges
        )
        if not covered:
            result.add_warning(
                "career_gaps",
                f"「{prev_period}」と「{next_period}」の間に6ヶ月以上の空白があるが、"
                "対応する career_gaps の記載が無い",
            )


def _warn_skills_languages_shape(profile: dict, result: ValidationResult) -> None:
    """W4: skills.languages の要素が {"language","level"} を持つオブジェクトでない。"""
    skills = profile.get("skills")
    if not isinstance(skills, dict):
        return
    languages = skills.get("languages")
    if not isinstance(languages, list):
        return
    for i, lang in enumerate(languages):
        valid = (
            isinstance(lang, dict)
            and _is_nonempty_str(lang.get("language"))
            and _is_nonempty_str(lang.get("level"))
        )
        if not valid:
            result.add_warning(
                f"skills.languages[{i}]",
                "language と level を持つオブジェクトの形式ではない",
            )


def _warn_salary_types(profile: dict, result: ValidationResult) -> None:
    """W5: salary.current / salary.desired が number でも null でもない。"""
    salary = profile.get("salary")
    if not isinstance(salary, dict):
        return
    for key in ("current", "desired"):
        if key not in salary:
            continue
        value = salary[key]
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            result.add_warning(
                f"salary.{key}",
                "current/desired は数値または null でなければならない",
            )


def _warn_must_conditions_count(profile: dict, result: ValidationResult) -> None:
    """W6: 必須条件の総数が4件以上である。

    v1 では job_change_axis.must_conditions の件数、v2 では conditions[level=must] と
    work_character_preferences[desire=must] の合計で数える。ルールの目的は「必須条件を
    増やしすぎて母集団を潰さない」ことにあり、実質的な必須条件の総数で判断する。
    """
    axis = profile.get("job_change_axis")
    if not isinstance(axis, dict):
        return

    if schema_version_of(profile) == _V2_SCHEMA_VERSION:
        total = len(_must_conditions(axis)) + len(_must_traits(axis))
        if total >= _MUST_CONDITION_SOFT_LIMIT:
            result.add_warning(
                "job_change_axis",
                f"必須条件（conditions の must と work_character_preferences の must）の合計が"
                f"{total}件である。3件程度に絞ることを推奨する",
            )
        return

    must = axis.get("must_conditions")
    if isinstance(must, list) and len(must) >= _MUST_CONDITION_SOFT_LIMIT:
        result.add_warning(
            "job_change_axis.must_conditions",
            "must_conditions が4件以上である。3件程度に絞ることを推奨する",
        )


def schema_version_of(profile: Any) -> str:
    """profile の schema_version を返す。取得できない場合は空文字を返す。"""
    if not isinstance(profile, dict):
        return ""
    version = profile.get("schema_version")
    return version if isinstance(version, str) else ""


def _must_conditions(axis: dict) -> list[dict]:
    conditions = axis.get("conditions")
    if not isinstance(conditions, list):
        return []
    return [c for c in conditions if isinstance(c, dict) and c.get("level") == "must"]


def _must_traits(axis: dict) -> list[dict]:
    preferences = axis.get("work_character_preferences")
    if not isinstance(preferences, list):
        return []
    return [p for p in preferences if isinstance(p, dict) and p.get("desire") == "must"]


def _validate_conditions(axis: dict, result: ValidationResult) -> None:
    """v2: job_change_axis.conditions[] を検査する。"""
    conditions = axis.get("conditions")
    if not isinstance(conditions, list):
        result.add_error(
            "job_change_axis.conditions",
            "schema_version 2.0 では conditions は配列が必須である",
        )
        return

    seen_ids: set[str] = set()
    must_axes: dict[str, int] = {}
    for i, condition in enumerate(conditions):
        path = f"job_change_axis.conditions[{i}]"
        if not isinstance(condition, dict):
            result.add_error(path, "conditions の各要素はオブジェクトでなければならない")
            continue

        condition_id = condition.get("id")
        if not _is_nonempty_str(condition_id) or not _CONDITION_ID_RE.match(condition_id):
            result.add_error(f"{path}.id", "id は `^[a-z0-9][a-z0-9-]*$` に一致する非空文字列である")
        elif condition_id in seen_ids:
            result.add_error(f"{path}.id", f"id が重複している: {condition_id}")
        else:
            seen_ids.add(condition_id)

        level = condition.get("level")
        if level not in _CONDITION_LEVELS:
            result.add_error(f"{path}.level", f"level は {'/'.join(_CONDITION_LEVELS)} のいずれかである")

        if not _is_nonempty_str(condition.get("statement")):
            result.add_error(f"{path}.statement", "statement は必須（非空）である")

        axis_id = condition.get("axis")
        if axis_id is not None and axis_id not in _SCREENING_AXES:
            result.add_error(
                f"{path}.axis",
                "axis は screening-axes.md の8軸 id のいずれか、または null である",
            )
        elif level == "must" and axis_id is not None:
            must_axes[axis_id] = must_axes.get(axis_id, 0) + 1

        operator = condition.get("operator")
        if operator not in _CONDITION_OPERATORS:
            result.add_error(
                f"{path}.operator",
                f"operator は {'/'.join(_CONDITION_OPERATORS)} のいずれかである",
            )
        elif operator != "qualitative" and condition.get("value") is None:
            result.add_error(
                f"{path}.value",
                "operator が qualitative でない条件に value は必須である（比較できない条件を機械条件にしない）",
            )

        verification = condition.get("verification")
        if verification not in _CONDITION_VERIFICATIONS:
            result.add_error(
                f"{path}.verification",
                f"verification は {'/'.join(_CONDITION_VERIFICATIONS)} のいずれかである",
            )

    for axis_id, count in sorted(must_axes.items()):
        if count > 1:
            result.add_warning(
                "job_change_axis.conditions",
                f"同じ軸に必須条件が{count}件ある（axis={axis_id}）。判定では最も厳しい閾値を採る",
            )

    must_list = _must_conditions(axis)
    if not must_list:
        result.add_warning(
            "job_change_axis.conditions",
            "level=must の条件が1件も無い。必須条件が無いと求人検索の選別が働かない",
        )

    priorities = [c.get("priority") for c in must_list]
    valid = [p for p in priorities if isinstance(p, int) and not isinstance(p, bool)]
    if len(valid) < len(must_list):
        result.add_warning(
            "job_change_axis.conditions",
            "level=must の条件に priority（整数）が付いていないものがある",
        )
    elif len(set(valid)) < len(valid):
        result.add_warning("job_change_axis.conditions", "level=must の条件の priority が重複している")


def _validate_work_character_preferences(axis: dict, result: ValidationResult) -> None:
    """v2: job_change_axis.work_character_preferences[] を検査する。"""
    preferences = axis.get("work_character_preferences")
    if not isinstance(preferences, list):
        result.add_error(
            "job_change_axis.work_character_preferences",
            "schema_version 2.0 では work_character_preferences は配列が必須である",
        )
        return

    seen: list[str] = []
    for i, preference in enumerate(preferences):
        path = f"job_change_axis.work_character_preferences[{i}]"
        if not isinstance(preference, dict):
            result.add_error(path, "各要素はオブジェクトでなければならない")
            continue

        trait = preference.get("trait")
        if trait not in _WORK_CHARACTER_TRAITS:
            result.add_error(f"{path}.trait", "trait は screening-axes.md の8特性 id のいずれかである")
        else:
            seen.append(trait)

        desire = preference.get("desire")
        if desire not in _DESIRE_LEVELS:
            result.add_error(f"{path}.desire", f"desire は {'/'.join(_DESIRE_LEVELS)} のいずれかである")
        elif desire == "must" and not _is_nonempty_str(preference.get("statement")):
            result.add_error(
                f"{path}.statement",
                "desire=must の特性には statement（本人の言葉での条件文）が必須である",
            )

    missing = [t for t in _WORK_CHARACTER_TRAITS if t not in seen]
    duplicated = sorted({t for t in seen if seen.count(t) > 1})
    if missing:
        result.add_error(
            "job_change_axis.work_character_preferences",
            f"8特性を過不足なく持つ必要がある。欠落: {', '.join(missing)}",
        )
    if duplicated:
        result.add_error(
            "job_change_axis.work_character_preferences",
            f"trait が重複している: {', '.join(duplicated)}",
        )


def _validate_v2_axis(profile: dict, result: ValidationResult) -> None:
    """schema_version 2.0 のときだけ効く追加検査。"""
    if schema_version_of(profile) != _V2_SCHEMA_VERSION:
        return
    axis = profile.get("job_change_axis")
    if not isinstance(axis, dict):
        return

    _validate_conditions(axis, result)
    _validate_work_character_preferences(axis, result)

    for legacy in ("must_conditions", "want_conditions"):
        if isinstance(axis.get(legacy), list) and axis[legacy]:
            result.add_warning(
                f"job_change_axis.{legacy}",
                f"{legacy} が残っている。2.0 では conditions[] へ移し、この配列は空にする",
            )


def _warn_v1_migration(profile: dict, result: ValidationResult) -> None:
    """v1 のプロファイルへ、v2 への移行を促す。"""
    if schema_version_of(profile) not in _V1_SCHEMA_VERSIONS:
        return
    result.add_warning(
        "schema_version",
        "schema_version 2.0 への移行を推奨する（8軸スクリーニングと作業特性の評価は 2.0 で働く）",
    )


def _warn_salary_floor_above_desired(profile: dict, result: ValidationResult) -> None:
    """v2: 譲れない年収下限が希望年収を上回っている。"""
    if schema_version_of(profile) != _V2_SCHEMA_VERSION:
        return
    axis = profile.get("job_change_axis")
    salary = profile.get("salary")
    if not isinstance(axis, dict) or not isinstance(salary, dict):
        return
    desired = salary.get("desired")
    if not isinstance(desired, (int, float)) or isinstance(desired, bool):
        return
    for condition in _must_conditions(axis):
        if condition.get("axis") != "salary_condition":
            continue
        value = condition.get("value")
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value > desired:
            result.add_warning(
                "job_change_axis.conditions",
                f"必須の年収下限（{value}）が希望年収（{desired}）を上回っている",
            )


def _warn_career_gaps_shape(profile: dict, result: ValidationResult) -> None:
    """W7: career_gaps[].period の形式不一致、または explanation の欠落・空。"""
    career_gaps = profile.get("career_gaps")
    if not isinstance(career_gaps, list):
        return
    for i, g in enumerate(career_gaps):
        path = f"career_gaps[{i}]"
        if not isinstance(g, dict):
            result.add_warning(path, "career_gaps の各要素はオブジェクトでなければならない")
            continue
        period = g.get("period")
        if not _is_nonempty_str(period) or _parse_period(period) is None:
            result.add_warning(
                f"{path}.period",
                "period が既定の形式（YYYY-MM〜YYYY-MM または YYYY-MM〜現在）と一致しないか、欠落している",
            )
        if not _is_nonempty_str(g.get("explanation")):
            result.add_warning(f"{path}.explanation", "explanation が欠落または空である")


def _warn_skills_portable_category(profile: dict, result: ValidationResult) -> None:
    """W8: skills.portable[].category が「対課題」「対人」以外である。"""
    skills = profile.get("skills")
    if not isinstance(skills, dict):
        return
    portable = skills.get("portable")
    if not isinstance(portable, list):
        return
    for i, item in enumerate(portable):
        category = item.get("category") if isinstance(item, dict) else None
        if category not in _PORTABLE_CATEGORIES:
            result.add_warning(
                f"skills.portable[{i}].category",
                f"category は「{_PORTABLE_CATEGORIES[0]}」または「{_PORTABLE_CATEGORIES[1]}」でなければならない",
            )


def validate(document: Any) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(document, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result

    if not _is_nonempty_str(document.get("schema_version")):
        result.add_error("schema_version", "schema_version は必須（非空）である")

    _validate_basic(document, result)
    _validate_career_history(document, result)
    _validate_job_change_axis(document, result)
    _validate_v2_axis(document, result)

    _warn_achievements(document, result)
    _warn_skills(document, result)
    _warn_targets(document, result)
    _warn_updated_at(document, result)

    _warn_schema_version_known(document, result)
    _warn_career_history_period_format(document, result)
    _warn_career_gaps(document, result)
    _warn_skills_languages_shape(document, result)
    _warn_salary_types(document, result)
    _warn_must_conditions_count(document, result)
    _warn_career_gaps_shape(document, result)
    _warn_skills_portable_category(document, result)
    _warn_v1_migration(document, result)
    _warn_salary_floor_above_desired(document, result)

    return result


def load_profile(path: str) -> Any:
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

    parser = argparse.ArgumentParser(description="job-change-support プロファイル検証ツール")
    parser.add_argument("profile_path", help="検証対象の profile.json ファイルパス")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    try:
        document = load_profile(args.profile_path)
    except (OSError, json.JSONDecodeError) as exc:
        result = ValidationResult()
        result.add_error(args.profile_path, f"JSON として読み込めない（{exc}）")
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
