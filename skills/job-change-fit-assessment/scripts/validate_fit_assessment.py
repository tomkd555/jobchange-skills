"""job-change-fit-assessment: 適合性評価（fit_assessment.json）の決定的（非LLM）検証ツール。

標準ライブラリのみで、適合性評価の原本である fit_assessment.json を機械検査する。
7次元（experience_proximity / aspiration_alignment / work_character_fit /
condition_fit / culture_fit / compensation_fit / time_fit。schema_version 1.0 は
skill_fit を含む5次元）の
評価・must 条件の判定・総合判定が、仕様の構造要件を満たすかを、ERROR（成立しない
欠落・不正値）と WARN（成立するが質を下げる点）に分けて報告する。フィールド仕様と
検証規則の原本は references/fit-format.md、判定基準の原本は references/fit-criteria.md
である。

CLI:
    python validate_fit_assessment.py <fit_assessment.json> [--json]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any

_V1_SCHEMA_VERSION = "1.0"
_V2_SCHEMA_VERSION = "2.0"
_KNOWN_SCHEMA_VERSIONS = (_V1_SCHEMA_VERSION, _V2_SCHEMA_VERSION)

_V1_DIMENSION_IDS = ("skill_fit", "condition_fit", "culture_fit", "compensation_fit", "time_fit")
_V2_DIMENSION_IDS = (
    "experience_proximity",
    "aspiration_alignment",
    "work_character_fit",
    "condition_fit",
    "culture_fit",
    "compensation_fit",
    "time_fit",
)
_V1_EVIDENCE_SOURCES = ("company_research", "job_posting", "profile", "self_analysis", "time_analysis")
_V2_EVIDENCE_SOURCES = _V1_EVIDENCE_SOURCES + ("job_search_screening",)
_MET_VALUES = ("yes", "no", "unknown")
_RECOMMENDATIONS = ("推奨", "条件付き推奨", "非推奨", "判断保留")
_V1_INPUT_KEYS = ("job_posting", "company_research", "self_analysis", "time_analysis")
_V2_INPUT_KEYS = _V1_INPUT_KEYS + ("job_search_screening",)

# スキルギャップの3段階（none を含めて5値）。厳しい順の重みを持つ。
_GAP_LEVELS = {
    "none": 0,
    "complementable_within_3m": 1,
    "needs_6_12m_study": 2,
    "not_applicable_now": 3,
}
_GAP_VALUES = tuple(_GAP_LEVELS) + ("unknown",)
_GAP_ITEM_LEVELS = tuple(k for k in _GAP_LEVELS if k != "none")
# 企業スコアの語彙。原本は job-change-company-research の references/company-score-rubric.md、
# 総合点の算出は scripts/calculate_company_score.py。
_SCORE_KINDS = ("quantitative", "qualitative")
# 企業スラッグの形式。原本は job-change-support の references/company-index-format.md にある。
# 任意の接頭辞（大文字1文字とアンダースコア）＋本体（英数字・ハイフン・日本語文字）。
_SLUG_RE = re.compile(
    r"^([A-Z]_)?"
    r"[0-9A-Za-z぀-ヿ㐀-鿿＀-￯]"
    r"[0-9A-Za-z぀-ヿ㐀-鿿＀-￯-]*$"
)
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _schema_version(document: Any) -> str:
    """document の schema_version を返す。取得できない場合は空文字を返す。"""
    if not isinstance(document, dict):
        return ""
    version = document.get("schema_version")
    return version if isinstance(version, str) else ""


def _is_v2(document: Any) -> bool:
    return _schema_version(document) == _V2_SCHEMA_VERSION


def _dimension_ids(document: Any) -> tuple[str, ...]:
    return _V2_DIMENSION_IDS if _is_v2(document) else _V1_DIMENSION_IDS


def _input_keys(document: Any) -> tuple[str, ...]:
    return _V2_INPUT_KEYS if _is_v2(document) else _V1_INPUT_KEYS


def _evidence_sources(version: str) -> tuple[str, ...]:
    return _V2_EVIDENCE_SOURCES if version == _V2_SCHEMA_VERSION else _V1_EVIDENCE_SOURCES


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


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_top_level(document: dict, result: ValidationResult) -> None:
    if not _is_nonempty_str(document.get("schema_version")):
        result.add_error("schema_version", "schema_version は必須（非空）である")
    else:
        version = document["schema_version"]
        if version not in _KNOWN_SCHEMA_VERSIONS:
            result.add_warning(
                "schema_version",
                f"schema_version が既知のバージョン（{'/'.join(_KNOWN_SCHEMA_VERSIONS)}）ではない",
            )

    slug = document.get("slug")
    if not _is_nonempty_str(slug):
        result.add_error("slug", "slug は必須（非空）である")
    elif not _SLUG_RE.match(slug):
        result.add_error(
            "slug",
            "slug は「任意の接頭辞（大文字1字＋_）＋本体（英数字・ハイフン・日本語文字）」で、"
            "本体の先頭はハイフン不可・空白や記号は不可である",
        )

    assessed_at = document.get("assessed_at")
    if not _is_nonempty_str(assessed_at):
        result.add_error("assessed_at", "assessed_at は必須（非空）である")
    elif not _DATE_RE.match(assessed_at):
        result.add_warning("assessed_at", "assessed_at が YYYY-MM-DD の形式と一致しない")


def _validate_inputs(document: dict, result: ValidationResult) -> None:
    input_keys = _input_keys(document)
    inputs = document.get("inputs")
    if not isinstance(inputs, dict):
        result.add_error("inputs", "inputs はオブジェクトが必須である")
        return
    for key in input_keys:
        if key not in inputs:
            result.add_error(f"inputs.{key}", f"{key} は必須である")
        elif not isinstance(inputs[key], bool):
            result.add_error(f"inputs.{key}", f"{key} は真偽値でなければならない")
    if all(inputs.get(k) is False for k in input_keys):
        result.add_warning(
            "inputs",
            "入力が1つも存在しない（全て false）。評価の根拠が乏しく質を下げる",
        )


def _validate_evidence_list(
    evidence: Any,
    path: str,
    result: ValidationResult,
    *,
    require_nonempty: bool,
    version: str = _V1_SCHEMA_VERSION,
) -> None:
    """evidence 配列を検証する。source 不正は ERROR、ref 欠落は WARN。"""
    evidence_sources = _evidence_sources(version)
    if not isinstance(evidence, list):
        result.add_error(path, "evidence は配列でなければならない")
        return
    if require_nonempty and not evidence:
        result.add_error(path, "evidence は1件以上必要である")
        return
    for i, ev in enumerate(evidence):
        ev_path = f"{path}[{i}]"
        if not isinstance(ev, dict):
            result.add_error(ev_path, "evidence の各要素はオブジェクトでなければならない")
            continue
        source = ev.get("source")
        if source not in evidence_sources:
            result.add_error(
                f"{ev_path}.source",
                f"source は {'/'.join(evidence_sources)} のいずれかでなければならない",
            )
        if not _is_nonempty_str(ev.get("ref")):
            result.add_warning(f"{ev_path}.ref", "ref（参照子）が欠落または空である")


def _validate_dimensions(document: dict, result: ValidationResult) -> None:
    version = _schema_version(document)
    dimension_ids = _dimension_ids(document)
    dimensions = document.get("dimensions")
    if not isinstance(dimensions, list):
        result.add_error("dimensions", "dimensions は配列が必須である")
        return

    seen_ids: list[str] = []
    for i, dim in enumerate(dimensions):
        path = f"dimensions[{i}]"
        if not isinstance(dim, dict):
            result.add_error(path, "dimensions の各要素はオブジェクトでなければならない")
            continue

        dim_id = dim.get("id")
        if dim_id in dimension_ids:
            seen_ids.append(dim_id)
        # id の過不足検査は下でまとめて行う（未知 id もそこで ERROR）

        score = dim.get("score")
        if score is None:
            result.add_warning(f"{path}.score", "score が null（判断保留）である")
        elif not _is_int(score) or not (1 <= score <= 5):
            result.add_error(f"{path}.score", "score は 1〜5 の整数または null でなければならない")

        if not _is_nonempty_str(dim.get("verdict")):
            result.add_error(f"{path}.verdict", "verdict は必須（非空）である")

        _validate_evidence_list(
            dim.get("evidence"),
            f"{path}.evidence",
            result,
            require_nonempty=True,
            version=version,
        )

    present = set(seen_ids)
    missing = [d for d in dimension_ids if d not in present]
    for d in missing:
        result.add_error("dimensions", f"必須の次元 id「{d}」が存在しない")

    duplicates = [d for d in dimension_ids if seen_ids.count(d) > 1]
    for d in duplicates:
        result.add_error("dimensions", f"次元 id「{d}」が重複している")

    for i, dim in enumerate(dimensions):
        if isinstance(dim, dict) and dim.get("id") not in dimension_ids:
            result.add_error(
                f"dimensions[{i}].id",
                f"id は {'/'.join(dimension_ids)} のいずれかでなければならない",
            )


def _validate_must_conditions(document: dict, result: ValidationResult) -> None:
    version = _schema_version(document)
    must_results = document.get("must_condition_results")
    if not isinstance(must_results, list):
        result.add_error("must_condition_results", "must_condition_results は配列が必須である")
        return
    for i, mc in enumerate(must_results):
        path = f"must_condition_results[{i}]"
        if not isinstance(mc, dict):
            result.add_error(path, "must_condition_results の各要素はオブジェクトでなければならない")
            continue
        if not _is_nonempty_str(mc.get("condition")):
            result.add_error(f"{path}.condition", "condition は必須（非空）である")
        met = mc.get("met")
        if met not in _MET_VALUES:
            result.add_error(
                f"{path}.met",
                f"met は {'/'.join(_MET_VALUES)} のいずれかでなければならない",
            )
        # met が yes/no の断定には evidence を要する。unknown は evidence 空を許容する。
        require_nonempty = met in ("yes", "no")
        _validate_evidence_list(
            mc.get("evidence"),
            f"{path}.evidence",
            result,
            require_nonempty=require_nonempty,
            version=version,
        )


def _validate_overall(document: dict, result: ValidationResult) -> None:
    overall = document.get("overall")
    if not isinstance(overall, dict):
        result.add_error("overall", "overall はオブジェクトが必須である")
        return
    recommendation = overall.get("recommendation")
    if recommendation not in _RECOMMENDATIONS:
        result.add_error(
            "overall.recommendation",
            f"recommendation は {'/'.join(_RECOMMENDATIONS)} のいずれかでなければならない",
        )
    if not _is_nonempty_str(overall.get("rationale")):
        result.add_error("overall.rationale", "rationale は必須（非空）である")
    open_questions = overall.get("open_questions")
    if not isinstance(open_questions, list):
        result.add_error("overall.open_questions", "open_questions は配列でなければならない")


def _validate_company_score(document: dict, result: ValidationResult) -> None:
    """任意フィールド company_score（企業スコアの総合点と軸ごとの内訳）を検査する。

    無ければ検査しない（PASS）。total が null のときと provisional が true のときは、
    総合点を単独では読めないことを WARN で示す。
    """
    if "company_score" not in document:
        return
    score = document.get("company_score")
    if not isinstance(score, dict):
        result.add_error("company_score", "company_score はオブジェクトでなければならない")
        return

    total = score.get("total")
    if total is None:
        result.add_warning(
            "company_score.total",
            "判定できた軸が無く総合点を算出できていない。実測値と基準を補って算出し直す",
        )
    elif not _is_int(total) or not (0 <= total <= 100):
        result.add_error(
            "company_score.total", "total は 0〜100 の整数または null でなければならない"
        )

    coverage = score.get("coverage")
    if not _is_int(coverage) or not (0 <= coverage <= 100):
        result.add_error("company_score.coverage", "coverage は 0〜100 の整数でなければならない")

    provisional = score.get("provisional")
    if not isinstance(provisional, bool):
        result.add_error("company_score.provisional", "provisional は真偽値でなければならない")
    elif provisional:
        result.add_warning(
            "company_score.provisional",
            "判定できた軸の重みの合計が足りず暫定の点数である。少数の軸に引きずられる点を報告へ添える",
        )

    axes = score.get("axes")
    if not isinstance(axes, list):
        result.add_error("company_score.axes", "axes は配列でなければならない")
    else:
        for i, entry in enumerate(axes):
            path = f"company_score.axes[{i}]"
            if not isinstance(entry, dict):
                result.add_error(path, "axes の各要素はオブジェクトでなければならない")
                continue
            if not _is_nonempty_str(entry.get("axis")):
                result.add_error(f"{path}.axis", "axis は必須（非空）である")
            if entry.get("kind") not in _SCORE_KINDS:
                result.add_error(
                    f"{path}.kind",
                    f"kind は {'/'.join(_SCORE_KINDS)} のいずれかでなければならない",
                )
            weight = entry.get("weight")
            if not _is_int(weight) or not (1 <= weight <= 100):
                result.add_error(f"{path}.weight", "weight は 1〜100 の整数でなければならない")
            axis_score = entry.get("score")
            if axis_score is not None and (
                not _is_int(axis_score) or not (0 <= axis_score <= 100)
            ):
                result.add_error(
                    f"{path}.score", "score は 0〜100 の整数または null でなければならない"
                )

    if not _is_nonempty_str(score.get("rationale")):
        result.add_error("company_score.rationale", "rationale は必須（非空）である")


def _warn_recommendation_consistency(document: dict, result: ValidationResult) -> None:
    """W: must 条件に met=no があるのに recommendation が「推奨」である（1.0 のみ）。

    2.0 では同じ整合を ERROR として扱う（_validate_v2_recommendation）。
    """
    if _is_v2(document):
        return
    overall = document.get("overall")
    must_results = document.get("must_condition_results")
    if not isinstance(overall, dict) or not isinstance(must_results, list):
        return
    if overall.get("recommendation") != "推奨":
        return
    has_unmet = any(
        isinstance(mc, dict) and mc.get("met") == "no" for mc in must_results
    )
    if has_unmet:
        result.add_warning(
            "overall.recommendation",
            "満たさない must 条件（met=no）があるのに recommendation が「推奨」である。"
            "「条件付き推奨」または「非推奨」の妥当性を確認する",
        )


def _dimension_by_id(document: dict, dimension_id: str) -> dict | None:
    dimensions = document.get("dimensions")
    if not isinstance(dimensions, list):
        return None
    for dim in dimensions:
        if isinstance(dim, dict) and dim.get("id") == dimension_id:
            return dim
    return None


def _validate_skill_gap(document: dict, result: ValidationResult) -> None:
    """2.0: experience_proximity のスキルギャップ3段階を検査する。"""
    dimension = _dimension_by_id(document, "experience_proximity")
    if dimension is None:
        return
    path = "dimensions(experience_proximity)"

    gap = dimension.get("skill_gap")
    if gap not in _GAP_VALUES:
        result.add_error(f"{path}.skill_gap", f"skill_gap は {'/'.join(_GAP_VALUES)} のいずれかである")

    items = dimension.get("skill_gap_items")
    if not isinstance(items, list):
        result.add_error(f"{path}.skill_gap_items", "skill_gap_items は配列が必須である（無ければ空配列）")
        return

    levels: list[str] = []
    for i, item in enumerate(items):
        item_path = f"{path}.skill_gap_items[{i}]"
        if not isinstance(item, dict):
            result.add_error(item_path, "各要素はオブジェクトでなければならない")
            continue
        if not _is_nonempty_str(item.get("requirement")):
            result.add_error(f"{item_path}.requirement", "requirement は必須（非空）である。要件をそのまま写す")
        level = item.get("gap_level")
        if level not in _GAP_ITEM_LEVELS:
            result.add_error(
                f"{item_path}.gap_level",
                f"gap_level は {'/'.join(_GAP_ITEM_LEVELS)} のいずれかである",
            )
        else:
            levels.append(level)
        if not _is_nonempty_str(item.get("basis")):
            result.add_error(f"{item_path}.basis", "basis（段階を分けた根拠）は必須（非空）である")
        _validate_evidence_list(
            item.get("evidence"),
            f"{item_path}.evidence",
            result,
            require_nonempty=True,
            version=_V2_SCHEMA_VERSION,
        )

    if gap not in _GAP_LEVELS:
        return  # unknown・不正値のときは内訳との整合を問わない。
    expected = max((_GAP_LEVELS[level] for level in levels), default=_GAP_LEVELS["none"])
    if _GAP_LEVELS[gap] != expected:
        name = next(k for k, v in _GAP_LEVELS.items() if v == expected)
        result.add_error(
            f"{path}.skill_gap",
            f"skill_gap は内訳（skill_gap_items）の最も重い段階と一致させる（内訳から: {name}／記載: {gap}）",
        )


def _validate_v2_must_conditions(document: dict, profile: Any, result: ValidationResult) -> None:
    """2.0: must_condition_results の ref・negotiable と、profile との1対1を検査する。"""
    must_results = document.get("must_condition_results")
    if not isinstance(must_results, list):
        return

    refs: list[str] = []
    for i, mc in enumerate(must_results):
        path = f"must_condition_results[{i}]"
        if not isinstance(mc, dict):
            continue
        ref = mc.get("ref")
        if not _is_nonempty_str(ref):
            result.add_error(f"{path}.ref", "ref（profile の条件 id または特性 id）は必須（非空）である")
        else:
            refs.append(ref)
        negotiable = mc.get("negotiable")
        if negotiable is not None and not isinstance(negotiable, bool):
            result.add_error(f"{path}.negotiable", "negotiable は真偽値または省略である")
        elif negotiable is True:
            evidence = mc.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                result.add_error(
                    f"{path}.evidence",
                    "negotiable=true には根拠が要る（無根拠に交渉可能とみなさない）",
                )

    duplicated = sorted({r for r in refs if refs.count(r) > 1})
    if duplicated:
        result.add_error("must_condition_results", f"ref が重複している: {', '.join(duplicated)}")

    if profile is None:
        result.add_warning(
            "must_condition_results",
            "--profile が指定されていない。profile の必須条件との1対1は未検証である",
        )
        return

    expected = _profile_must_refs(profile)
    if expected is None:
        return
    missing = sorted(expected - set(refs))
    extra = sorted(set(refs) - expected)
    if missing:
        result.add_error(
            "must_condition_results",
            f"profile の必須条件に対応する判定が無い: {', '.join(missing)}",
        )
    if extra:
        result.add_error(
            "must_condition_results",
            f"profile に存在しない必須条件を判定している: {', '.join(extra)}",
        )


def _profile_must_refs(profile: Any) -> set[str] | None:
    """profile.json から必須条件の id 集合を取り出す。2.0 でなければ None を返す。"""
    if not isinstance(profile, dict) or profile.get("schema_version") != "2.0":
        return None
    axis = profile.get("job_change_axis")
    if not isinstance(axis, dict):
        return None
    refs: set[str] = set()
    conditions = axis.get("conditions")
    if isinstance(conditions, list):
        for condition in conditions:
            if isinstance(condition, dict) and condition.get("level") == "must":
                if _is_nonempty_str(condition.get("id")):
                    refs.add(condition["id"])
    preferences = axis.get("work_character_preferences")
    if isinstance(preferences, list):
        for preference in preferences:
            if isinstance(preference, dict) and preference.get("desire") == "must":
                if _is_nonempty_str(preference.get("trait")):
                    refs.add(preference["trait"])
    return refs


def _validate_v2_recommendation(document: dict, result: ValidationResult) -> None:
    """2.0: must 違反・応募困難と総合判定の整合を ERROR として検査する。"""
    overall = document.get("overall")
    must_results = document.get("must_condition_results")
    if not isinstance(overall, dict):
        return
    recommendation = overall.get("recommendation")

    unmet = [
        mc for mc in must_results
        if isinstance(mc, dict) and mc.get("met") == "no"
    ] if isinstance(must_results, list) else []

    if unmet:
        if recommendation == "推奨":
            result.add_error(
                "overall.recommendation",
                "満たさない必須条件があるのに「推奨」としている。「条件付き推奨」または「非推奨」にする",
            )
        elif recommendation == "条件付き推奨":
            blocking = [mc for mc in unmet if mc.get("negotiable") is not True]
            if blocking:
                result.add_error(
                    "overall.recommendation",
                    "交渉で解消できない必須条件（negotiable が true でない met=no）が残るのに"
                    "「条件付き推奨」としている。「非推奨」にする",
                )

    dimension = _dimension_by_id(document, "experience_proximity")
    if isinstance(dimension, dict) and dimension.get("skill_gap") == "not_applicable_now":
        if recommendation in ("推奨", "条件付き推奨"):
            result.add_error(
                "overall.recommendation",
                "skill_gap が not_applicable_now（現時点では応募困難）なのに応募を勧めている",
            )

    inputs = document.get("inputs")
    if isinstance(inputs, dict):
        false_count = sum(1 for k in _V2_INPUT_KEYS if inputs.get(k) is False)
        if false_count >= 3 and recommendation == "推奨":
            result.add_warning(
                "overall.recommendation",
                "入力の3つ以上が false なのに「推奨」としている。判断材料が乏しい",
            )


def _validate_aspiration_alignment(document: dict, result: ValidationResult) -> None:
    """2.0: 志向の一致が、自己分析・profile の材料に対応づいているかを検査する。"""
    dimension = _dimension_by_id(document, "aspiration_alignment")
    if not isinstance(dimension, dict):
        return
    path = "dimensions(aspiration_alignment)"
    score = dimension.get("score")
    if score is None:
        return

    inputs = document.get("inputs")
    has_self_analysis = isinstance(inputs, dict) and inputs.get("self_analysis") is True
    if not has_self_analysis and _is_int(score) and score >= 4:
        result.add_error(
            f"{path}.score",
            "自己分析が無い（inputs.self_analysis=false）のに志向の一致を高く評価している",
        )

    evidence = dimension.get("evidence")
    sources = {ev.get("source") for ev in evidence if isinstance(ev, dict)} if isinstance(evidence, list) else set()
    if not sources & {"self_analysis", "profile"}:
        result.add_error(
            f"{path}.evidence",
            "志向の一致には self_analysis または profile を根拠に含める（求人票だけで志向を断定しない）",
        )
    if not has_self_analysis:
        result.add_warning(
            f"{path}",
            "自己分析が無いため志向の根拠が弱い。job-change-self-analysis の実施を促す",
        )


def validate(document: Any, profile: Any = None, screening: Any = None) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(document, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result

    _validate_top_level(document, result)
    _validate_inputs(document, result)
    _validate_dimensions(document, result)
    _validate_must_conditions(document, result)
    _validate_overall(document, result)
    _validate_company_score(document, result)

    _warn_recommendation_consistency(document, result)

    if _is_v2(document):
        _validate_skill_gap(document, result)
        _validate_v2_must_conditions(document, profile, result)
        _validate_v2_recommendation(document, result)
        _validate_aspiration_alignment(document, result)
        _warn_screening_divergence(document, screening, result)

    return result


def _warn_screening_divergence(document: dict, screening: Any, result: ValidationResult) -> None:
    """2.0: 求人検索のスクリーニングと適合性評価で判定が変わった軸を報告する。"""
    if not isinstance(screening, dict):
        return
    source = document.get("screening_source")
    if not isinstance(source, dict):
        return
    index = source.get("result_index")
    results = screening.get("results")
    if not _is_int(index) or not isinstance(results, list) or not (0 <= index < len(results)):
        result.add_warning(
            "screening_source.result_index",
            "求人検索の結果を参照できない（result_index が範囲外である）",
        )
        return

    item = results[index]
    judgements = item.get("axis_judgements") if isinstance(item, dict) else None
    if not isinstance(judgements, list):
        return
    met_axes = {
        j.get("axis")
        for j in judgements
        if isinstance(j, dict) and j.get("level") == "must" and j.get("judgement") == "meets"
    }
    if not met_axes:
        return

    must_results = document.get("must_condition_results")
    if not isinstance(must_results, list):
        return
    if any(isinstance(mc, dict) and mc.get("met") == "no" for mc in must_results):
        result.add_warning(
            "must_condition_results",
            "求人検索では必須条件を満たすと判定した求人が、求人票の取込後に met=no となっている。"
            "変わった軸を overall.open_questions に記録する",
        )


def load_fit_assessment(path: str) -> Any:
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

    parser = argparse.ArgumentParser(description="job-change-fit-assessment 適合性評価検証ツール")
    parser.add_argument("fit_assessment_path", help="検証対象の fit_assessment.json ファイルパス")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    parser.add_argument(
        "--profile",
        help="profile.json のパス。必須条件との1対1を検査する（ローカル読み取りのみ）",
    )
    parser.add_argument(
        "--screening",
        help="job_search_results.json のパス。スクリーニング時との判定の食い違いを報告する",
    )
    args = parser.parse_args(argv)

    def _load(path: str, label: str) -> tuple[Any, ValidationResult | None]:
        try:
            return load_fit_assessment(path), None
        except (OSError, json.JSONDecodeError) as exc:
            failure = ValidationResult()
            failure.add_error(path, f"{label}を読み込めない（{exc}）")
            return None, failure

    document, failure = _load(args.fit_assessment_path, "fit_assessment.json")
    profile = screening = None
    if failure is None and args.profile:
        profile, failure = _load(args.profile, "profile.json")
    if failure is None and args.screening:
        screening, failure = _load(args.screening, "job_search_results.json")
    if failure is not None:
        if args.json:
            print(json.dumps(failure.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(format_report(failure))
        return 1

    result = validate(document, profile=profile, screening=screening)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(result))

    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
