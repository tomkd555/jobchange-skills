"""job-change-job-search: job_search_results.json の機械的な（非LLM）検証ツール。

標準ライブラリのみで、求人検索の成果物である job_search_results.json を機械的に検査する。
スキーマ（必須フィールド・型・列挙値・引用の存在）に加え、--profile を渡した場合は
PII リントを行い、利用者の現勤務先名・氏名らしき値・現年収（salary.current）が成果物へ
混入していないかを検出する。profile の読み取りはローカルに閉じ、外部へ送信しない。

CLI:
    python validate_job_search_results.py <job_search_results.json> [--json] [--profile <profile.json>]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import unicodedata
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
_V21_SCHEMA_VERSION = "2.1"
_V22_SCHEMA_VERSION = "2.2"
_V23_SCHEMA_VERSION = "2.3"
_KNOWN_SCHEMA_VERSIONS = (
    _V1_SCHEMA_VERSION,
    _V2_SCHEMA_VERSION,
    _V21_SCHEMA_VERSION,
    _V22_SCHEMA_VERSION,
    _V23_SCHEMA_VERSION,
)
# 観測層・判定層・総括を持つバージョン。
_SCREENING_SCHEMA_VERSIONS = (_V2_SCHEMA_VERSION, _V21_SCHEMA_VERSION, _V22_SCHEMA_VERSION, _V23_SCHEMA_VERSION)
# search_log・improvement_axes・baseline_comparison が有効なバージョン。
_V21_AND_LATER_SCHEMA_VERSIONS = (_V21_SCHEMA_VERSION, _V22_SCHEMA_VERSION, _V23_SCHEMA_VERSION)
# search_sets・role_match・related_info が有効なバージョン。
_V22_AND_LATER_SCHEMA_VERSIONS = (_V22_SCHEMA_VERSION, _V23_SCHEMA_VERSION)

# 取得日時。YYYY-MM-DD、または ISO 8601（日付に時刻が続く形）を受ける。
_FETCHED_AT_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}([T ][0-9:.+\-Z]+)?$")

# similar_better の軸別比較。4軸は screening-axes.md の語彙をそのまま用い、
# employment_type・scope_of_change は基準比較専用の追加軸である。原本は references/job-search-format.md にある。
BASELINE_COMPARISON_AXES = (
    "salary_condition",
    "remote_certainty",
    "annual_holidays",
    "overtime_hours",
    "employment_type",
    "scope_of_change",
)
# 尺度上の関係。良し悪しではなく、事実としてどちら側かだけを表す。
RELATIONS = ("higher", "lower", "same", "unknown")
# 雇用形態は順序を持たないため、同一か否かの3値を用いる。
_EMPLOYMENT_TYPE_RELATIONS = ("same", "different", "unknown")
# 改善軸に選ばれたときの (改善方向, 逆方向)。良し悪しはここで初めて現れる（判定層）。
# employment_type は尺度上の方向を持たないため改善軸に取れない。雇用形態の希望は conditions で扱う。
_IMPROVEMENT_DIRECTION = {
    "salary_condition": ("higher", "lower"),
    "annual_holidays": ("higher", "lower"),
    "overtime_hours": ("lower", "higher"),
    "remote_certainty": ("higher", "lower"),
    "scope_of_change": ("lower", "higher"),
}
IMPROVEMENT_AXES = tuple(_IMPROVEMENT_DIRECTION)
BASELINE_OVERALLS = ("better", "not_better")


def _axis_relations(axis: str) -> tuple[str, ...]:
    return _EMPLOYMENT_TYPE_RELATIONS if axis == "employment_type" else RELATIONS

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
# work_character_preferences[].desire → axis_judgements[].level の対応表。原本は job-search-format.md にある。
_DESIRE_TO_LEVEL = {
    "must": "must",
    "important": "want",
    "neutral": "none",
    "not_required": "none",
}
# work_character_preferences[].trait → 8軸 id の対応表。求人票から観測できる5特性だけが軸を持つ
# （残る3特性は screening-axes.md の「観測できない3特性」であり、判定に関与しない）。原本は同ファイル。
_TRAIT_TO_AXIS = {
    "hands_on": "hands_on_ratio",
    "build_ops_ratio": "hands_on_ratio",
    "low_coordination": "coordination_ratio",
    "full_remote_guaranteed": "remote_certainty",
    "no_oncall": "oncall_load",
}
# level の厳しさの順。同じ軸に複数の条件・特性が対応する場合、最も厳しい方を採る。
_LEVEL_STRICTNESS = {"none": 0, "want": 1, "must": 2}

CLASSIFICATIONS = ("apply_candidate", "needs_more_research", "excluded")
# 厳しい順。override は厳格化方向のみ許す。
_CLASSIFICATION_STRICTNESS = {"apply_candidate": 0, "needs_more_research": 1, "excluded": 2}
_MAX_UNKNOWN_FOR_APPLY = 4

RECOMMENDATIONS = ("応募推奨あり", "応募推奨なし", "判定不能")
AXES_SOURCES = ("job_change_axis.conditions", "degraded")

# 検索集合。primary は利用者の指定条件。exploration は 2.2 の探索集合、derived は 2.3 の派生レーン
# （exploration を10レーンへ一般化したもの）。原本は references/job-search-format.md にある。
SEARCH_SETS = ("primary", "exploration", "derived")
_SEARCH_SETS_BY_VERSION = {
    _V22_SCHEMA_VERSION: ("primary", "exploration"),
    _V23_SCHEMA_VERSION: ("primary", "derived"),
}
# 派生レーン（2.3）。原本は references/derivation-lanes.md にある。
DERIVATION_LANES = (
    "adjacent_role",
    "industry_widen",
    "seniority_shift",
    "remote_widen",
    "region_widen",
    "better_salary",
    "better_holidays",
    "better_workstyle",
    "company_type",
    "direct_careers",
)
# 1レーンあたりのクエリ本数の上限。超過は WARN。
_MAX_QUERIES_PER_LANE = 3
# 求人の職種と検索条件の職種との関係（2.2）。
ROLE_MATCHES = ("same", "adjacent", "different")
# related_info の許容キー（2.2）。ログイン不要で取得できる企業関連事実に限る。
RELATED_INFO_KEYS = (
    "employee_count",
    "founded_year",
    "listed",
    "capital_yen",
    "edinet_code",
    "certifications",
    "review_aggregate",
    "posting_age",
    "salary_benchmark",
)
_RELATED_INFO_GRADES = ("A", "B", "C", "D")
# related_info.as_of の形式。YYYY または YYYY-MM。
_RELATED_INFO_AS_OF_RE = re.compile(r"^[0-9]{4}(-[0-9]{2})?$")
# 2.3 で related_info に残る求人単位のキー。残りの7キーは company_profiles[].basics へ移る。
POSTING_RELATED_INFO_KEYS = ("posting_age", "salary_benchmark")
COMPANY_BASICS_KEYS = tuple(k for k in RELATED_INFO_KEYS if k not in POSTING_RELATED_INFO_KEYS)
# company_profiles[].metrics の軸キーと単位（2.3）。job-change-company-research の
# validate_company_research.QUANTITATIVE_AXIS_UNITS と同一に保つ（hub の test_vocabulary_sync が照合する）。
COMPANY_METRIC_UNITS = {
    "compensation_level": "円",
    "annual_holidays": "日",
    "monthly_overtime": "時間",
    "paid_leave_rate": "%",
    "turnover_rate": "%",
    "male_childcare_leave_rate": "%",
    "revenue_growth": "%",
    "operating_margin": "%",
    "equity_ratio": "%",
}
# 0〜100 の範囲に収まるべき比率の軸。
_RATE_METRICS_0_100 = ("paid_leave_rate", "turnover_rate", "male_childcare_leave_rate", "equity_ratio")
# 負の値を取りうる軸（成長率・利益率）。
_SIGNED_METRICS = ("revenue_growth", "operating_margin")
# company_key の正規化で先頭・末尾から取り除く法人格の表記。NFKC 後の形で書く。
_LEGAL_ENTITY_TOKENS = (
    "株式会社",
    "有限会社",
    "合同会社",
    "合資会社",
    "合名会社",
    "一般社団法人",
    "一般財団法人",
    "公益社団法人",
    "公益財団法人",
    "(株)",
    "(有)",
    "(同)",
)


def normalize_company_key(name: Any) -> str:
    """企業名を company_key へ正規化する。merge_search_results.py と共用する唯一の実装である。

    NFKC 正規化（全角英数→半角、（株）・㈱→(株)）→ 空白の全除去 → 先頭・末尾の法人格表記の除去
    （中間の表記は残す）→ ASCII の小文字化。法人格だけの名前は空文字を返す。
    """
    if not isinstance(name, str):
        return ""
    s = unicodedata.normalize("NFKC", name)
    s = "".join(s.split())
    changed = True
    while changed and s:
        changed = False
        for token in _LEGAL_ENTITY_TOKENS:
            if s.startswith(token):
                s = s[len(token):]
                changed = True
            if s.endswith(token):
                s = s[: -len(token)]
                changed = True
    return s.lower()

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


def _is_valid_fetched_at(value: Any) -> bool:
    """YYYY-MM-DD 形式の実在日付、または日付で始まる ISO 8601 であれば True を返す。"""
    if not isinstance(value, str) or not _FETCHED_AT_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value[:10])
    except ValueError:
        return False
    return True


# company_profiles[].negative_checks・recent_news の日付。YYYY-MM-DD または YYYY-MM。
_YEAR_MONTH_DAY_RE = re.compile(r"^[0-9]{4}-[0-9]{2}(-[0-9]{2})?$")


def _is_valid_year_month_or_day(value: Any) -> bool:
    """YYYY-MM-DD 形式の実在日付、または YYYY-MM 形式であれば True を返す。"""
    if not isinstance(value, str) or not _YEAR_MONTH_DAY_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value if len(value) == 10 else f"{value}-01")
    except ValueError:
        return False
    return True


def _validate_search_log(
    document: dict, version: Any, valid_lanes: list[str], result: ValidationResult
) -> None:
    """検索の実行ログを検査する。2.1 では必須である。"""
    log = document.get("search_log")
    required = version in _V21_AND_LATER_SCHEMA_VERSIONS
    if log is None:
        if required:
            result.add_error(
                "search_log",
                "search_log は必須である。実行したクエリと取得元を記録しないまま網羅性を主張できない",
            )
        return
    if not isinstance(log, list):
        result.add_error("search_log", "search_log は配列でなければならない")
        return
    if not log and required:
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
        if version in _V22_AND_LATER_SCHEMA_VERSIONS:
            allowed_sets = _SEARCH_SETS_BY_VERSION[version]
            search_set = entry.get("search_set")
            if "search_set" not in entry:
                result.add_error(
                    f"{path}.search_set",
                    f"search_set は必須である（{'/'.join(allowed_sets)} のいずれか）",
                )
            elif search_set not in allowed_sets:
                result.add_error(
                    f"{path}.search_set",
                    f"search_set は {'/'.join(allowed_sets)} のいずれかである（実値: {search_set!r}）",
                )
            elif version == _V23_SCHEMA_VERSION:
                lane = entry.get("lane")
                if search_set == "derived":
                    if lane not in valid_lanes:
                        result.add_error(
                            f"{path}.lane",
                            "search_set が derived の search_log には derivations にあるレーンの"
                            f"lane が必須である（実値: {lane!r}）",
                        )
                elif "lane" in entry and entry["lane"] is not None:
                    result.add_error(
                        f"{path}.lane",
                        "search_set が primary の search_log に lane を書いてはならない",
                    )


def derive_baseline_overall(axes: list[dict], improvement_axes: list[str]) -> str:
    """改善軸と軸別の関係から総合判定を導く。判定表は job-search-format.md にある。

    利用者が選んだ改善軸だけを見る。選ばれなかった軸は表示用の記録であり、総合判定に効かせない。
    """
    relations = {axis.get("axis"): axis.get("relation") for axis in axes}
    improved = False
    for axis in improvement_axes:
        direction = _IMPROVEMENT_DIRECTION.get(axis)
        if direction is None:
            continue
        relation = relations.get(axis)
        if relation == direction[1]:
            return "not_better"
        if relation == direction[0]:
            improved = True
    return "better" if improved else "not_better"


def _validate_improvement_axes(
    document: dict, mode: str | None, version: Any, result: ValidationResult
) -> list[str]:
    """トップレベルの improvement_axes を検査し、有効な軸 id の一覧を返す。"""
    axes = document.get("improvement_axes")
    if axes is None:
        if mode == "similar_better" and version in _V21_AND_LATER_SCHEMA_VERSIONS:
            result.add_warning(
                "improvement_axes",
                "similar_better では利用者が選んだ改善軸（improvement_axes）の記録を推奨する",
            )
        return []
    if not isinstance(axes, list):
        result.add_error("improvement_axes", "improvement_axes は配列でなければならない")
        return []
    if mode == "fuzzy" and axes:
        result.add_warning("improvement_axes", "fuzzy では improvement_axes は用いない（similar_better 専用）")
    if not axes and mode == "similar_better" and version in _V21_AND_LATER_SCHEMA_VERSIONS:
        result.add_warning("improvement_axes", "improvement_axes が空である。狙う改善軸を1つ以上記録する")

    valid: list[str] = []
    for i, axis in enumerate(axes):
        if axis == "employment_type":
            result.add_error(
                f"improvement_axes[{i}]",
                "employment_type は尺度上の方向を持たないため改善軸に取れない。"
                "雇用形態の希望は conditions の必須条件として扱う",
            )
            continue
        if axis not in IMPROVEMENT_AXES:
            result.add_error(
                f"improvement_axes[{i}]",
                f"改善軸は {'/'.join(IMPROVEMENT_AXES)} のいずれかである（実値: {axis!r}）",
            )
            continue
        if axis in valid:
            result.add_error(f"improvement_axes[{i}]", f"改善軸が重複している: {axis}")
            continue
        valid.append(axis)
    return valid


def _validate_baseline_comparison(
    item: dict,
    path: str,
    mode: str | None,
    version: Any,
    improvement_axes: list[str],
    result: ValidationResult,
) -> None:
    comparison = item.get("baseline_comparison")
    bc_path = f"{path}.baseline_comparison"
    if comparison is None:
        if mode == "similar_better" and version in _V21_AND_LATER_SCHEMA_VERSIONS:
            result.add_warning(
                bc_path,
                "similar_better では基準求人との軸別比較（baseline_comparison）の記載を推奨する",
            )
        return
    if not isinstance(comparison, dict):
        result.add_error(bc_path, "baseline_comparison はオブジェクトでなければならない")
        return
    if mode == "fuzzy":
        result.add_warning(bc_path, "fuzzy では baseline_comparison は用いない（similar_better 専用）")

    axes = comparison.get("axes")
    if not isinstance(axes, list):
        result.add_error(f"{bc_path}.axes", "axes は配列が必須である")
        return

    seen: list[str] = []
    valid: list[dict] = []
    for j, entry in enumerate(axes):
        e_path = f"{bc_path}.axes[{j}]"
        if not isinstance(entry, dict):
            result.add_error(e_path, "axes の各要素はオブジェクトでなければならない")
            continue
        axis = entry.get("axis")
        if axis not in BASELINE_COMPARISON_AXES:
            result.add_error(
                f"{e_path}.axis",
                f"axis は {'/'.join(BASELINE_COMPARISON_AXES)} のいずれかである",
            )
            continue
        seen.append(axis)
        relation = entry.get("relation")
        allowed = _axis_relations(axis)
        if relation not in allowed:
            result.add_error(
                f"{e_path}.relation",
                f"{axis} の relation は {'/'.join(allowed)} のいずれかである（実値: {relation!r}）",
            )
            continue
        valid.append(entry)
        if relation == "unknown":
            continue
        # 記載が無い軸は unknown にする。同等（same）も含め、比べたと言う以上は両側の値と引用が要る。
        for key in ("baseline_value", "candidate_value"):
            if not _is_nonempty_str(entry.get(key)):
                result.add_error(
                    f"{e_path}.{key}",
                    f"relation が {relation} の軸には {key} が必須である。"
                    "求人票に記載が無い軸は unknown とする（記載の無さを same と扱ってはならない）",
                )
        if not _is_nonempty_str(entry.get("quote")):
            result.add_error(
                f"{e_path}.quote",
                f"relation が {relation} の軸には掲載ページからの引用（quote）が必須である",
            )

    missing = [a for a in BASELINE_COMPARISON_AXES if a not in seen]
    duplicated = sorted({a for a in seen if seen.count(a) > 1})
    if missing:
        result.add_error(f"{bc_path}.axes", f"6軸を過不足なく持つ必要がある。欠落: {', '.join(missing)}")
    if duplicated:
        result.add_error(f"{bc_path}.axes", f"axis が重複している: {', '.join(duplicated)}")

    overall = comparison.get("overall")
    if overall not in BASELINE_OVERALLS:
        result.add_error(
            f"{bc_path}.overall",
            f"overall は {'/'.join(BASELINE_OVERALLS)} のいずれかである",
        )
        return
    if not improvement_axes:
        if mode == "similar_better":
            result.add_error(
                f"{bc_path}.overall",
                "改善軸（improvement_axes）が無いまま総合判定を書いてはならない。"
                "どの軸で上回りたいかが決まらなければ、より良いかどうかは導けない",
            )
        return  # fuzzy では baseline_comparison 自体が場違いであり、既に WARN で示している。
    if len(valid) != len(BASELINE_COMPARISON_AXES):
        return  # 軸側が壊れている場合、導出結果との照合は行わない。
    derived = derive_baseline_overall(valid, improvement_axes)
    if overall != derived:
        result.add_error(
            f"{bc_path}.overall",
            f"改善軸（{'/'.join(improvement_axes)}）から導かれる総合判定は {derived} である"
            "（改善軸の1つ以上が改善方向で、かつ改善軸に逆方向が1つも無いときだけ better）",
        )


def _validate_result_item(
    item: Any,
    index: int,
    mode: str | None,
    version: Any,
    improvement_axes: list[str],
    result: ValidationResult,
) -> None:
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

    _validate_baseline_comparison(item, path, mode, version, improvement_axes, result)


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
    """軸判定から分類を機械的に導く。判定表は job-search-format.md にある。"""
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


def _validate_search_log_exploration_link(document: dict, results: Any, result: ValidationResult) -> None:
    """探索集合の求人があるのに search_log に探索集合のクエリが無い場合を検査する（2.2）。

    探索集合の求人は探索集合のクエリからしか採用できない。result 側の件数に関わらず
    ERROR は1件だけ報告し、result ごとに重複報告しない。
    """
    if not isinstance(results, list):
        return
    has_exploration_result = any(
        isinstance(item, dict) and item.get("search_set") == "exploration" for item in results
    )
    if not has_exploration_result:
        return
    log = document.get("search_log")
    has_exploration_log = isinstance(log, list) and any(
        isinstance(entry, dict) and entry.get("search_set") == "exploration" for entry in log
    )
    if not has_exploration_log:
        result.add_error(
            "search_log",
            "search_set が exploration の result があるが、search_log に search_set が exploration の"
            "要素が無い。探索集合の求人は探索集合のクエリからしか採用できない",
        )


def _validate_search_sets(document: dict, mode: str | None, result: ValidationResult) -> None:
    """search_sets（探索集合の記録、2.2 専用）を検査する。"""
    search_sets = document.get("search_sets")
    if not isinstance(search_sets, dict):
        result.add_error("search_sets", "search_sets はオブジェクトが必須である")
        return

    if not isinstance(search_sets.get("primary"), dict):
        result.add_error("search_sets.primary", "primary はオブジェクトが必須である")

    exploration = search_sets.get("exploration")
    if exploration is not None:
        if not isinstance(exploration, dict):
            result.add_error(
                "search_sets.exploration",
                "exploration はオブジェクトまたは null でなければならない",
            )
        else:
            path = "search_sets.exploration"
            roles = exploration.get("roles")
            if not isinstance(roles, list) or not all(_is_nonempty_str(r) for r in roles):
                result.add_error(
                    f"{path}.roles", "roles は非空の文字列の配列でなければならない（該当が無ければ空配列）"
                )
            industries = exploration.get("industries")
            if industries is not None and (
                not isinstance(industries, list) or not all(_is_nonempty_str(i) for i in industries)
            ):
                result.add_error(
                    f"{path}.industries",
                    "industries は非空の文字列の配列、または任意を表す null でなければならない",
                )
            dropped = exploration.get("dropped_conditions")
            if not isinstance(dropped, list) or not all(_is_nonempty_str(d) for d in dropped):
                result.add_error(
                    f"{path}.dropped_conditions",
                    "dropped_conditions は非空の文字列の配列でなければならない（該当が無ければ空配列）",
                )
            if not _is_nonempty_str(exploration.get("rationale")):
                result.add_error(f"{path}.rationale", "rationale は必須（非空）である")

    if mode == "fuzzy" and exploration is None:
        result.add_warning(
            "search_sets.exploration", "探索集合を作っていない（偏りの点検を省いている）"
        )
    if mode == "similar_better" and exploration is not None:
        result.add_warning(
            "search_sets.exploration", "similar_better では exploration は用いない（fuzzy 専用）"
        )


def _check_source_and_grade(entry: dict, path: str, result: ValidationResult) -> None:
    """出典URL（http で始まる）とエビデンスレベル（A〜D）を検査する。出典付きの値で共用する。"""
    source_url = entry.get("source_url")
    if not (isinstance(source_url, str) and source_url.startswith("http")):
        result.add_error(
            f"{path}.source_url",
            f"source_url は http で始まる文字列でなければならない（実値: {source_url!r}）",
        )
    grade = entry.get("grade")
    if grade not in _RELATED_INFO_GRADES:
        result.add_error(
            f"{path}.grade",
            f"grade は {'/'.join(_RELATED_INFO_GRADES)} のいずれかである（実値: {grade!r}）",
        )


def _validate_sourced_value(entry: dict, entry_path: str, key: str, result: ValidationResult) -> None:
    """出典付き値1件の本体（value・source_url・grade・as_of）を検査する。entry は dict である前提。

    results[].related_info（2.2 以降）と company_profiles[].basics（2.3）で共用する。
    """
    for required_key in ("value", "source_url", "grade", "as_of"):
        if required_key not in entry:
            result.add_error(f"{entry_path}.{required_key}", f"{required_key} は必須である")

    value = entry.get("value")
    if value is not None:
        if isinstance(value, bool) and key != "listed":
            result.add_error(
                f"{entry_path}.value",
                f"真偽値は listed 以外のキーでは使えない（{key} の実値: {value!r}）",
            )
        _check_source_and_grade(entry, entry_path, result)

    as_of = entry.get("as_of")
    if as_of is not None and not (isinstance(as_of, str) and _RELATED_INFO_AS_OF_RE.match(as_of)):
        result.add_error(
            f"{entry_path}.as_of",
            f"as_of は YYYY または YYYY-MM 形式、または null でなければならない（実値: {as_of!r}）",
        )


def _validate_related_info(item: dict, path: str, version: Any, result: ValidationResult) -> None:
    """results[].related_info（2.2 以降）を検査する。"""
    if "related_info" not in item:
        return
    related = item["related_info"]
    if not isinstance(related, dict):
        result.add_error(f"{path}.related_info", "related_info はオブジェクトでなければならない")
        return

    for key, entry in related.items():
        entry_path = f"{path}.related_info.{key}"
        if key not in RELATED_INFO_KEYS:
            result.add_error(
                entry_path,
                f"related_info のキーは {'/'.join(RELATED_INFO_KEYS)} のいずれかである（実値: {key!r}）",
            )
            continue
        if not isinstance(entry, dict):
            result.add_error(entry_path, "related_info の各値はオブジェクトでなければならない")
            continue
        _validate_sourced_value(entry, entry_path, key, result)
        if version == _V23_SCHEMA_VERSION and key in COMPANY_BASICS_KEYS:
            result.add_warning(entry_path, "2.3 では company_profiles[].basics へ置く")


def _validate_company_basics(basics: Any, path: str, result: ValidationResult) -> None:
    """company_profiles[].basics（2.3）を検査する。1件ごとの本体は related_info と共用する。"""
    b_path = f"{path}.basics"
    if not isinstance(basics, dict):
        result.add_error(b_path, "basics はオブジェクトが必須である")
        return
    for key, entry in basics.items():
        entry_path = f"{b_path}.{key}"
        if key not in COMPANY_BASICS_KEYS:
            result.add_error(
                entry_path,
                f"basics のキーは {'/'.join(COMPANY_BASICS_KEYS)} のいずれかである（実値: {key!r}）",
            )
            continue
        if not isinstance(entry, dict):
            result.add_error(entry_path, "basics の各値はオブジェクトでなければならない")
            continue
        _validate_sourced_value(entry, entry_path, key, result)
        if entry.get("value") is None and not _is_nonempty_str(entry.get("note")):
            result.add_warning(
                f"{entry_path}.note", "value が null の場合、取得できなかった事情を note に書くことを推奨する"
            )
    missing = [k for k in COMPANY_BASICS_KEYS if k not in basics]
    if missing:
        result.add_warning(b_path, f"取得していない基礎情報がある: {', '.join(missing)}")


def _validate_v22_result_item(
    item: Any, index: int, exploration_defined: bool, result: ValidationResult
) -> None:
    """result 1件の 2.2 専用フィールド（search_set・role_match・related_info）を検査する。"""
    if not isinstance(item, dict):
        return
    path = f"results[{index}]"

    allowed_sets = _SEARCH_SETS_BY_VERSION[_V22_SCHEMA_VERSION]
    search_set = item.get("search_set")
    if search_set not in allowed_sets:
        result.add_error(
            f"{path}.search_set",
            f"search_set は {'/'.join(allowed_sets)} のいずれかである（実値: {search_set!r}）",
        )
    elif search_set == "exploration" and not exploration_defined:
        result.add_error(
            f"{path}.search_set",
            "search_set が exploration だが、search_sets.exploration が null である",
        )

    role_match = item.get("role_match")
    if role_match not in ROLE_MATCHES:
        result.add_error(
            f"{path}.role_match",
            f"role_match は {'/'.join(ROLE_MATCHES)} のいずれかである（実値: {role_match!r}）",
        )
    elif search_set == "primary" and role_match == "different":
        result.add_warning(
            f"{path}.role_match",
            "primary は利用者の指定条件による検索である。role_match が different の結果はノイズの可能性がある",
        )

    _validate_related_info(item, path, _V22_SCHEMA_VERSION, result)


def _validate_screening_exploration(document: dict, results: Any, result: ValidationResult) -> None:
    """screening.exploration（2.2 専用）を検査する。"""
    screening = document.get("screening")
    if not isinstance(screening, dict):
        return  # screening 自体の欠落・型不一致は _validate_screening が既に報告している。

    exploration = screening.get("exploration")
    path = "screening.exploration"
    if not isinstance(exploration, dict):
        result.add_error(path, "exploration はオブジェクトが必須である")
        return

    for required_key in ("performed", "result_count", "apply_candidate_count"):
        if required_key not in exploration:
            result.add_error(
                f"{path}.{required_key}", f"{required_key} は必須である。未実施なら null を書く"
            )
    if "performed" not in exploration:
        return

    performed = exploration.get("performed")
    if not isinstance(performed, bool):
        result.add_error(f"{path}.performed", "performed は真偽値が必須である")
        return

    items = results if isinstance(results, list) else []
    actual_results = sum(1 for r in items if isinstance(r, dict) and r.get("search_set") == "exploration")
    actual_apply = sum(
        1
        for r in items
        if isinstance(r, dict)
        and r.get("search_set") == "exploration"
        and r.get("classification") == "apply_candidate"
    )

    result_count = exploration.get("result_count")
    apply_count = exploration.get("apply_candidate_count")

    if performed:
        if isinstance(result_count, bool) or not isinstance(result_count, int):
            result.add_error(
                f"{path}.result_count", f"result_count は整数でなければならない（実値: {result_count!r}）"
            )
        elif result_count != actual_results:
            result.add_error(
                f"{path}.result_count",
                f"実際の件数（search_set=exploration の results、{actual_results}件）と一致しない"
                f"（記載: {result_count!r}）",
            )
        if isinstance(apply_count, bool) or not isinstance(apply_count, int):
            result.add_error(
                f"{path}.apply_candidate_count",
                f"apply_candidate_count は整数でなければならない（実値: {apply_count!r}）",
            )
        elif apply_count != actual_apply:
            result.add_error(
                f"{path}.apply_candidate_count",
                f"実際の件数（search_set=exploration かつ apply_candidate、{actual_apply}件）と一致しない"
                f"（記載: {apply_count!r}）",
            )
    else:
        if result_count is not None:
            result.add_error(
                f"{path}.result_count", "performed が false の場合、result_count は null でなければならない"
            )
        if apply_count is not None:
            result.add_error(
                f"{path}.apply_candidate_count",
                "performed が false の場合、apply_candidate_count は null でなければならない",
            )
        search_sets = document.get("search_sets")
        if isinstance(search_sets, dict) and search_sets.get("exploration") is not None:
            result.add_error(path, "探索集合があるのに未実施と記録している")


def _validate_threshold_refs(document: dict, profile: Any, result: ValidationResult) -> None:
    """--profile 指定時: threshold_ref の実在と level の一致、および軸ごとの必須度との整合を検査する。"""
    if not isinstance(profile, dict):
        return
    axis_block = profile.get("job_change_axis")
    if not isinstance(axis_block, dict):
        return

    levels: dict[str, str] = {}
    # 軸 id → profile 側でその軸に対応する条件・特性のうち最も厳しい level。
    # 同じ軸に複数の条件・特性が対応しうる（例: hands_on と build_ops_ratio はどちらも
    # hands_on_ratio）ため、最も厳しい方を採る。
    axis_levels: dict[str, str] = {}

    def _tighten_axis(axis: Any, level: str) -> None:
        if axis not in SCREENING_AXES:
            return
        current = axis_levels.get(axis, "none")
        if _LEVEL_STRICTNESS.get(level, 0) > _LEVEL_STRICTNESS.get(current, 0):
            axis_levels[axis] = level

    conditions = axis_block.get("conditions")
    if isinstance(conditions, list):
        for condition in conditions:
            if isinstance(condition, dict) and _is_nonempty_str(condition.get("id")):
                level = condition.get("level", "")
                levels[condition["id"]] = level
                _tighten_axis(condition.get("axis"), level)
    preferences = axis_block.get("work_character_preferences")
    if isinstance(preferences, list):
        for preference in preferences:
            if isinstance(preference, dict) and _is_nonempty_str(preference.get("trait")):
                desire = preference.get("desire")
                level = _DESIRE_TO_LEVEL.get(desire, "none")
                levels[preference["trait"]] = level
                _tighten_axis(_TRAIT_TO_AXIS.get(preference["trait"]), level)
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
            if not isinstance(judgement, dict):
                continue
            level = judgement.get("level")
            path = f"results[{i}].axis_judgements[{j}]"
            if level in ("must", "want"):
                ref = judgement.get("threshold_ref")
                if not _is_nonempty_str(ref):
                    continue
                if ref not in levels:
                    result.add_error(f"{path}.threshold_ref", f"profile に存在しない条件・特性を参照している: {ref}")
                elif levels[ref] != level:
                    result.add_error(
                        f"{path}.threshold_ref",
                        f"profile での必須度（{levels[ref]}）と level（{level}）が一致しない",
                    )
            elif level == "none":
                # level を none にすると、profile 側にその軸への条件・特性が無いことになる。
                # 軸に must・want の必須度が実在するのに none へ緩めていれば、下流の分類が甘くなる。
                required = axis_levels.get(judgement.get("axis"))
                if required in ("must", "want"):
                    result.add_error(
                        f"{path}.level",
                        f"profile での必須度は{required}だが、level が none になっている。"
                        "対応する条件・特性のしきい値を threshold_ref に書く",
                    )


# --- schema_version 2.3（派生レーンと企業プロフィール）の検査 -----------------


def _validate_derivations(search_sets: dict, result: ValidationResult) -> list[str]:
    """search_sets.derivations（2.3 必須）を検査し、有効なレーン id の一覧を返す。"""
    path = "search_sets.derivations"
    derivations = search_sets.get("derivations")
    if not isinstance(derivations, list):
        result.add_error(path, "derivations は配列が必須である")
        return []

    primary = search_sets.get("primary")
    primary_salary_min = primary.get("salary_min") if isinstance(primary, dict) else None
    if isinstance(primary_salary_min, bool) or not isinstance(primary_salary_min, (int, float)):
        primary_salary_min = None

    seen: list[str] = []
    valid: list[str] = []
    for i, derivation in enumerate(derivations):
        d_path = f"{path}[{i}]"
        if not isinstance(derivation, dict):
            result.add_error(d_path, "derivations の各要素はオブジェクトでなければならない")
            continue

        lane = derivation.get("lane")
        if lane not in DERIVATION_LANES:
            result.add_error(
                f"{d_path}.lane", f"lane は {'/'.join(DERIVATION_LANES)} のいずれかである（実値: {lane!r}）"
            )
        elif lane in seen:
            result.add_error(f"{d_path}.lane", f"lane が重複している: {lane}")
        else:
            seen.append(lane)
            valid.append(lane)

        roles = derivation.get("roles")
        if not isinstance(roles, list) or not all(_is_nonempty_str(r) for r in roles):
            result.add_error(
                f"{d_path}.roles", "roles は非空の文字列の配列でなければならない（該当が無ければ空配列）"
            )

        industries = derivation.get("industries")
        if industries is not None and (
            not isinstance(industries, list) or not all(_is_nonempty_str(x) for x in industries)
        ):
            result.add_error(
                f"{d_path}.industries",
                "industries は非空の文字列の配列、または任意を表す null でなければならない",
            )

        salary_min = derivation.get("salary_min")
        if salary_min is not None:
            if isinstance(salary_min, bool) or not isinstance(salary_min, (int, float)):
                result.add_error(
                    f"{d_path}.salary_min",
                    f"salary_min は数値または null でなければならない（実値: {salary_min!r}）",
                )
            elif primary_salary_min is not None and salary_min < primary_salary_min:
                result.add_error(
                    f"{d_path}.salary_min",
                    f"salary_min は primary の salary_min（{primary_salary_min}）を下回ってはならない"
                    f"（実値: {salary_min}）",
                )

        for key in ("location", "remote_policy", "employment_type"):
            if key in derivation and derivation[key] is not None and not isinstance(derivation[key], str):
                result.add_error(f"{d_path}.{key}", f"{key} は文字列または null でなければならない")

        changed = derivation.get("changed_conditions")
        if not isinstance(changed, list) or not changed or not all(_is_nonempty_str(c) for c in changed):
            result.add_error(
                f"{d_path}.changed_conditions",
                "changed_conditions は非空の文字列を1件以上持つ配列でなければならない",
            )

        if not _is_nonempty_str(derivation.get("rationale")):
            result.add_error(f"{d_path}.rationale", "rationale は必須（非空）である")

    return valid


def _validate_search_sets_v23(document: dict, mode: str | None, result: ValidationResult) -> list[str]:
    """search_sets（2.3）を検査し、有効な派生レーン id の一覧を返す。"""
    search_sets = document.get("search_sets")
    if not isinstance(search_sets, dict):
        result.add_error("search_sets", "search_sets はオブジェクトが必須である")
        return []

    if not isinstance(search_sets.get("primary"), dict):
        result.add_error("search_sets.primary", "primary はオブジェクトが必須である")

    if search_sets.get("exploration") is not None:
        result.add_error("search_sets.exploration", "2.3 では derivations を使う")

    valid_lanes = _validate_derivations(search_sets, result)

    derivations = search_sets.get("derivations")
    if mode == "fuzzy" and isinstance(derivations, list) and not derivations:
        result.add_warning(
            "search_sets.derivations", "派生レーンを検索していない（偏りの点検を省いている）"
        )
    return valid_lanes


def _validate_v23_result_item(
    item: Any,
    index: int,
    valid_lanes: list[str],
    company_profiles: Any,
    result: ValidationResult,
) -> None:
    """result 1件の 2.3 専用フィールド（search_set・lane・role_match・company_key・related_info）を検査する。"""
    if not isinstance(item, dict):
        return
    path = f"results[{index}]"

    allowed_sets = _SEARCH_SETS_BY_VERSION[_V23_SCHEMA_VERSION]
    search_set = item.get("search_set")
    if search_set not in allowed_sets:
        result.add_error(
            f"{path}.search_set",
            f"search_set は {'/'.join(allowed_sets)} のいずれかである（実値: {search_set!r}）",
        )

    lane = item.get("lane")
    if search_set == "derived":
        if lane not in valid_lanes:
            result.add_error(
                f"{path}.lane",
                f"search_set が derived の result には derivations にあるレーンの lane が必須である"
                f"（実値: {lane!r}）",
            )
    elif search_set == "primary" and "lane" in item and item["lane"] is not None:
        result.add_error(f"{path}.lane", "search_set が primary の result に lane を書いてはならない")

    role_match = item.get("role_match")
    if role_match not in ROLE_MATCHES:
        result.add_error(
            f"{path}.role_match",
            f"role_match は {'/'.join(ROLE_MATCHES)} のいずれかである（実値: {role_match!r}）",
        )
    elif search_set == "primary" and role_match == "different":
        result.add_warning(
            f"{path}.role_match",
            "primary は利用者の指定条件による検索である。role_match が different の結果はノイズの可能性がある",
        )

    _validate_related_info(item, path, _V23_SCHEMA_VERSION, result)

    company_key = item.get("company_key")
    if not _is_nonempty_str(company_key):
        result.add_error(f"{path}.company_key", "company_key は必須（非空）である")
    elif isinstance(company_profiles, dict):
        profile = company_profiles.get(company_key)
        if not isinstance(profile, dict):
            result.add_error(
                f"{path}.company_key",
                f"company_key は company_profiles に存在するキーでなければならない（実値: {company_key!r}）",
            )
        else:
            normalized_name = normalize_company_key(item.get("company_name"))
            candidates = {normalize_company_key(profile.get("name"))}
            aliases = profile.get("aliases")
            if isinstance(aliases, list):
                candidates.update(normalize_company_key(a) for a in aliases)
            if normalized_name and normalized_name not in candidates:
                result.add_warning(
                    f"{path}.company_key",
                    f"company_name（{item.get('company_name')!r}）の正規化結果が "
                    f"company_profiles[{company_key!r}] の name・aliases のいずれとも一致しない",
                )


def _validate_metric(key: str, entry: Any, path: str, result: ValidationResult) -> None:
    """company_profiles[].metrics の軸1件を検査する。"""
    if not isinstance(entry, dict):
        result.add_error(path, "各項目は {value, unit, source_url, grade, as_of} のオブジェクトでなければならない")
        return
    for required_key in ("value", "unit", "source_url", "grade", "as_of"):
        if required_key not in entry:
            result.add_error(f"{path}.{required_key}", f"{required_key} は必須である")

    if "unit" in entry and entry.get("unit") != COMPANY_METRIC_UNITS[key]:
        result.add_error(
            f"{path}.unit",
            f"unit は {COMPANY_METRIC_UNITS[key]!r} でなければならない（実値: {entry.get('unit')!r}）",
        )

    value = entry.get("value")
    if value is None:
        if not _is_nonempty_str(entry.get("note")):
            result.add_warning(
                f"{path}.note", "value が null の場合、取得できなかった事情を note に書くことを推奨する"
            )
        return

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        result.add_error(f"{path}.value", f"value は数値または null でなければならない（実値: {value!r}）")
    else:
        if value < 0 and key not in _SIGNED_METRICS:
            result.add_error(f"{path}.value", f"{key} は負の値を取らない（実値: {value}）")
        if key in _RATE_METRICS_0_100 and not (0 <= value <= 100):
            result.add_error(f"{path}.value", f"{key} は0〜100の範囲でなければならない（実値: {value}）")
        if key == "compensation_level" and 0 <= value < _SALARY_CONDITION_WARN_BELOW:
            result.add_warning(
                f"{path}.value",
                f"compensation_level は円単位である。{value} は万円単位で書いていないか確かめる",
            )

    _check_source_and_grade(entry, path, result)
    as_of = entry.get("as_of")
    if not (isinstance(as_of, str) and _RELATED_INFO_AS_OF_RE.match(as_of)):
        result.add_error(
            f"{path}.as_of", f"as_of は YYYY または YYYY-MM 形式でなければならない（実値: {as_of!r}）"
        )


def _validate_negative_checks(negative_checks: Any, path: str, result: ValidationResult) -> None:
    """company_profiles[].negative_checks（労働法令違反の公表事案の確認記録）を検査する。"""
    if not isinstance(negative_checks, dict):
        result.add_error(path, "negative_checks はオブジェクトが必須である")
        return
    llv_path = f"{path}.labor_law_violation_list"
    llv = negative_checks.get("labor_law_violation_list")
    if not isinstance(llv, dict):
        result.add_error(llv_path, "labor_law_violation_list はオブジェクトが必須である")
        return

    checked = llv.get("checked")
    if not isinstance(checked, bool):
        result.add_error(f"{llv_path}.checked", "checked は真偽値が必須である")
        return

    hit = llv.get("hit")
    if checked:
        if not isinstance(hit, bool):
            result.add_error(f"{llv_path}.hit", "checked が true の場合、hit は真偽値が必須である")
        source_url = llv.get("source_url")
        if not (isinstance(source_url, str) and source_url.startswith("http")):
            result.add_error(
                f"{llv_path}.source_url",
                f"source_url は http で始まる文字列でなければならない（実値: {source_url!r}）",
            )
        as_of = llv.get("as_of")
        if not _is_valid_year_month_or_day(as_of):
            result.add_error(
                f"{llv_path}.as_of",
                f"as_of は YYYY-MM-DD または YYYY-MM 形式でなければならない（実値: {as_of!r}）",
            )
        if hit is True and not _is_nonempty_str(llv.get("note")):
            result.add_error(f"{llv_path}.note", "hit が true の場合、note（該当事案の要旨）は必須である")
    else:
        if hit is not None:
            result.add_error(f"{llv_path}.hit", "checked が false の場合、hit は null でなければならない")


def _validate_recent_news(news: Any, path: str, result: ValidationResult) -> None:
    """company_profiles[].recent_news を検査する。"""
    if not isinstance(news, list):
        result.add_error(path, "recent_news は配列が必須である（該当が無ければ空配列）")
        return
    for i, entry in enumerate(news):
        e_path = f"{path}[{i}]"
        if not isinstance(entry, dict):
            result.add_error(e_path, "recent_news の各要素はオブジェクトでなければならない")
            continue
        if not _is_nonempty_str(entry.get("headline")):
            result.add_error(f"{e_path}.headline", "headline は必須（非空）である")
        date = entry.get("date")
        if not _is_valid_year_month_or_day(date):
            result.add_error(
                f"{e_path}.date", f"date は YYYY-MM-DD または YYYY-MM 形式でなければならない（実値: {date!r}）"
            )
        _check_source_and_grade(entry, e_path, result)


def _validate_company_profiles(document: dict, results: Any, result: ValidationResult) -> None:
    """company_profiles（2.3 必須）を検査する。"""
    profiles = document.get("company_profiles")
    if not isinstance(profiles, dict):
        result.add_error("company_profiles", "company_profiles はオブジェクトが必須である")
        return

    referenced = set()
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict) and _is_nonempty_str(item.get("company_key")):
                referenced.add(item["company_key"])

    for key, profile in profiles.items():
        path = f"company_profiles.{key}"
        if not isinstance(profile, dict):
            result.add_error(path, "各企業プロフィールはオブジェクトでなければならない")
            continue

        aliases = profile.get("aliases")
        if not isinstance(aliases, list) or not all(_is_nonempty_str(a) for a in aliases):
            result.add_error(
                f"{path}.aliases", "aliases は非空の文字列の配列でなければならない（該当が無ければ空配列）"
            )

        name = profile.get("name")
        if not _is_nonempty_str(name):
            result.add_error(f"{path}.name", "name は必須（非空）である")
        else:
            # キーは求人票の企業名から統合スクリプトが付け、name は会社概要の正式名称になりうる。
            # 両者が違う場合は求人票の表記を aliases に残すため、name か aliases のどれかと一致すればよい。
            candidates = {normalize_company_key(name)}
            if isinstance(aliases, list):
                candidates.update(normalize_company_key(a) for a in aliases)
            if key not in candidates:
                result.add_error(
                    path,
                    f"キーは name または aliases のいずれかの正規化結果と一致しなければならない"
                    f"（name の正規化結果: {normalize_company_key(name)!r}、キー: {key!r}）",
                )

        for url_key in ("official_url", "careers_url"):
            value = profile.get(url_key)
            if value is not None and not (isinstance(value, str) and value.startswith("http")):
                result.add_error(
                    f"{path}.{url_key}",
                    f"{url_key} は http で始まる文字列または null でなければならない（実値: {value!r}）",
                )

        for text_key in ("hq_location", "industry"):
            value = profile.get(text_key)
            if value is not None and not isinstance(value, str):
                result.add_error(f"{path}.{text_key}", f"{text_key} は文字列または null でなければならない")

        summary = profile.get("business_summary")
        if summary is not None:
            s_path = f"{path}.business_summary"
            if not isinstance(summary, dict):
                result.add_error(s_path, "business_summary はオブジェクトまたは null でなければならない")
            else:
                if not _is_nonempty_str(summary.get("text")):
                    result.add_error(f"{s_path}.text", "text は必須（非空）である")
                if not _is_nonempty_str(summary.get("quote")):
                    result.add_error(f"{s_path}.quote", "quote は必須（非空）である")
                _check_source_and_grade(summary, s_path, result)

        _validate_company_basics(profile.get("basics"), path, result)

        metrics = profile.get("metrics")
        m_path = f"{path}.metrics"
        if not isinstance(metrics, dict):
            result.add_error(m_path, "metrics はオブジェクトが必須である")
        else:
            for metric_key in COMPANY_METRIC_UNITS:
                if metric_key not in metrics:
                    result.add_error(f"{m_path}.{metric_key}", f"{metric_key} は必須である")
                    continue
                _validate_metric(metric_key, metrics[metric_key], f"{m_path}.{metric_key}", result)
            for unknown_key in metrics:
                if unknown_key not in COMPANY_METRIC_UNITS:
                    result.add_error(
                        f"{m_path}.{unknown_key}",
                        f"metrics のキーは {'/'.join(COMPANY_METRIC_UNITS)} のいずれかである"
                        f"（実値: {unknown_key!r}）",
                    )

        _validate_negative_checks(profile.get("negative_checks"), f"{path}.negative_checks", result)
        _validate_recent_news(profile.get("recent_news"), f"{path}.recent_news", result)

        open_questions = profile.get("open_questions")
        if not isinstance(open_questions, list) or not all(isinstance(q, str) for q in open_questions):
            result.add_error(
                f"{path}.open_questions", "open_questions は文字列の配列でなければならない（該当が無ければ空配列）"
            )

        if key not in referenced:
            result.add_warning(path, "この企業プロフィールを参照する result が無い")


def _validate_screening_derivations(
    document: dict, results: Any, valid_lanes: list[str], result: ValidationResult
) -> None:
    """screening.derivations（2.3 専用）を検査する。screening.exploration が残っていれば無視して WARN する。"""
    screening = document.get("screening")
    if not isinstance(screening, dict):
        return  # screening 自体の欠落・型不一致は _validate_screening が既に報告している。

    if screening.get("exploration") is not None:
        result.add_warning(
            "screening.exploration", "2.3 では exploration は無視される（screening.derivations を使う）"
        )

    path = "screening.derivations"
    derivations = screening.get("derivations")
    if not isinstance(derivations, dict):
        result.add_error(path, "derivations はオブジェクトが必須である")
        return

    performed = derivations.get("performed")
    if not isinstance(performed, bool):
        result.add_error(f"{path}.performed", "performed は真偽値が必須である")
        return

    lanes_field = derivations.get("lanes")
    if not isinstance(lanes_field, list):
        result.add_error(f"{path}.lanes", "lanes は配列が必須である")
        return

    items = results if isinstance(results, list) else []
    seen: list[str] = []
    for i, entry in enumerate(lanes_field):
        e_path = f"{path}.lanes[{i}]"
        if not isinstance(entry, dict):
            result.add_error(e_path, "lanes の各要素はオブジェクトでなければならない")
            continue
        lane = entry.get("lane")
        if lane not in DERIVATION_LANES:
            result.add_error(
                f"{e_path}.lane", f"lane は {'/'.join(DERIVATION_LANES)} のいずれかである（実値: {lane!r}）"
            )
            continue
        if lane in seen:
            result.add_error(f"{e_path}.lane", f"lane が重複している: {lane}")
            continue
        seen.append(lane)

        actual_results = sum(
            1
            for r in items
            if isinstance(r, dict) and r.get("search_set") == "derived" and r.get("lane") == lane
        )
        actual_apply = sum(
            1
            for r in items
            if isinstance(r, dict)
            and r.get("search_set") == "derived"
            and r.get("lane") == lane
            and r.get("classification") == "apply_candidate"
        )
        result_count = entry.get("result_count")
        if isinstance(result_count, bool) or not isinstance(result_count, int):
            result.add_error(
                f"{e_path}.result_count", f"result_count は整数でなければならない（実値: {result_count!r}）"
            )
        elif result_count != actual_results:
            result.add_error(
                f"{e_path}.result_count",
                f"実際の件数（{actual_results}件）と一致しない（記載: {result_count!r}）",
            )
        apply_count = entry.get("apply_candidate_count")
        if isinstance(apply_count, bool) or not isinstance(apply_count, int):
            result.add_error(
                f"{e_path}.apply_candidate_count",
                f"apply_candidate_count は整数でなければならない（実値: {apply_count!r}）",
            )
        elif apply_count != actual_apply:
            result.add_error(
                f"{e_path}.apply_candidate_count",
                f"実際の件数（{actual_apply}件）と一致しない（記載: {apply_count!r}）",
            )

    missing = [l for l in valid_lanes if l not in seen]
    extra = [l for l in seen if l not in valid_lanes]
    if missing:
        result.add_error(path, f"search_sets.derivations にあるレーンが欠落している: {', '.join(missing)}")
    if extra:
        result.add_error(path, f"search_sets.derivations に無いレーンがある: {', '.join(extra)}")

    if performed and not valid_lanes:
        result.add_error(f"{path}.performed", "performed が true だが派生レーンが無い")
    if not performed and (valid_lanes or lanes_field):
        result.add_error(f"{path}.performed", "performed が false なのに派生レーン・lanes を記録している")


def _validate_search_log_derivation_link(document: dict, results: Any, result: ValidationResult) -> None:
    """派生レーンの求人があるのに search_log に同じレーンのクエリが無い場合を検査する（2.3）。

    2.2 の _validate_search_log_exploration_link を、レーンごとに一般化したもの。
    ERROR はレーンごとに1件だけ報告する。1レーンのクエリが上限（_MAX_QUERIES_PER_LANE）を
    超えていれば WARN にする。
    """
    log = document.get("search_log")
    log_lane_counts: dict[str, int] = {}
    if isinstance(log, list):
        for entry in log:
            if isinstance(entry, dict) and entry.get("search_set") == "derived":
                lane = entry.get("lane")
                if _is_nonempty_str(lane):
                    log_lane_counts[lane] = log_lane_counts.get(lane, 0) + 1

    result_lanes: set[str] = set()
    if isinstance(results, list):
        result_lanes = {
            item.get("lane")
            for item in results
            if isinstance(item, dict)
            and item.get("search_set") == "derived"
            and _is_nonempty_str(item.get("lane"))
        }
    for lane in sorted(result_lanes):
        if log_lane_counts.get(lane, 0) == 0:
            result.add_error(
                "search_log",
                f"search_set が derived で lane が {lane} の result があるが、search_log に同じ lane の"
                "要素が無い。派生レーンの求人はそのレーンのクエリからしか採用できない",
            )

    for lane, count in log_lane_counts.items():
        if count > _MAX_QUERIES_PER_LANE:
            result.add_warning("search_log", f"lane {lane} のクエリが{_MAX_QUERIES_PER_LANE}本を超えている（{count}本）")


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

    improvement_axes = _validate_improvement_axes(document, valid_mode, version, result)

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
            _validate_result_item(item, i, valid_mode, version, improvement_axes, result)

    valid_lanes: list[str] = []
    if version == _V23_SCHEMA_VERSION:
        valid_lanes = _validate_search_sets_v23(document, valid_mode, result)

    _validate_search_log(document, version, valid_lanes, result)

    if version in _SCREENING_SCHEMA_VERSIONS:
        if isinstance(results, list):
            for i, item in enumerate(results):
                _validate_v2_result_item(item, i, result)
        _validate_screening(document, result)
        if profile is not None:
            _validate_threshold_refs(document, profile, result)

    if version == _V22_SCHEMA_VERSION:
        _validate_search_sets(document, valid_mode, result)
        search_sets = document.get("search_sets")
        exploration_defined = isinstance(search_sets, dict) and search_sets.get("exploration") is not None
        if isinstance(results, list):
            for i, item in enumerate(results):
                _validate_v22_result_item(item, i, exploration_defined, result)
        _validate_screening_exploration(document, results, result)
        _validate_search_log_exploration_link(document, results, result)

    if version == _V23_SCHEMA_VERSION:
        company_profiles = document.get("company_profiles")
        if isinstance(results, list):
            for i, item in enumerate(results):
                _validate_v23_result_item(item, i, valid_lanes, company_profiles, result)
        _validate_company_profiles(document, results, result)
        _validate_screening_derivations(document, results, valid_lanes, result)
        _validate_search_log_derivation_link(document, results, result)

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
