"""job-change-job-search: job_search_results.json の決定的（非LLM）検証ツール。

標準ライブラリのみで、求人検索の成果物である job_search_results.json を機械検査する。
スキーマ（必須フィールド・型・列挙値・引用の存在）に加え、--profile を渡した場合は
PII リントを行い、利用者の現勤務先名・氏名らしき値・現年収（salary.current）が成果物へ
混入していないかを検出する。profile の読み取りはローカルに閉じ、外部へ送信しない。

CLI:
    python validate_job_search_results.py <job_search_results.json> [--json] [--profile <profile.json>]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any

VALID_MODES = {"fuzzy", "similar_better"}
# 企業スラッグの形式。原本は job-change-support の references/company-index-format.md にある。
# 任意の接頭辞（大文字1文字とアンダースコア）＋本体（英数字・ハイフン・日本語文字）。
_SLUG_RE = re.compile(
    r"^([A-Z]_)?"
    r"[0-9A-Za-z぀-ヿ㐀-鿿＀-￯]"
    r"[0-9A-Za-z぀-ヿ㐀-鿿＀-￯-]*$"
)

# 検索実行の識別子。成果物を置くディレクトリ名 {YYYYMMDD}-{条件の短いスラッグ} と同じ形式である。
_SEARCH_ID_RE = re.compile(r"^[0-9]{8}-[0-9a-z][0-9a-z-]*$")

_V1_SCHEMA_VERSION = "1.0"
_V2_SCHEMA_VERSION = "2.0"
_KNOWN_SCHEMA_VERSIONS = (_V1_SCHEMA_VERSION, _V2_SCHEMA_VERSION)

# 語彙の原本は job-change-support の references/screening-axes.md にある。
SCREENING_AXES = (
    "remote_certainty",
    "overtime_hours",
    "annual_holidays",
    "oncall_load",
    "hands_on_ratio",
    "coordination_ratio",
    "experience_distance",
    "salary_condition",
)
# 列挙で観測する軸と、その値域。語彙の原本は job-change-support の references/screening-axes.md にある。
AXIS_ENUM_VALUES = {
    "remote_certainty": ("guaranteed", "full_remote_possible", "hybrid", "onsite"),
    "oncall_load": ("none_stated", "exists"),
}
# 数値で観測する軸と、その値域 (下限, 上限)。上限が None なら上限を設けない。
# 単位は screening-axes.md にある（残業は月平均時間、年間休日は日／年、年収は円）。
AXIS_NUMERIC_RANGE = {
    "overtime_hours": (0, None),
    "annual_holidays": (0, None),
    "hands_on_ratio": (0.0, 1.0),
    "coordination_ratio": (0.0, 1.0),
    "salary_condition": (0, None),
}
# 年収下限は円単位である。これ未満は万円単位で書いた取り違えの疑いがあるため WARN にする。
_SALARY_CONDITION_WARN_BELOW = 10000
DUTY_CATEGORIES = {
    "build": "hands_on",
    "operate": "hands_on",
    "verify": "hands_on",
    "automate": "hands_on",
    "coordinate": "coordination",
    "manage": "coordination",
    "customer_facing": "coordination",
    "other": None,
}
_RATIO_AXES = ("hands_on_ratio", "coordination_ratio")
_MIN_DUTY_ITEMS_FOR_RATIO = 3
_RATIO_TOLERANCE = 0.01

JUDGEMENTS = ("meets", "not_meets", "unknown")
DECIDED_JUDGEMENTS = ("meets", "not_meets")
LEVELS = ("must", "want", "none")

CLASSIFICATIONS = ("apply_candidate", "needs_more_research", "excluded")
# 厳しい順。override は厳格化方向のみ許す。
_CLASSIFICATION_STRICTNESS = {"apply_candidate": 0, "needs_more_research": 1, "excluded": 2}
_MAX_UNKNOWN_FOR_APPLY = 4

RECOMMENDATIONS = ("応募推奨あり", "応募推奨なし", "判定不能")
AXES_SOURCES = ("job_change_axis.conditions", "degraded")
# 現年収の混入検出に用いる下限。これ未満の数値は誤検出を避けるため PII 項目に含めない。
_SALARY_MIN_FOR_LINT = 10000
# basic 配下で氏名を保持しうるキー。
_NAME_KEYS = ("name", "full_name", "氏名", "kana", "name_kana")


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


def _validate_conditions(document: dict, result: ValidationResult) -> None:
    conditions = document.get("conditions")
    if not isinstance(conditions, dict):
        result.add_error("conditions", "conditions はオブジェクトが必須である")
        return
    if not conditions:
        result.add_warning("conditions", "conditions が空である。検索条件を記録することを推奨する")


def _validate_baseline(document: dict, mode: str | None, result: ValidationResult) -> None:
    baseline = document.get("baseline")
    if baseline is None:
        if mode == "similar_better":
            result.add_warning(
                "baseline",
                "similar_better では基準求人（baseline）の記録を推奨する",
            )
        return
    if mode == "fuzzy":
        result.add_warning("baseline", "fuzzy では baseline は用いない")
    if not isinstance(baseline, dict):
        result.add_error("baseline", "baseline はオブジェクトでなければならない")
        return
    has_url = _is_nonempty_str(baseline.get("url"))
    slug = baseline.get("slug")
    has_slug = _is_nonempty_str(slug)
    if not has_url and not has_slug:
        result.add_error("baseline", "baseline は url または slug のいずれかを持たなければならない")
    if has_slug and not _SLUG_RE.match(slug):
        result.add_error(
            "baseline.slug",
            "slug は「任意の接頭辞（大文字1字＋_）＋本体（英数字・ハイフン・日本語文字）」で、"
            f"本体の先頭はハイフン不可・空白や記号は不可である（実値: {slug!r}）",
        )


def _validate_result_item(item: Any, index: int, mode: str | None, result: ValidationResult) -> None:
    path = f"results[{index}]"
    if not isinstance(item, dict):
        result.add_error(path, "results の各要素はオブジェクトでなければならない")
        return

    for key in ("title", "company_name", "source_site", "match_notes", "quote"):
        if not _is_nonempty_str(item.get(key)):
            result.add_error(f"{path}.{key}", f"{key} は必須（非空）である")

    url = item.get("url")
    if not isinstance(url, str) or not url.startswith("http"):
        result.add_error(
            f"{path}.url",
            f"url は http で始まる文字列でなければならない（実値: {url!r}）",
        )

    # 任意・null 許容の文字列フィールド。
    for key in ("salary_range", "location", "remote_policy"):
        if key in item and item[key] is not None and not isinstance(item[key], str):
            result.add_error(f"{path}.{key}", f"{key} は文字列または null でなければならない")

    # annual_holidays は数値・文字列・null を許容する（bool は不可）。
    if "annual_holidays" in item:
        ah = item["annual_holidays"]
        if ah is not None and (isinstance(ah, bool) or not isinstance(ah, (int, float, str))):
            result.add_error(
                f"{path}.annual_holidays",
                "annual_holidays は数値・文字列・null のいずれかでなければならない",
            )

    # better_points の型と、モードとの整合。
    better = item.get("better_points")
    if better is not None:
        if not isinstance(better, list):
            result.add_error(f"{path}.better_points", "better_points は配列でなければならない")
        else:
            for j, bp in enumerate(better):
                if not _is_nonempty_str(bp):
                    result.add_error(
                        f"{path}.better_points[{j}]",
                        "better_points の各要素は非空の文字列でなければならない",
                    )
            if mode == "fuzzy" and better:
                result.add_warning(
                    f"{path}.better_points",
                    "fuzzy では better_points は用いない（similar_better 専用）",
                )
    if mode == "similar_better" and not (isinstance(better, list) and better):
        result.add_warning(
            f"{path}.better_points",
            "similar_better では基準求人より改善している点（better_points）の記載を推奨する",
        )


def _duty_ratios(duty_items: Any) -> tuple[float, float] | None:
    """duty_items から (hands_on_ratio, coordination_ratio) を再計算する。

    件数が母数として足りない場合は None を返す。
    """
    if not isinstance(duty_items, list) or len(duty_items) < _MIN_DUTY_ITEMS_FOR_RATIO:
        return None
    hands_on = coordination = 0
    for item in duty_items:
        group = DUTY_CATEGORIES.get(item.get("category")) if isinstance(item, dict) else None
        if group == "hands_on":
            hands_on += 1
        elif group == "coordination":
            coordination += 1
    total = len(duty_items)
    return hands_on / total, coordination / total


def _validate_duty_items(item: dict, path: str, result: ValidationResult) -> None:
    duty_items = item.get("duty_items")
    if not isinstance(duty_items, list):
        result.add_error(f"{path}.duty_items", "duty_items は配列が必須である（記載が無ければ空配列）")
        return
    for j, duty in enumerate(duty_items):
        duty_path = f"{path}.duty_items[{j}]"
        if not isinstance(duty, dict):
            result.add_error(duty_path, "duty_items の各要素はオブジェクトでなければならない")
            continue
        if not _is_nonempty_str(duty.get("quote")):
            result.add_error(f"{duty_path}.quote", "quote は必須（非空）である。業務内容をそのまま写す")
        if duty.get("category") not in DUTY_CATEGORIES:
            result.add_error(
                f"{duty_path}.category",
                f"category は {'/'.join(DUTY_CATEGORIES)} のいずれかである",
            )


def _validate_axis_value(
    axis: str, observation: dict, obs_path: str, stated: bool, result: ValidationResult
) -> None:
    """観測1件の value を、軸ごとの型と値域に照らして検査する。"""
    value = observation.get("value")

    if axis == "experience_distance":
        # この軸だけは観測層で距離を決めない。value は null 固定で、要件の引用と職種大分類を持つ。
        if value is not None:
            result.add_error(
                f"{obs_path}.value",
                "experience_distance の観測は value を null 固定とする。距離は判定層で決める",
            )
        if not stated:
            return
        required = observation.get("required_experience")
        if not isinstance(required, list) or not all(_is_nonempty_str(q) for q in required):
            result.add_error(
                f"{obs_path}.required_experience",
                "required_experience は必須要件の引用文（非空の文字列）の配列である",
            )
        if not _is_nonempty_str(observation.get("job_family")):
            result.add_error(
                f"{obs_path}.job_family",
                "job_family は職種の大分類（非空の文字列）である",
            )
        return

    if value is None:
        return

    if axis in AXIS_ENUM_VALUES:
        if value not in AXIS_ENUM_VALUES[axis]:
            result.add_error(
                f"{obs_path}.value",
                f"value は {'/'.join(AXIS_ENUM_VALUES[axis])} のいずれかである（実値: {value!r}）",
            )
        return

    low, high = AXIS_NUMERIC_RANGE[axis]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        result.add_error(f"{obs_path}.value", f"value は数値でなければならない（実値: {value!r}）")
        return
    if value < low or (high is not None and value > high):
        upper = "上限なし" if high is None else str(high)
        result.add_error(
            f"{obs_path}.value",
            f"value は {low} 以上・{upper} の範囲でなければならない（実値: {value}）",
        )
        return
    if axis == "salary_condition" and value < _SALARY_CONDITION_WARN_BELOW:
        result.add_warning(
            f"{obs_path}.value",
            f"salary_condition は円単位である。{value} は万円単位で書いていないか確かめる",
        )


def _validate_axis_observations(item: dict, path: str, result: ValidationResult) -> dict[str, dict]:
    """axis_observations を検査し、軸 id をキーとする辞書を返す。"""
    observations = item.get("axis_observations")
    if not isinstance(observations, list):
        result.add_error(f"{path}.axis_observations", "axis_observations は配列が必須である")
        return {}

    by_axis: dict[str, dict] = {}
    seen: list[str] = []
    for j, observation in enumerate(observations):
        obs_path = f"{path}.axis_observations[{j}]"
        if not isinstance(observation, dict):
            result.add_error(obs_path, "axis_observations の各要素はオブジェクトでなければならない")
            continue
        axis = observation.get("axis")
        if axis not in SCREENING_AXES:
            result.add_error(f"{obs_path}.axis", "axis は screening-axes.md の8軸 id のいずれかである")
            continue
        seen.append(axis)
        by_axis.setdefault(axis, observation)

        stated = observation.get("stated")
        if not isinstance(stated, bool):
            result.add_error(f"{obs_path}.stated", "stated は真偽値が必須である")
            continue
        if "value" not in observation:
            result.add_error(f"{obs_path}.value", "value は必須である（記載が無ければ null）")
        if stated and not _is_nonempty_str(observation.get("quote")):
            result.add_error(
                f"{obs_path}.quote",
                "stated=true の観測には掲載ページからの引用（quote）が必須である",
            )
        if stated and observation.get("value") is None and not _is_nonempty_str(observation.get("value_text")):
            result.add_error(
                f"{obs_path}.value_text",
                "stated=true かつ value が null の場合、定性表現を value_text に写す",
            )
        _validate_axis_value(axis, observation, obs_path, stated, result)

    missing = [a for a in SCREENING_AXES if a not in seen]
    duplicated = sorted({a for a in seen if seen.count(a) > 1})
    if missing:
        result.add_error(f"{path}.axis_observations", f"8軸を過不足なく持つ必要がある。欠落: {', '.join(missing)}")
    if duplicated:
        result.add_error(f"{path}.axis_observations", f"axis が重複している: {', '.join(duplicated)}")

    # 比率2軸は duty_items から再計算して照合する。
    ratios = _duty_ratios(item.get("duty_items"))
    for index, axis in enumerate(_RATIO_AXES):
        observation = by_axis.get(axis)
        if not isinstance(observation, dict) or not isinstance(observation.get("stated"), bool):
            continue
        if observation["stated"] and ratios is None:
            result.add_error(
                f"{path}.axis_observations({axis})",
                f"duty_items が{_MIN_DUTY_ITEMS_FOR_RATIO}件未満のため比率を出せない。stated は false にする",
            )
            continue
        value = observation.get("value")
        if observation["stated"] and ratios is not None and isinstance(value, (int, float)) and not isinstance(value, bool):
            expected = ratios[index]
            if abs(value - expected) > _RATIO_TOLERANCE:
                result.add_error(
                    f"{path}.axis_observations({axis})",
                    f"duty_items から再計算した比率（{expected:.3f}）と value（{value}）が一致しない",
                )
    return by_axis


def _validate_axis_judgements(
    item: dict, path: str, observations: dict[str, dict], result: ValidationResult
) -> list[dict]:
    judgements = item.get("axis_judgements")
    if not isinstance(judgements, list):
        result.add_error(f"{path}.axis_judgements", "axis_judgements は配列が必須である")
        return []

    seen: list[str] = []
    valid: list[dict] = []
    for j, judgement in enumerate(judgements):
        j_path = f"{path}.axis_judgements[{j}]"
        if not isinstance(judgement, dict):
            result.add_error(j_path, "axis_judgements の各要素はオブジェクトでなければならない")
            continue
        axis = judgement.get("axis")
        if axis not in SCREENING_AXES:
            result.add_error(f"{j_path}.axis", "axis は screening-axes.md の8軸 id のいずれかである")
            continue
        seen.append(axis)
        valid.append(judgement)

        level = judgement.get("level")
        if level not in LEVELS:
            result.add_error(f"{j_path}.level", f"level は {'/'.join(LEVELS)} のいずれかである")
        verdict = judgement.get("judgement")
        if verdict not in JUDGEMENTS:
            result.add_error(f"{j_path}.judgement", f"judgement は {'/'.join(JUDGEMENTS)} のいずれかである")
        if level in ("must", "want") and not _is_nonempty_str(judgement.get("threshold_ref")):
            result.add_error(
                f"{j_path}.threshold_ref",
                "level が must・want の判定には、しきい値の出所（profile の条件 id または特性 id）が必須である",
            )
        if not _is_nonempty_str(judgement.get("rationale")):
            result.add_error(f"{j_path}.rationale", "rationale は必須（非空）である")

        observation = observations.get(axis)
        if not isinstance(observation, dict) or verdict not in DECIDED_JUDGEMENTS:
            continue
        if observation.get("stated") is False:
            result.add_error(
                f"{j_path}.judgement",
                "求人票に記載が無い軸（stated=false）を meets・not_meets と判定してはならない",
            )
        elif observation.get("value") is None:
            result.add_error(
                f"{j_path}.judgement",
                "観測値が null の軸（定性表現のみ）を meets・not_meets と判定してはならない",
            )

    missing = [a for a in SCREENING_AXES if a not in seen]
    duplicated = sorted({a for a in seen if seen.count(a) > 1})
    if missing:
        result.add_error(f"{path}.axis_judgements", f"8軸を過不足なく持つ必要がある。欠落: {', '.join(missing)}")
    if duplicated:
        result.add_error(f"{path}.axis_judgements", f"axis が重複している: {', '.join(duplicated)}")
    return valid


def derive_classification(judgements: list[dict]) -> str:
    """軸判定から分類を決定的に導く。判定表は job-search-format.md にある。"""
    must = [j for j in judgements if j.get("level") == "must"]
    if any(j.get("judgement") == "not_meets" for j in must):
        return "excluded"
    if any(j.get("judgement") == "unknown" for j in must):
        return "needs_more_research"
    if sum(1 for j in judgements if j.get("judgement") == "unknown") >= _MAX_UNKNOWN_FOR_APPLY:
        return "needs_more_research"
    return "apply_candidate"


def _validate_classification(item: dict, path: str, judgements: list[dict], result: ValidationResult) -> None:
    classification = item.get("classification")
    if classification not in CLASSIFICATIONS:
        result.add_error(
            f"{path}.classification",
            f"classification は {'/'.join(CLASSIFICATIONS)} のいずれかである",
        )
        return

    reasons = item.get("classification_reasons")
    if not isinstance(reasons, list) or not reasons:
        result.add_error(f"{path}.classification_reasons", "classification_reasons は1件以上必須である")
    else:
        for j, reason in enumerate(reasons):
            r_path = f"{path}.classification_reasons[{j}]"
            if not isinstance(reason, dict):
                result.add_error(r_path, "各要素はオブジェクトでなければならない")
                continue
            if reason.get("axis") not in SCREENING_AXES:
                result.add_error(f"{r_path}.axis", "axis は8軸 id のいずれかである")
            if not _is_nonempty_str(reason.get("reason")):
                result.add_error(f"{r_path}.reason", "reason は必須（非空）である")

    if len(judgements) != len(SCREENING_AXES):
        return  # 判定側が壊れている場合、導出結果との照合は行わない。

    derived = derive_classification(judgements)
    if classification == derived:
        return

    override = item.get("classification_override")
    if not isinstance(override, dict):
        result.add_error(
            f"{path}.classification",
            f"軸判定から導かれる分類は {derived} である。異なる分類にするには classification_override が要る",
        )
        return
    if override.get("from") != derived or override.get("to") != classification:
        result.add_error(
            f"{path}.classification_override",
            f"override の from・to が実際の分類と一致しない（導出: {derived} → 記載: {classification}）",
        )
    if not _is_nonempty_str(override.get("reason")):
        result.add_error(f"{path}.classification_override.reason", "reason は必須（非空）である")
    if _CLASSIFICATION_STRICTNESS[classification] < _CLASSIFICATION_STRICTNESS[derived]:
        result.add_error(
            f"{path}.classification_override",
            "override は分類を厳しくする方向にのみ許す（緩める方向は認めない）",
        )


def _validate_screening(document: dict, result: ValidationResult) -> None:
    screening = document.get("screening")
    if not isinstance(screening, dict):
        result.add_error("screening", "schema_version 2.0 では screening はオブジェクトが必須である")
        return

    if not _is_nonempty_str(screening.get("screened_at")):
        result.add_error("screening.screened_at", "screened_at は必須（非空）である")
    if not _is_nonempty_str(screening.get("profile_schema_version")):
        result.add_error(
            "screening.profile_schema_version",
            "判定に用いた profile の schema_version は必須である",
        )

    axes_source = screening.get("axes_source")
    if axes_source not in AXES_SOURCES:
        result.add_error("screening.axes_source", f"axes_source は {'/'.join(AXES_SOURCES)} のいずれかである")

    recommendation = screening.get("recommendation")
    if recommendation not in RECOMMENDATIONS:
        result.add_error("screening.recommendation", f"recommendation は {'/'.join(RECOMMENDATIONS)} のいずれかである")
    if not _is_nonempty_str(screening.get("rationale")):
        result.add_error("screening.rationale", "rationale は必須（非空）である")

    results = document.get("results")
    actual = {name: 0 for name in CLASSIFICATIONS}
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict) and item.get("classification") in actual:
                actual[item["classification"]] += 1

    counts = screening.get("counts")
    if not isinstance(counts, dict):
        result.add_error("screening.counts", "counts はオブジェクトが必須である")
    else:
        for name in CLASSIFICATIONS:
            if counts.get(name) != actual[name]:
                result.add_error(
                    f"screening.counts.{name}",
                    f"実際の集計（{actual[name]}件）と一致しない（記載: {counts.get(name)!r}）",
                )
        total = len(results) if isinstance(results, list) else None
        if counts.get("total") != total:
            result.add_error("screening.counts.total", f"results の件数（{total}）と一致しない")

    _validate_unmet_axis_summary(screening, results, result)
    _validate_current_employer_exclusion(screening, result)

    if recommendation in RECOMMENDATIONS:
        if axes_source == "degraded":
            if recommendation != "判定不能":
                result.add_error(
                    "screening.recommendation",
                    "axes_source が degraded のときの recommendation は「判定不能」だけである",
                )
        elif actual["apply_candidate"] >= 1 and recommendation != "応募推奨あり":
            result.add_error(
                "screening.recommendation",
                f"応募候補が{actual['apply_candidate']}件あるのに「応募推奨あり」でない",
            )
        elif actual["apply_candidate"] == 0 and recommendation != "応募推奨なし":
            result.add_error(
                "screening.recommendation",
                "応募候補が0件のときは「応募推奨なし」と明記する。無理に一押しを選ばない",
            )

    if isinstance(results, list) and results and actual["excluded"] == len(results):
        result.add_warning(
            "screening",
            "全件が除外候補である。必須条件が厳しすぎる可能性がある。profile の条件の見直しを促す",
        )


def _validate_unmet_axis_summary(screening: dict, results: Any, result: ValidationResult) -> None:
    summary = screening.get("unmet_axis_summary")
    if not isinstance(summary, list):
        result.add_error("screening.unmet_axis_summary", "unmet_axis_summary は配列が必須である")
        return

    actual: dict[str, dict[str, int]] = {a: {"not_meets": 0, "unknown": 0} for a in SCREENING_AXES}
    total_judgements = 0
    if isinstance(results, list):
        for item in results:
            judgements = item.get("axis_judgements") if isinstance(item, dict) else None
            if not isinstance(judgements, list):
                continue
            for judgement in judgements:
                if not isinstance(judgement, dict):
                    continue
                axis = judgement.get("axis")
                verdict = judgement.get("judgement")
                if axis in actual:
                    total_judgements += 1
                    if verdict in actual[axis]:
                        actual[axis][verdict] += 1

    seen = set()
    for i, entry in enumerate(summary):
        path = f"screening.unmet_axis_summary[{i}]"
        if not isinstance(entry, dict):
            result.add_error(path, "各要素はオブジェクトでなければならない")
            continue
        axis = entry.get("axis")
        if axis not in actual:
            result.add_error(f"{path}.axis", "axis は8軸 id のいずれかである")
            continue
        seen.add(axis)
        for key in ("not_meets", "unknown"):
            if entry.get(key) != actual[axis][key]:
                result.add_error(
                    f"{path}.{key}",
                    f"実際の集計（{actual[axis][key]}件）と一致しない（記載: {entry.get(key)!r}）",
                )

    missing = [a for a in SCREENING_AXES if a not in seen]
    if missing:
        result.add_error(
            "screening.unmet_axis_summary",
            f"8軸すべてを持つ必要がある。欠落: {', '.join(missing)}",
        )

    unknown_total = sum(v["unknown"] for v in actual.values())
    if total_judgements and unknown_total * 2 > total_judgements:
        result.add_warning(
            "screening.unmet_axis_summary",
            "判定の半数超が unknown である。求人票の情報密度が低い。検索経路の見直しを検討する",
        )


def _validate_current_employer_exclusion(screening: dict, result: ValidationResult) -> None:
    exclusion = screening.get("current_employer_exclusion")
    if not isinstance(exclusion, dict):
        result.add_error(
            "screening.current_employer_exclusion",
            "current_employer_exclusion はオブジェクトが必須である",
        )
        return
    performed = exclusion.get("performed")
    if not isinstance(performed, bool):
        result.add_error("screening.current_employer_exclusion.performed", "performed は真偽値が必須である")
        return
    count = exclusion.get("excluded_count")
    if performed and not (isinstance(count, int) and not isinstance(count, bool)):
        result.add_error(
            "screening.current_employer_exclusion.excluded_count",
            "除外を実施した場合、excluded_count は整数でなければならない",
        )
    if not performed and count is not None:
        result.add_error(
            "screening.current_employer_exclusion.excluded_count",
            "除外を実施していないのに件数を主張してはならない（未実施なら null にする）",
        )
    if not _is_nonempty_str(exclusion.get("method")):
        result.add_error(
            "screening.current_employer_exclusion.method",
            "method（除外の判定方法、または未実施の理由）は必須（非空）である",
        )


def _validate_v2_result_item(item: Any, index: int, result: ValidationResult) -> None:
    if not isinstance(item, dict):
        return
    path = f"results[{index}]"
    _validate_duty_items(item, path, result)
    observations = _validate_axis_observations(item, path, result)
    judgements = _validate_axis_judgements(item, path, observations, result)
    _validate_classification(item, path, judgements, result)


def _validate_threshold_refs(document: dict, profile: Any, result: ValidationResult) -> None:
    """--profile 指定時: threshold_ref の実在と level の一致を検査する。"""
    if not isinstance(profile, dict):
        return
    axis_block = profile.get("job_change_axis")
    if not isinstance(axis_block, dict):
        return

    levels: dict[str, str] = {}
    conditions = axis_block.get("conditions")
    if isinstance(conditions, list):
        for condition in conditions:
            if isinstance(condition, dict) and _is_nonempty_str(condition.get("id")):
                levels[condition["id"]] = condition.get("level", "")
    preferences = axis_block.get("work_character_preferences")
    if isinstance(preferences, list):
        for preference in preferences:
            if isinstance(preference, dict) and _is_nonempty_str(preference.get("trait")):
                desire = preference.get("desire")
                levels[preference["trait"]] = "must" if desire == "must" else "want"
    if not levels:
        return

    results = document.get("results")
    if not isinstance(results, list):
        return
    for i, item in enumerate(results):
        judgements = item.get("axis_judgements") if isinstance(item, dict) else None
        if not isinstance(judgements, list):
            continue
        for j, judgement in enumerate(judgements):
            if not isinstance(judgement, dict) or judgement.get("level") not in ("must", "want"):
                continue
            ref = judgement.get("threshold_ref")
            path = f"results[{i}].axis_judgements[{j}].threshold_ref"
            if not _is_nonempty_str(ref):
                continue
            if ref not in levels:
                result.add_error(path, f"profile に存在しない条件・特性を参照している: {ref}")
            elif levels[ref] != judgement.get("level"):
                result.add_error(
                    path,
                    f"profile での必須度（{levels[ref]}）と level（{judgement.get('level')}）が一致しない",
                )


def validate(
    document: Any,
    pii_terms: list[tuple[str, str]] | None = None,
    profile: Any = None,
) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(document, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result

    version = document.get("schema_version")
    if not _is_nonempty_str(version):
        result.add_error("schema_version", "schema_version は必須（非空）である")
    elif version not in _KNOWN_SCHEMA_VERSIONS:
        result.add_warning(
            "schema_version",
            f"schema_version が既知のバージョン（{'/'.join(_KNOWN_SCHEMA_VERSIONS)}）ではない（実値: {version!r}）",
        )

    search_id = document.get("search_id")
    if not _is_nonempty_str(search_id):
        result.add_error("search_id", "search_id は必須（非空）である。成果物を置くディレクトリ名と同じ値を書く")
    elif not _SEARCH_ID_RE.match(search_id):
        result.add_error(
            "search_id",
            "search_id は「実行日8桁（YYYYMMDD）＋ハイフン＋条件の短いスラッグ（英小文字・数字・ハイフン）」"
            f"でなければならない（実値: {search_id!r}）",
        )

    mode = document.get("mode")
    valid_mode: str | None = None
    if not _is_nonempty_str(mode):
        result.add_error("mode", "mode は必須（非空）である")
    elif mode not in VALID_MODES:
        result.add_error("mode", f"mode は fuzzy・similar_better のいずれかでなければならない（実値: {mode!r}）")
    else:
        valid_mode = mode

    if not _is_nonempty_str(document.get("executed_at")):
        result.add_error("executed_at", "executed_at は必須（非空）である")

    _validate_conditions(document, result)
    _validate_baseline(document, valid_mode, result)

    results = document.get("results")
    if not isinstance(results, list):
        result.add_error("results", "results は配列でなければならない")
    elif not results:
        result.add_warning(
            "results",
            "results が空である。取得できなかった事情は coverage_notes に記すことを推奨する",
        )
    else:
        for i, item in enumerate(results):
            _validate_result_item(item, i, valid_mode, result)

    if version == _V2_SCHEMA_VERSION:
        if isinstance(results, list):
            for i, item in enumerate(results):
                _validate_v2_result_item(item, i, result)
        _validate_screening(document, result)
        if profile is not None:
            _validate_threshold_refs(document, profile, result)

    if pii_terms is None:
        result.add_warning(
            "(root)",
            "--profile が指定されていない。PII リントとしきい値の突き合わせは未実施である",
        )
    else:
        _run_pii_lint(document, pii_terms, result)

    return result


def _run_pii_lint(
    document: dict, pii_terms: list[tuple[str, str]], result: ValidationResult
) -> None:
    """成果物 JSON 全体を文字列化し、profile 由来の PII に当たる文字列が混入していないか検査する。"""
    blob = json.dumps(document, ensure_ascii=False)
    for label, value in pii_terms:
        if value and value in blob:
            result.add_error(
                "(pii)",
                f"profile 由来の{label}「{value}」が成果物に混入している。"
                "匿名化してから保存すること",
            )


def collect_pii_terms(profile: Any) -> list[tuple[str, str]]:
    """profile.json から PII 混入検査に用いる (ラベル, 値) の一覧を抽出する（純粋関数）。

    抽出対象: 現勤務先名（career_history のうち在職中〈〜現在〉のエントリの company。
    在職中が特定できない場合は先頭エントリの company）・氏名らしき値（basic 内）・
    現年収（salary.current）。
    """
    terms: list[tuple[str, str]] = []
    if not isinstance(profile, dict):
        return terms

    # 現勤務先名。
    career = profile.get("career_history")
    if isinstance(career, list):
        ongoing: list[str] = []
        for entry in career:
            if not isinstance(entry, dict):
                continue
            company = entry.get("company")
            period = entry.get("period")
            if _is_nonempty_str(company) and isinstance(period, str) and period.rstrip().endswith("現在"):
                ongoing.append(company.strip())
        if ongoing:
            for company in ongoing:
                terms.append(("現勤務先名", company))
        else:
            # 在職中を特定できない場合は先頭（新しい順の慣行）を現勤務先とみなす。
            for entry in career:
                if isinstance(entry, dict) and _is_nonempty_str(entry.get("company")):
                    terms.append(("現勤務先名", entry["company"].strip()))
                    break

    # 氏名らしき値。
    basic = profile.get("basic")
    if isinstance(basic, dict):
        for key in _NAME_KEYS:
            value = basic.get(key)
            if _is_nonempty_str(value):
                terms.append(("氏名", value.strip()))

    # 現年収。
    salary = profile.get("salary")
    if isinstance(salary, dict):
        current = salary.get("current")
        if isinstance(current, bool):
            pass
        elif isinstance(current, int) and current >= _SALARY_MIN_FOR_LINT:
            terms.append(("現年収", str(current)))
        elif isinstance(current, float) and current >= _SALARY_MIN_FOR_LINT:
            terms.append(("現年収", str(int(current)) if current.is_integer() else str(current)))

    return terms


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

    parser = argparse.ArgumentParser(description="job-change-job-search 求人検索結果検証ツール")
    parser.add_argument("results_path", help="検証対象の job_search_results.json ファイルパス")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    parser.add_argument(
        "--profile",
        help="PII リント用の profile.json パス（ローカルでのみ読み取り、外部送信しない）",
    )
    args = parser.parse_args(argv)

    try:
        document = load_json(args.results_path)
    except (OSError, json.JSONDecodeError) as exc:
        result = ValidationResult()
        result.add_error(args.results_path, f"JSON として読み込めない（{exc}）")
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(format_report(result))
        return 1

    pii_terms: list[tuple[str, str]] | None = None
    profile: Any = None
    if args.profile:
        try:
            profile = load_json(args.profile)
        except (OSError, json.JSONDecodeError) as exc:
            result = ValidationResult()
            result.add_error(args.profile, f"profile.json を読み込めない（{exc}）")
            if args.json:
                print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(format_report(result))
            return 1
        pii_terms = collect_pii_terms(profile)

    result = validate(document, pii_terms=pii_terms, profile=profile)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(result))

    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
