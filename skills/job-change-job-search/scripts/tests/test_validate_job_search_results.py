"""validate_job_search_results.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_job_search_results
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_job_search_results as vj  # noqa: E402


# --- 検証済みフィクスチャ（1.0 → 2.3）----------------------------------------


def _valid_fuzzy() -> dict:
    """ERROR 0件・WARN 0件になる 1.0 の fuzzy を返す。"""
    return {
        "schema_version": "1.0",
        "search_id": "20260717-remote-saas-be",
        "mode": "fuzzy",
        "executed_at": "2026-07-17",
        "conditions": {"roles": ["バックエンドエンジニア"], "salary_min": 6000000, "remote_policy": "リモート中心"},
        "results": [
            {
                "title": "バックエンドエンジニア（SaaS）",
                "company_name": "架空テック株式会社",
                "url": "https://example.com/jobs/1",
                "source_site": "求人ボックス",
                "salary_range": "600万〜850万円",
                "location": "東京都（フルリモート可）",
                "remote_policy": "フルリモート",
                "annual_holidays": 125,
                "match_notes": "年収下限・リモート条件に合致する。",
                "quote": "【給与】年収600万〜850万円　【休日】年間休日125日",
            }
        ],
        "coverage_notes": "求人ボックスの検索結果1ページ目を対象とした。",
        "open_questions": [],
    }


def _valid_similar_better() -> dict:
    """ERROR 0件・WARN 0件になる 1.0 の similar_better を返す。"""
    doc = _valid_fuzzy()
    doc.update(search_id="20260717-better-than-cloudworks", mode="similar_better",
               baseline={"slug": "kakuu-cloudworks"})
    doc["results"][0]["better_points"] = ["年収レンジの下限が100万円高い"]
    return doc


def _duty_items(build: int = 4, coordinate: int = 1) -> list[dict]:
    items = [{"quote": f"構築業務{i}", "category": "build"} for i in range(build)]
    return items + [{"quote": f"調整業務{i}", "category": "coordinate"} for i in range(coordinate)]


def _observation(axis: str, stated: bool = True, value=1, **extra) -> dict:
    entry = {"axis": axis, "stated": stated, "value": value, "value_text": None,
             "quote": "掲載ページからの引用" if stated else None}
    entry.update(extra)
    return entry


def _observations(duty_items: list[dict]) -> list[dict]:
    ratios = vj._duty_ratios(duty_items)
    hands_on, coordination = ratios if ratios else (None, None)
    return [
        _observation("remote_certainty", value="guaranteed"),
        _observation("overtime_hours", value=8),
        _observation("annual_holidays", value=128),
        _observation("oncall_load", value="none_stated"),
        _observation("hands_on_ratio", stated=ratios is not None, value=hands_on),
        _observation("coordination_ratio", stated=ratios is not None, value=coordination),
        _observation("experience_distance", value=None, value_text="必須要件の引用文",
                     required_experience=["AWS を用いたインフラ構築の実務経験3年以上"], job_family="インフラエンジニア"),
        _observation("salary_condition", value=6500000),
    ]


def _judgements(**overrides) -> list[dict]:
    """8軸の判定。既定は remote_certainty・overtime_hours が must、他は want、experience_distance だけ none/unknown。"""
    levels = {"remote_certainty": "must", "overtime_hours": "must"}
    entries = []
    for axis in vj.SCREENING_AXES:
        level, verdict = levels.get(axis, "want"), "meets"
        if axis == "experience_distance":
            level, verdict = "none", "unknown"
        if axis in overrides:
            level, verdict = overrides[axis]
        entries.append({"axis": axis, "level": level, "judgement": verdict,
                        "threshold_ref": None if level == "none" else f"ref-{axis}",
                        "rationale": "観測値としきい値を対比した根拠"})
    return entries


def _result_item(classification: str = "apply_candidate", **overrides) -> dict:
    duty_items = _duty_items()
    return {
        "title": "クラウドインフラエンジニア",
        "company_name": "架空アトラス株式会社",
        "url": "https://example.com/jobs/1",
        "source_site": "求人ボックス",
        "salary_range": "650万〜900万円",
        "location": "東京都（フルリモート）",
        "remote_policy": "フルリモート勤務制度あり",
        "annual_holidays": 128,
        "match_notes": "条件を満たす",
        "better_points": [],
        "quote": "年収650万〜900万円／フルリモート勤務制度あり",
        "duty_items": duty_items,
        "axis_observations": _observations(duty_items),
        "axis_judgements": _judgements(**overrides),
        "classification": classification,
        "classification_reasons": [{"axis": "remote_certainty", "reason": "必須条件を満たす"}],
        "classification_override": None,
        "slug": None,
    }


def _screening(items: list[dict], recommendation: str = "応募推奨あり") -> dict:
    counts = {name: sum(1 for i in items if i["classification"] == name) for name in vj.CLASSIFICATIONS}
    counts["total"] = len(items)
    summary = []
    for axis in vj.SCREENING_AXES:
        verdicts = [j["judgement"] for i in items for j in i["axis_judgements"] if j["axis"] == axis]
        summary.append({"axis": axis, "not_meets": verdicts.count("not_meets"), "unknown": verdicts.count("unknown")})
    return {
        "screened_at": "2026-07-25",
        "profile_schema_version": "2.0",
        "axes_source": "job_change_axis.conditions",
        "counts": counts,
        "recommendation": recommendation,
        "rationale": "必須条件を満たす求人がある",
        "unmet_axis_summary": summary,
        "current_employer_exclusion": {"performed": True, "excluded_count": 0, "method": "在職中エントリと company_name を照合した"},
    }


def _valid_v2(items: list[dict] | None = None, recommendation: str = "応募推奨あり") -> dict:
    items = [_result_item()] if items is None else items
    document = _valid_fuzzy()
    document.update(schema_version="2.0", results=items, screening=_screening(items, recommendation))
    return document


def _search_log() -> list[dict]:
    return [{"query": "データサイエンティスト 東京都 フルリモート", "url": "https://example.com/search/1",
             "fetched_at": "2026-07-25", "hit_count": 42, "adopted_count": 2, "source": "求人ボックス",
             "search_set": "primary"}]


def _comparison(overall: str = "not_better", **relations: str) -> dict:
    """6軸の軸別比較を作る。既定は全軸 same。"""
    axes = []
    for axis in vj.BASELINE_COMPARISON_AXES:
        relation = relations.get(axis, "same")
        entry = {"axis": axis, "relation": relation}
        if relation != "unknown":
            entry.update(baseline_value="基準求人の値", candidate_value="候補求人の値", quote="掲載ページからの引用")
        axes.append(entry)
    return {"axes": axes, "overall": overall}


def _valid_v21(items: list[dict] | None = None, recommendation: str = "応募推奨あり") -> dict:
    document = _valid_v2(items, recommendation)
    document.update(schema_version="2.1", search_log=_search_log())
    return document


def _valid_v21_similar_better(comparison: dict | None = None, improvement_axes: list[str] | None = None) -> dict:
    item = _result_item()
    item["better_points"] = ["年収レンジの下限が100万円高い"]
    item["baseline_comparison"] = _comparison("better", salary_condition="higher") if comparison is None else comparison
    document = _valid_v21([item])
    document.update(mode="similar_better", baseline={"slug": "kakuu-cloudworks"},
                    improvement_axes=["salary_condition", "annual_holidays"] if improvement_axes is None else improvement_axes)
    return document


def _v22_result_item(search_set: str = "primary", role_match: str = "same", **overrides) -> dict:
    item = _result_item(**overrides)
    item.update(search_set=search_set, role_match=role_match)
    return item


def _valid_v22(items: list[dict] | None = None, recommendation: str = "応募推奨あり") -> dict:
    """ERROR 0件・WARN 0件の 2.2。探索集合は0件で実施済みとし、exploration の result があれば対応する search_log を足す。"""
    items = [_v22_result_item()] if items is None else items
    document = _valid_v21(items, recommendation)
    document.update(schema_version="2.2", search_sets={
        "primary": {"roles": ["インフラエンジニア"], "salary_min": 6000000},
        "exploration": {"roles": ["SRE"], "industries": None, "dropped_conditions": ["industries"],
                        "rationale": "業界の指定は選好であるため探索集合では外した"},
    })
    document["screening"]["exploration"] = {"performed": True, "result_count": 0, "apply_candidate_count": 0}
    if any(i.get("search_set") == "exploration" for i in items):
        document["search_log"].append({"query": "site:herp.careers SRE 東京都", "url": None, "fetched_at": "2026-07-25",
                                       "hit_count": None, "adopted_count": 1, "source": "WebSearch",
                                       "search_set": "exploration"})
    return document


def _v22_explore(log: bool = True, counts=(1, 1)) -> dict:
    """探索集合の result を1件持つ 2.2。log=False で探索集合の search_log を外す。"""
    document = _valid_v22([_v22_result_item("exploration", "adjacent")])
    document["screening"]["exploration"] = {"performed": True, "result_count": counts[0],
                                            "apply_candidate_count": counts[1]}
    if not log:
        document["search_log"] = [e for e in document["search_log"] if e.get("search_set") != "exploration"]
    return document


def _null_metric(unit: str) -> dict:
    return {"value": None, "unit": unit, "source_url": None, "grade": None, "as_of": None,
            "note": "ログイン必須の一次情報のため未取得"}


def _real_metric(value, unit: str, as_of: str = "2026-03") -> dict:
    return {"value": value, "unit": unit, "source_url": "https://example.com/ir/yuho.pdf", "grade": "A", "as_of": as_of}


def _valid_company_profile(name: str) -> dict:
    """ERROR 0件・WARN 0件の company_profiles[key]。9軸のうち2軸だけ実測値で、残りは null＋note。"""
    metrics = {key: _null_metric(unit) for key, unit in vj.COMPANY_METRIC_UNITS.items()}
    metrics["compensation_level"] = _real_metric(6800000, "円")
    metrics["annual_holidays"] = _real_metric(125, "日")
    return {
        "name": name,
        "aliases": [],
        "official_url": "https://example.com",
        "careers_url": "https://example.com/careers",
        "hq_location": "東京都",
        "industry": "SaaS",
        "business_summary": {"text": "SaaS型の業務システムを開発する企業である。",
                             "quote": "当社はSaaS型の業務システムを開発しています。",
                             "source_url": "https://example.com/about", "grade": "A"},
        "basics": {k: {"value": None, "source_url": None, "grade": None, "as_of": None, "note": "未取得"}
                   for k in vj.COMPANY_BASICS_KEYS},
        "metrics": metrics,
        "negative_checks": {"labor_law_violation_list": {"checked": True, "hit": False,
                                                          "source_url": "https://www.mhlw.go.jp/kinkyu/151106.html",
                                                          "as_of": "2026-07-01"}},
        "recent_news": [{"headline": "新オフィス開設のお知らせ", "date": "2026-06-01",
                         "source_url": "https://example.com/news/1", "grade": "A"}],
        "open_questions": [],
    }


def _derivation(lane: str = "better_salary", salary_min: int = 7500000) -> dict:
    return {"lane": lane, "roles": ["インフラエンジニア"], "industries": None, "salary_min": salary_min,
            "location": None, "remote_policy": None, "employment_type": None,
            "changed_conditions": ["salary_min"], "rationale": "年収を優先して条件を緩めた派生レーン"}


def _v23_result_item(search_set: str = "primary", lane: str | None = None, role_match: str = "same",
                     company_name: str = "架空アトラス株式会社") -> dict:
    item = _result_item()
    item.update(company_name=company_name, search_set=search_set, role_match=role_match,
                company_key=vj.normalize_company_key(company_name))
    if lane is not None:
        item["lane"] = lane
    return item


def _valid_v23(items: list[dict] | None = None) -> dict:
    """ERROR 0件・WARN 0件の 2.3。primary 1件と better_salary レーンの derived 1件を持つ。"""
    if items is None:
        items = [_v23_result_item(),
                 _v23_result_item("derived", "better_salary", "adjacent", "架空クラウド株式会社")]
    document = _valid_v21(items)
    lanes: dict[str, dict] = {}
    for item in items:
        if item.get("search_set") == "derived":
            counts = lanes.setdefault(item["lane"], {"lane": item["lane"], "result_count": 0, "apply_candidate_count": 0})
            counts["result_count"] += 1
            counts["apply_candidate_count"] += item["classification"] == "apply_candidate"
    primary_query = dict(_search_log()[0], search_set="primary")
    derived_query = dict(primary_query, search_set="derived", lane="better_salary")
    document.update(
        schema_version="2.3",
        search_sets={"primary": {"roles": ["インフラエンジニア"], "salary_min": 6000000},
                     "derivations": [_derivation()]},
        search_log=[primary_query, derived_query],
        company_profiles={vj.normalize_company_key(n): _valid_company_profile(n)
                          for n in sorted({i["company_name"] for i in items})},
    )
    document["screening"]["derivations"] = {"performed": bool(lanes), "lanes": list(lanes.values())}
    return document


def _v23_no_lanes(performed: bool = False) -> dict:
    """派生レーンの無い 2.3。performed を変えて矛盾した記録も作れる。"""
    document = _valid_v23([_v23_result_item()])
    document["search_sets"]["derivations"] = []
    document["search_log"] = [e for e in document["search_log"] if e["search_set"] == "primary"]
    document["screening"]["derivations"] = {"performed": performed, "lanes": []}
    return document


def _profile_with_pii() -> dict:
    return {
        "schema_version": "1.1",
        "basic": {"current_role": "エンジニア", "name": "山田太郎"},
        "career_history": [
            {"company": "架空プロダクツ株式会社", "period": "2021-04〜現在", "role": "エンジニア"},
            {"company": "架空システムズ株式会社", "period": "2018-04〜2021-03", "role": "エンジニア"},
        ],
        "job_change_axis": {"reasons": ["裁量拡大"]},
        "salary": {"current": 5500000, "desired": 7000000},
    }


# --- 表駆動の変更子 ------------------------------------------------------------


def _set(*args):
    """_set(キー..., 値): doc の入れ子の位置へ値を入れる変更子を返す。"""
    *path, value = args

    def mutate(doc):
        cur = doc
        for key in path[:-1]:
            cur = cur[key]
        cur[path[-1]] = value

    return mutate


def _del(*path):
    def mutate(doc):
        cur = doc
        for key in path[:-1]:
            cur = cur[key]
        del cur[path[-1]]

    return mutate


def _all(*mutators):
    def mutate(doc):
        for m in mutators:
            m(doc)

    return mutate


def _noop(doc):
    return None


def _obs(axis: str) -> tuple:
    return ("results", 0, "axis_observations", vj.SCREENING_AXES.index(axis))


def _jdg(axis: str) -> tuple:
    return ("results", 0, "axis_judgements", vj.SCREENING_AXES.index(axis))


_K = vj.normalize_company_key("架空アトラス株式会社")


def _prof(*path) -> tuple:
    return ("company_profiles", _K, *path)


def _ri(value=100, **kw) -> dict:
    entry = {"value": value, "source_url": "https://example.com", "grade": "A", "as_of": None}
    entry.update(kw)
    return entry


def _v2_excluded(recommendation: str) -> dict:
    return _valid_v2([_result_item("excluded", remote_certainty=("must", "not_meets"))], recommendation)


def _sb_cmp(mutate=None):
    """salary_condition だけ higher の similar_better。軸別比較を mutate で壊せる。"""
    def factory():
        comparison = _comparison("better", salary_condition="higher")
        if mutate:
            mutate(comparison)
        return _valid_v21_similar_better(comparison)

    return factory


def _validate(base, mutate):
    document = base()
    replaced = mutate(document)
    return vj.validate(document if replaced is None else replaced, pii_terms=[])


# --- ERROR 規則（ラベル, 基準フィクスチャ, 変更子, 期待する部分文字列）-------------

_ERROR_ROWS = [
    # 1.0: 必須・型・列挙・書式
    ("root が object でない", _valid_fuzzy, lambda d: ["x"], "(root)"),
    ("必須の文字列（代表）", _valid_fuzzy, _del("schema_version"), "schema_version"),
    ("search_id の書式", _valid_fuzzy, _set("search_id", "20260717-リモート"), "search_id"),
    ("mode の列挙", _valid_fuzzy, _set("mode", "broad"), "mode"),
    ("conditions の型", _valid_fuzzy, _set("conditions", "リモート"), "conditions"),
    ("results の型", _valid_fuzzy, _set("results", {}), "results"),
    ("result の必須文字列（代表）", _valid_fuzzy, _del("results", 0, "title"), "title"),
    ("result.url は http 始まり", _valid_fuzzy, _set("results", 0, "url", "www.example.com/jobs/1"), "results[0].url"),
    ("null 許容文字列の型（代表）", _valid_fuzzy, _set("results", 0, "salary_range", 600), "salary_range"),
    ("annual_holidays は bool 不可", _valid_fuzzy, _set("results", 0, "annual_holidays", True), "annual_holidays"),
    ("better_points の型", _valid_similar_better, _set("results", 0, "better_points", "年収が高い"), "better_points"),
    ("baseline.slug の書式", _valid_similar_better, _set("baseline", {"slug": "Kakuu_Cloud"}), "baseline.slug"),
    ("baseline は url か slug が必要", _valid_similar_better, _set("baseline", {}), "url または slug"),
    # 2.0: 観測層
    ("2.0 は screening が必須", _valid_v2, _del("screening"), "screening"),
    ("観測の軸が欠落", _valid_v2, lambda d: d["results"][0]["axis_observations"].pop() and None, "欠落"),
    ("観測の軸が重複", _valid_v2, _set(*_obs("overtime_hours"), "axis", "remote_certainty"), "重複"),
    ("stated=true は quote 必須", _valid_v2, _set(*_obs("remote_certainty"), "quote", ""), "掲載ページからの引用"),
    ("stated=true で value が null なら value_text 必須", _valid_v2,
     _all(_set(*_obs("overtime_hours"), "value", None), _set(*_obs("overtime_hours"), "value_text", None)), "value_text"),
    ("duty_items の category 列挙", _valid_v2,
     lambda d: d["results"][0]["duty_items"].append({"quote": "x", "category": "nope"}), "category"),
    ("比率は duty_items 3件以上が必要", _valid_v2,
     _set("results", 0, "duty_items", [{"quote": "構築", "category": "build"}]), "件未満"),
    ("比率は duty_items から再計算して照合", _valid_v2, _set(*_obs("hands_on_ratio"), "value", 0.1), "再計算"),
    ("列挙軸の値域", _valid_v2, _set(*_obs("remote_certainty"), "value", "banana"), "guaranteed"),
    ("stated=false でも値域を検査", _valid_v2,
     _all(_set(*_obs("oncall_load"), "stated", False), _set(*_obs("oncall_load"), "value", "banana"),
          _set(*_obs("oncall_load"), "quote", None)), "none_stated/exists"),
    ("数値軸は bool 不可", _valid_v2, _set(*_obs("annual_holidays"), "value", True), "数値でなければならない"),
    ("数値軸の下限", _valid_v2, _set(*_obs("overtime_hours"), "value", -5), "範囲"),
    ("比率軸の上限", _valid_v2, _set(*_obs("hands_on_ratio"), "value", 1.5), "範囲"),
    ("experience_distance は value が null 固定", _valid_v2, _set(*_obs("experience_distance"), "value", "near"), "null 固定"),
    ("experience_distance は required_experience 必須", _valid_v2,
     _del(*_obs("experience_distance"), "required_experience"), "required_experience"),
    ("experience_distance は job_family 必須", _valid_v2, _set(*_obs("experience_distance"), "job_family", ""), "job_family"),
    # 2.0: 判定層
    ("stated=false の軸は判定できない", _valid_v2,
     _all(_set(*_obs("annual_holidays"), "stated", False), _set(*_obs("annual_holidays"), "value", None),
          _set(*_obs("annual_holidays"), "quote", None)), "記載が無い軸"),
    ("value が null の軸は判定できない", _valid_v2,
     _all(_set(*_obs("annual_holidays"), "value", None), _set(*_obs("annual_holidays"), "value_text", "多め")),
     "観測値が null"),
    ("must は threshold_ref 必須", _valid_v2, _set(*_jdg("remote_certainty"), "threshold_ref", None), "threshold_ref"),
    ("judgement の列挙（代表）", _valid_v2, _set(*_jdg("remote_certainty"), "judgement", "maybe"), "judgement"),
    ("分類は軸判定から導出した値と一致", lambda: _valid_v2([_result_item("apply_candidate", remote_certainty=("must", "not_meets"))]),
     _noop, "classification"),
    ("override は厳しくする方向のみ",
     lambda: _valid_v2([dict(_result_item("apply_candidate", remote_certainty=("must", "not_meets")),
                             classification_override={"from": "excluded", "to": "apply_candidate", "reason": "交渉できる"})]),
     _noop, "厳しくする方向"),
    ("override の from・to は実際の分類と一致",
     lambda: _valid_v2([dict(_result_item("needs_more_research"),
                             classification_override={"from": "excluded", "to": "needs_more_research", "reason": "古い"})],
                       "応募推奨なし"),
     _noop, "一致しない"),
    ("classification_reasons は1件以上", _valid_v2, _set("results", 0, "classification_reasons", []), "classification_reasons"),
    # 2.0: 総括
    ("counts が実際の集計と一致", _valid_v2, _set("screening", "counts", "apply_candidate", 5), "screening.counts"),
    ("応募候補0件で「応募推奨あり」", lambda: _v2_excluded("応募推奨あり"), _noop, "応募推奨なし"),
    ("応募候補ありで「応募推奨なし」", lambda: _valid_v2(recommendation="応募推奨なし"), _noop, "応募推奨あり"),
    ("degraded は「判定不能」だけ", _valid_v2, _set("screening", "axes_source", "degraded"), "判定不能"),
    ("未実施の除外が件数を主張", _valid_v2, _set("screening", "current_employer_exclusion", "performed", False), "件数を主張"),
    ("実施した除外は整数の件数が必要", _valid_v2, _set("screening", "current_employer_exclusion", "excluded_count", None), "excluded_count"),
    ("unmet_axis_summary が実際の集計と一致", _valid_v2, _set("screening", "unmet_axis_summary", 0, "not_meets", 3), "unmet_axis_summary"),
    # 2.1
    ("2.1 は search_log 必須", _valid_v21, _del("search_log"), "search_log"),
    ("search_log が空", _valid_v21, _set("search_log", []), "search_log"),
    ("search_log の型", _valid_v21, _set("search_log", {"query": "x"}), "search_log"),
    ("search_log の必須文字列（代表）", _valid_v21, _set("search_log", 0, "query", ""), "query"),
    ("search_log の null 許容キーは存在が必須", _valid_v21, _del("search_log", 0, "url"), "url"),
    ("search_log.url は http か null", _valid_v21, _set("search_log", 0, "url", "example.com/search"), "url"),
    ("fetched_at は実在日付", _valid_v21, _set("search_log", 0, "fetched_at", "2026-02-30"), "fetched_at"),
    ("fetched_at の書式", _valid_v21, _set("search_log", 0, "fetched_at", "2026/07/25"), "fetched_at"),
    ("件数は0以上", _valid_v21, _set("search_log", 0, "hit_count", -1), "hit_count"),
    ("件数は bool 不可", _valid_v21, _set("search_log", 0, "adopted_count", True), "adopted_count"),
    ("改善軸の語彙", lambda: _valid_v21_similar_better(improvement_axes=["commute"]), _noop, "improvement_axes"),
    ("employment_type は改善軸に取れない",
     lambda: _valid_v21_similar_better(improvement_axes=["salary_condition", "employment_type"]), _noop, "employment_type"),
    ("改善軸の重複",
     lambda: _valid_v21_similar_better(improvement_axes=["salary_condition", "salary_condition"]), _noop, "重複"),
    ("改善軸なしの総合判定", lambda: _valid_v21_similar_better(improvement_axes=[]), _noop, "overall"),
    ("総合判定 better だが改善軸に逆方向",
     lambda: _valid_v21_similar_better(_comparison("better", salary_condition="higher", annual_holidays="lower")),
     _noop, "overall"),
    ("総合判定 better だが改善方向の軸なし", lambda: _valid_v21_similar_better(_comparison("better")), _noop, "overall"),
    ("same でも quote が必須", _sb_cmp(lambda c: c["axes"][1].__setitem__("quote", "")), _noop, "quote"),
    ("unknown 以外は baseline_value が必須", _sb_cmp(lambda c: c["axes"][0].pop("baseline_value")), _noop, "baseline_value"),
    ("軸別比較は6軸そろう", _sb_cmp(lambda c: c["axes"].pop() and None), _noop, "6軸"),
    ("軸別比較の軸が重複", _sb_cmp(lambda c: c["axes"].append(dict(c["axes"][0]))), _noop, "重複"),
    ("relation の列挙", _sb_cmp(lambda c: c["axes"][2].__setitem__("relation", "slightly_higher")), _noop, "relation"),
    ("employment_type は順序の relation 不可", _sb_cmp(lambda c: c["axes"][4].__setitem__("relation", "higher")), _noop, "employment_type"),
    # 2.2
    ("2.2 の search_log は search_set 必須", _valid_v22, _del("search_log", 0, "search_set"), "search_log[0].search_set"),
    ("探索集合の result には探索集合の search_log が必要", lambda: _v22_explore(log=False), _noop, "[ERROR] search_log:"),
    ("search_sets 必須", _valid_v22, _del("search_sets"), "search_sets"),
    ("search_sets.primary 必須", _valid_v22, _del("search_sets", "primary"), "search_sets.primary"),
    ("exploration は object か null", _valid_v22, _set("search_sets", "exploration", "SRE"), "search_sets.exploration"),
    ("exploration.roles は文字列の配列（代表）", _valid_v22, _set("search_sets", "exploration", "roles", "SRE"), "roles"),
    ("2.2 の result.search_set の語彙", _valid_v22, _set("results", 0, "search_set", "tertiary"), "results[0].search_set"),
    ("2.2 は derived 不可", _valid_v22, _set("results", 0, "search_set", "derived"), "results[0].search_set"),
    ("exploration の result には search_sets.exploration が必要", _valid_v22,
     _all(_set("search_sets", "exploration", None), _set("results", 0, "search_set", "exploration")),
     "search_sets.exploration が null"),
    ("role_match の列挙", _valid_v22, _set("results", 0, "role_match", "opposite"), "role_match"),
    ("related_info のキー", _valid_v22, _set("results", 0, "related_info", {"headcount": _ri(1)}), "related_info"),
    ("related_info は値があれば出典が必要", _valid_v22,
     _set("results", 0, "related_info", {"employee_count": _ri(source_url=None)}), "source_url"),
    ("related_info の bool は listed のみ", _valid_v22,
     _set("results", 0, "related_info", {"employee_count": _ri(True)}), "value"),
    ("related_info.as_of の書式", _valid_v22,
     _set("results", 0, "related_info", {"employee_count": _ri(as_of="2026/03")}), "as_of"),
    ("related_info の必須キー", _valid_v22,
     _set("results", 0, "related_info", {"employee_count": {"value": 100, "source_url": "https://example.com", "grade": "A"}}),
     "as_of"),
    ("related_info の各値は object", _valid_v22, _set("results", 0, "related_info", {"employee_count": 320}), "各値はオブジェクト"),
    ("screening.exploration 必須", _valid_v22, _del("screening", "exploration"), "screening.exploration"),
    ("exploration.performed は bool", _valid_v22, _set("screening", "exploration", "performed", "yes"), "performed"),
    ("exploration.result_count の集計", lambda: _v22_explore(counts=(0, 1)), _noop, "result_count"),
    ("exploration.apply_candidate_count の集計", lambda: _v22_explore(counts=(1, 0)), _noop, "apply_candidate_count"),
    ("exploration の件数は bool 不可", lambda: _v22_explore(counts=(True, 1)), _noop, "result_count は整数"),
    ("未実施なら件数は null", _valid_v22,
     _all(_set("search_sets", "exploration", None),
          _set("screening", "exploration", {"performed": False, "result_count": 0, "apply_candidate_count": None})),
     "result_count"),
    ("未実施でも件数キーは必須", _valid_v22,
     _all(_set("search_sets", "exploration", None), _set("screening", "exploration", {"performed": False})), "必須である"),
    ("探索集合があるのに未実施", _valid_v22,
     _set("screening", "exploration", {"performed": False, "result_count": None, "apply_candidate_count": None}),
     "探索集合があるのに"),
    # 2.3
    ("derivations 必須", _valid_v23, _del("search_sets", "derivations"), "search_sets.derivations"),
    ("2.3 は exploration 不可", _valid_v23, _set("search_sets", "exploration", {"roles": []}), "2.3 では derivations"),
    ("lane の重複", _valid_v23, lambda d: d["search_sets"]["derivations"].append(_derivation()), "重複している"),
    ("派生の salary_min は primary を下回れない", _valid_v23, _set("search_sets", "derivations", 0, "salary_min", 1000000), "salary_min"),
    ("changed_conditions は1件以上", _valid_v23, _set("search_sets", "derivations", 0, "changed_conditions", []), "changed_conditions"),
    ("derived の result は lane 必須", _valid_v23, _del("results", 1, "lane"), "results[1].lane"),
    ("primary の result は lane 不可", _valid_v23, _set("results", 0, "lane", "better_salary"), "results[0].lane"),
    ("2.3 の result.search_set の語彙", _valid_v23, _set("results", 0, "search_set", "exploration"), "results[0].search_set"),
    ("派生レーンの result には同じ lane の search_log が必要", _valid_v23,
     lambda d: d.__setitem__("search_log", [e for e in d["search_log"] if e.get("search_set") != "derived"]),
     "[ERROR] search_log:"),
    ("derived の search_log は lane 必須", _valid_v23, _del("search_log", 1, "lane"), "search_log[1].lane"),
    ("primary の search_log は lane 不可", _valid_v23, _set("search_log", 0, "lane", "better_salary"), "search_log[0].lane"),
    ("company_key 必須", _valid_v23, _del("results", 0, "company_key"), "company_key"),
    ("company_key は company_profiles に存在", _valid_v23, _set("results", 0, "company_key", "no-such-company"),
     "company_profiles に存在するキー"),
    ("company_profiles 必須", _valid_v23, _del("company_profiles"), "company_profiles"),
    ("プロフィールのキーは name か aliases の正規化結果", _valid_v23, _set(*_prof("name"), "別会社株式会社"), "キーは name または aliases"),
    ("metrics の軸が欠落", _valid_v23, _del(*_prof("metrics", "equity_ratio")), "metrics.equity_ratio"),
    ("metrics の軸の語彙", _valid_v23, _set(*_prof("metrics", "headcount_growth"), _real_metric(1, "%", "2026")),
     "metrics.headcount_growth"),
    ("metrics の単位", _valid_v23, _set(*_prof("metrics", "annual_holidays", "unit"), "件"), "metrics.annual_holidays.unit"),
    ("符号なしの軸は負数不可", _valid_v23, _set(*_prof("metrics", "annual_holidays", "value"), -1), "負の値"),
    ("比率の軸は0〜100", _valid_v23, _set(*_prof("metrics", "paid_leave_rate"), _real_metric(120, "%", "2026")), "0〜100の範囲"),
    ("労働法令違反ありは note 必須", _valid_v23,
     _set(*_prof("negative_checks", "labor_law_violation_list", "hit"), True), "note"),
    ("未確認なら hit は null", _valid_v23,
     _set(*_prof("negative_checks", "labor_law_violation_list", "checked"), False), "hit"),
    ("recent_news の日付", _valid_v23, _set(*_prof("recent_news", 0, "date"), "2026/06/01"), "recent_news"),
    ("screening.derivations 必須", _valid_v23, _del("screening", "derivations"), "screening.derivations"),
    ("レーン別の件数の集計", _valid_v23, _set("screening", "derivations", "lanes", 0, "result_count", 9), "result_count"),
    ("search_sets のレーンが lanes に必要", _valid_v23, _set("screening", "derivations", "lanes", []), "レーンが欠落している"),
    ("performed=true なのに派生レーンなし", lambda: _v23_no_lanes(True), _noop, "performed が true だが派生レーンが無い"),
    ("performed=false なのにレーンあり", _valid_v23, _set("screening", "derivations", "performed", False), "performed が false"),
]

# --- WARN 規則（ERROR 0件のまま警告が出る）---------------------------------------

_WARN_ROWS = [
    ("similar_better で baseline なし", _valid_similar_better, _del("baseline"), "baseline"),
    ("similar_better で better_points なし", _valid_similar_better, _del("results", 0, "better_points"), "better_points"),
    ("fuzzy で better_points", _valid_fuzzy, _set("results", 0, "better_points", ["年収が高い"]), "better_points"),
    ("results が空", _valid_fuzzy, _set("results", []), "results"),
    ("salary_condition を万円単位で書いた疑い", _valid_v2, _set(*_obs("salary_condition"), "value", 650), "万円単位"),
    ("全件が除外候補", lambda: _v2_excluded("応募推奨なし"), _noop, "全件が除外候補"),
    ("similar_better で軸別比較なし", _valid_v21_similar_better, _del("results", 0, "baseline_comparison"), "baseline_comparison"),
    ("fuzzy で軸別比較", _valid_v21,
     _set("results", 0, "baseline_comparison", _comparison("better", salary_condition="higher")), "baseline_comparison"),
    ("similar_better で改善軸なし", _valid_v21_similar_better,
     _all(_del("improvement_axes"), _del("results", 0, "baseline_comparison")), "improvement_axes"),
    ("fuzzy で改善軸", _valid_v21, _set("improvement_axes", ["salary_condition"]), "improvement_axes"),
    ("fuzzy で探索集合なし", _valid_v22, _set("search_sets", "exploration", None), "偏りの点検を省いている"),
    ("similar_better で探索集合", _valid_v22,
     _all(_set("mode", "similar_better"), _set("baseline", {"slug": "kakuu-cloudworks"})), "search_sets.exploration"),
    ("primary の role_match が different", _valid_v22, _set("results", 0, "role_match", "different"), "role_match"),
    ("fuzzy で派生レーンなし", _v23_no_lanes, _noop, "派生レーンを検索していない"),
    ("1レーンのクエリが上限超過", _valid_v23, lambda d: d["search_log"].extend(dict(d["search_log"][1]) for _ in range(3)), "を超えている"),
    ("company_name とプロフィールが不一致", _valid_v23, _set("results", 0, "company_name", "別の会社株式会社"), "company_key"),
    ("basics が null で note なし", _valid_v23,
     _set(*_prof("basics", "founded_year"), {"value": None, "source_url": None, "grade": None, "as_of": None, "note": ""}),
     "basics.founded_year.note"),
    ("basics のキー不足", _valid_v23, _del(*_prof("basics", "founded_year")), "取得していない基礎情報"),
    ("metrics が null で note なし", _valid_v23, _set(*_prof("metrics", "turnover_rate", "note"), ""), "metrics.turnover_rate.note"),
    ("compensation_level を万円単位で書いた疑い", _valid_v23, _set(*_prof("metrics", "compensation_level", "value"), 680), "万円単位"),
    ("参照されないプロフィール", _valid_v23,
     lambda d: d["company_profiles"].__setitem__("架空未参照", _valid_company_profile("架空未参照")), "参照する result が無い"),
    ("2.3 の related_info に企業基礎情報", _valid_v23,
     _set("results", 0, "related_info", {"employee_count": _ri(300, as_of="2026")}), "company_profiles[].basics"),
    ("2.3 の screening.exploration は無視", _valid_v23,
     _set("screening", "exploration", {"performed": False, "result_count": None, "apply_candidate_count": None}),
     "2.3 では exploration は無視"),
]

# --- 許容される境界（ERROR 0件）--------------------------------------------------

_ACCEPT_ROWS = [
    ("厳しくする方向の override", lambda: _valid_v2([dict(_result_item("needs_more_research"),
     classification_override={"from": "apply_candidate", "to": "needs_more_research", "reason": "掲載が古い"})], "応募推奨なし"), _noop),
    ("未実施の除外は件数 null", _valid_v2,
     _all(_set("screening", "current_employer_exclusion", "performed", False),
          _set("screening", "current_employer_exclusion", "excluded_count", None))),
    ("fetched_at は ISO 8601", _valid_v21, _set("search_log", 0, "fetched_at", "2026-07-25T09:30:00+09:00")),
    ("search_log の null 許容キーは null", _valid_v21,
     lambda d: d["search_log"][0].update(url=None, fetched_at=None, hit_count=None, adopted_count=None)),
    ("unknown の relation は根拠不要",
     lambda: _valid_v21_similar_better(_comparison("better", salary_condition="higher", scope_of_change="unknown")), _noop),
    ("related_info の value が null なら出典検査を省く", _valid_v22,
     _set("results", 0, "related_info", {"employee_count": _ri(None, source_url=None, grade=None)})),
    ("related_info の bool は listed で許容", _valid_v22, _set("results", 0, "related_info", {"listed": _ri(True)})),
    ("related_info.as_of は年のみ可", _valid_v22, _set("results", 0, "related_info", {"employee_count": _ri(as_of="2026")})),
    ("符号付きの軸は負数可", _valid_v23, _set(*_prof("metrics", "revenue_growth"), _real_metric(-5.5, "%", "2026"))),
    ("キーは aliases の正規化結果と一致でも可", _valid_v23,
     _all(_set(*_prof("name"), "株式会社架空アトラスホールディングス"), _set(*_prof("aliases"), ["架空アトラス株式会社"]))),
]


def _v21_ignoring_v22_fields() -> dict:
    document = _valid_v21()
    document["results"][0]["search_set"] = "not-a-real-value"
    del document["search_log"][0]["search_set"]
    return document


def _v23_posting_related_info() -> dict:
    document = _valid_v23()
    document["results"][0]["related_info"] = {"posting_age": _ri(3, source_url="https://example.com/jobs/1", as_of="2026-07")}
    return document


class ValidateTest(unittest.TestCase):
    def test_valid_fixtures_pass_without_errors_or_warnings(self):
        rows = [
            ("1.0 fuzzy", _valid_fuzzy), ("1.0 similar_better", _valid_similar_better),
            ("2.0", _valid_v2), ("2.1", _valid_v21), ("2.1 similar_better", _valid_v21_similar_better),
            ("2.1 は 2.2 の項目を見ない", _v21_ignoring_v22_fields),
            ("2.2", _valid_v22), ("2.2 探索集合の result", _v22_explore),
            ("2.3", _valid_v23), ("2.3 求人単位の related_info", _v23_posting_related_info),
        ]
        for label, build in rows:
            with self.subTest(label):
                result = vj.validate(build(), pii_terms=[])
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_bundled_examples_pass(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        hub_assets = os.path.join(os.path.dirname(base), "job-change-support", "assets")
        # 職歴と転職の軸を CLI と同じ順で重ねる。
        profile = {**vj.load_json(os.path.join(hub_assets, "profile_example.json")),
                   **vj.load_json(os.path.join(hub_assets, "axis_example.json"))}
        for name in ("job_search_results_example.json", "job_search_results_similar_better_example.json"):
            with self.subTest(name):
                document = vj.load_json(os.path.join(base, "assets", name))
                result = vj.validate(document, pii_terms=vj.collect_pii_terms(profile), profile=profile)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_error_rules(self):
        for label, base, mutate, expected in _ERROR_ROWS:
            with self.subTest(label):
                result = _validate(base, mutate)
                self.assertFalse(result.ok)
                self.assertTrue(any(expected in e for e in result.errors), result.errors)

    def test_warn_rules(self):
        for label, base, mutate, expected in _WARN_ROWS:
            with self.subTest(label):
                result = _validate(base, mutate)
                self.assertEqual(result.errors, [])
                self.assertTrue(any(expected in w for w in result.warnings), result.warnings)

    def test_accepted_boundaries(self):
        for label, base, mutate in _ACCEPT_ROWS:
            with self.subTest(label):
                self.assertEqual(_validate(base, mutate).errors, [])

    def test_threshold_refs_against_profile(self):
        def profile_base() -> dict:
            conditions = [{"id": f"ref-{a}", "level": level} for a, level in (
                ("remote_certainty", "must"), ("overtime_hours", "must"), ("annual_holidays", "want"),
                ("oncall_load", "want"), ("hands_on_ratio", "want"), ("coordination_ratio", "want"),
                ("salary_condition", "want"))]
            return {"job_change_axis": {"conditions": conditions, "work_character_preferences": []}}

        def prefs(*items):
            return lambda p, d: p["job_change_axis"].__setitem__("work_character_preferences", list(items))

        def judge(axis, level, ref):
            return lambda p, d: d["results"][0]["axis_judgements"][vj.SCREENING_AXES.index(axis)].update(
                level=level, threshold_ref=ref)

        def chain(*fs):
            return lambda p, d: [f(p, d) for f in fs]

        # (ラベル, profile と doc の変更子, 期待する ERROR。None は ERROR 0件)
        rows = [
            ("実在する参照", lambda p, d: None, None),
            ("実在しない参照", judge("remote_certainty", "must", "ref-does-not-exist"), "存在しない条件"),
            ("必須度の不一致", lambda p, d: p["job_change_axis"]["conditions"][0].update(level="want"), "必須度"),
            ("desire important は want に写る",
             chain(prefs({"trait": "hands_on", "desire": "important"}), judge("hands_on_ratio", "want", "hands_on")), None),
            ("desire neutral は none に写る",
             chain(prefs({"trait": "low_coordination", "desire": "neutral"}), judge("coordination_ratio", "none", None)), None),
            ("desire neutral を want のまま残す",
             chain(prefs({"trait": "low_coordination", "desire": "neutral"}),
                   judge("coordination_ratio", "want", "low_coordination")), "必須度"),
            ("conditions[].axis が must の軸を none に緩める",
             chain(lambda p, d: p["job_change_axis"].__setitem__(
                 "conditions", [{"id": "c", "axis": "remote_certainty", "level": "must"}]),
                 judge("remote_certainty", "none", None)), "必須度"),
            ("want の特性の軸を none に緩める",
             chain(prefs({"trait": "no_oncall", "desire": "important"}), judge("oncall_load", "none", None)), "必須度"),
        ]
        for label, mutate, expected in rows:
            with self.subTest(label):
                profile, document = profile_base(), _valid_v2()
                mutate(profile, document)
                result = vj.validate(document, pii_terms=[], profile=profile)
                if expected is None:
                    self.assertEqual(result.errors, [])
                else:
                    self.assertTrue(any(expected in e for e in result.errors), result.errors)


class CalculationTest(unittest.TestCase):
    def test_derive_baseline_overall(self):
        def axes(**relations):
            return [{"axis": a, "relation": relations.get(a, "same")} for a in vj.BASELINE_COMPARISON_AXES]

        # (ラベル, 軸別の relation, 改善軸, 期待する総合判定)
        rows = [
            ("改善方向が1つで逆方向なし", {"salary_condition": "higher"}, ["salary_condition"], "better"),
            ("改善軸に逆方向", {"salary_condition": "higher", "annual_holidays": "lower"},
             ["salary_condition", "annual_holidays"], "not_better"),
            ("改善軸に無い軸の逆方向は無視", {"salary_condition": "higher", "annual_holidays": "lower"},
             ["salary_condition"], "better"),
            ("unknown は改善に数えない", {"salary_condition": "unknown"}, ["salary_condition"], "not_better"),
            ("残業は少ない方が改善", {"overtime_hours": "lower"}, ["overtime_hours"], "better"),
            ("残業が多いと悪化", {"overtime_hours": "higher"}, ["overtime_hours"], "not_better"),
            ("変更の範囲は狭い方が改善", {"scope_of_change": "lower"}, ["scope_of_change"], "better"),
            ("employment_type は改善軸にならない", {"employment_type": "different"}, ["employment_type"], "not_better"),
        ]
        for label, relations, improvement, expected in rows:
            with self.subTest(label):
                self.assertEqual(vj.derive_baseline_overall(axes(**relations), improvement), expected)

    def test_derive_classification(self):
        def j(level, verdict):
            return {"level": level, "judgement": verdict}

        rows = [
            ("must の not_meets は除外", [j("must", "not_meets"), j("want", "meets")], "excluded"),
            ("must の unknown は要調査", [j("must", "unknown"), j("want", "meets")], "needs_more_research"),
            ("unknown 3件は応募候補", [j("want", "unknown")] * 3, "apply_candidate"),
            ("unknown 4件は要調査", [j("want", "unknown")] * 4, "needs_more_research"),
            ("すべて meets は応募候補", [j("must", "meets"), j("want", "meets")], "apply_candidate"),
        ]
        for label, judgements, expected in rows:
            with self.subTest(label):
                self.assertEqual(vj.derive_classification(judgements), expected)

    def test_duty_ratios(self):
        self.assertIsNone(vj._duty_ratios(_duty_items(build=1, coordinate=1)))
        self.assertEqual(vj._duty_ratios(_duty_items(build=4, coordinate=1)), (0.8, 0.2))

    def test_normalize_company_key(self):
        rows = [
            ("株式会社架空テック", "架空テック"), ("架空テック株式会社", "架空テック"),
            ("架空 テック 株式会社", "架空テック"), ("ACME Corp 株式会社", "acmecorp"),
            ("架空テック（株）", "架空テック"), ("株式会社", ""), (None, ""),
        ]
        for name, expected in rows:
            with self.subTest(name):
                self.assertEqual(vj.normalize_company_key(name), expected)


class PiiTest(unittest.TestCase):
    def test_collect_pii_terms(self):
        employer, name, salary = ("現勤務先名", "架空プロダクツ株式会社"), ("氏名", "山田太郎"), ("現年収", "5500000")

        def profile(mutate=None):
            p = _profile_with_pii()
            if mutate:
                mutate(p)
            return p

        rows = [
            ("在職中の会社だけが現勤務先", profile(), [employer, name, salary]),
            ("在職中が無ければ先頭を現勤務先とみなす",
             profile(lambda p: p["career_history"][0].update(period="2021-04〜2026-06")), [employer, name, salary]),
            ("float の現年収", profile(lambda p: p["salary"].update(current=5500000.0)), [employer, name, salary]),
            ("下限未満の現年収は対象外", profile(lambda p: p["salary"].update(current=5000)), [employer, name]),
            ("bool の現年収は対象外", profile(lambda p: p["salary"].update(current=True)), [employer, name]),
        ]
        for label, p, expected in rows:
            with self.subTest(label):
                self.assertEqual(vj.collect_pii_terms(p), expected)

    def test_lint_detects_leaks(self):
        terms = vj.collect_pii_terms(_profile_with_pii())
        # (ラベル, 基準, 変更子, 期待するラベル)
        rows = [
            ("本文への現勤務先名", _valid_fuzzy, _set("results", 0, "match_notes", "架空プロダクツ株式会社より好条件である。"), "現勤務先名"),
            ("現年収", _valid_fuzzy, _set("conditions", "current_salary", 5500000), "現年収"),
            ("氏名", _valid_fuzzy, _set("conditions", "applicant", "山田太郎"), "氏名"),
            ("search_log のクエリ", _valid_v21, _set("search_log", 0, "query", "架空プロダクツ株式会社 より良い求人"), "現勤務先名"),
            ("company_profiles の open_questions", _valid_v23,
             _set(*_prof("open_questions"), ["架空プロダクツ株式会社より条件が良いか未確認"]), "現勤務先名"),
        ]
        for label, base, mutate, expected in rows:
            with self.subTest(label):
                document = base()
                mutate(document)
                result = vj.validate(document, pii_terms=terms)
                self.assertFalse(result.ok)
                self.assertTrue(any(expected in e for e in result.errors), result.errors)

    def test_lint_passes_clean_documents_and_desired_salary(self):
        terms = vj.collect_pii_terms(_profile_with_pii())
        clean = _valid_fuzzy()
        desired = _valid_fuzzy()
        desired["conditions"]["salary_min"] = 7000000  # 希望年収の下限は許容する
        for label, document in (("匿名化済み", clean), ("希望年収の下限", desired)):
            with self.subTest(label):
                result = vj.validate(document, pii_terms=terms)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_missing_profile_is_reported_as_unverified(self):
        result = vj.validate(_valid_fuzzy())
        self.assertTrue(result.ok)
        self.assertTrue(any("未実施" in w for w in result.warnings))


class CliTest(unittest.TestCase):
    def _main_json(self, argv: list) -> tuple[int, dict]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = vj.main(argv + ["--json"])
        return code, json.loads(out.getvalue())

    def test_exit_codes_and_warnings(self):
        with tempfile.TemporaryDirectory() as d:
            def write(name, obj, encoding="utf-8"):
                path = os.path.join(d, name)
                with open(path, "w", encoding=encoding) as f:
                    json.dump(obj, f, ensure_ascii=False)
                return path

            doc = write("doc.json", _valid_fuzzy())
            invalid = _valid_fuzzy()
            del invalid["mode"]
            leak = _valid_fuzzy()
            leak["results"][0]["match_notes"] = "架空プロダクツ株式会社の同業。"
            salary_leak = _valid_fuzzy()
            salary_leak["results"][0]["match_notes"] = "現年収の 5500000 円を上回る。"
            broken = os.path.join(d, "broken.json")
            with open(broken, "w", encoding="utf-8") as f:
                f.write("{ not valid json ")

            # 職歴だけの profile.json と axis.json に分ける。
            profile = _profile_with_pii()
            axis = {"schema_version": "1.1", "job_change_axis": profile.pop("job_change_axis"),
                    "salary": profile.pop("salary")}
            profile["schema_version"] = "3.0"
            career, axis_path = write("career.json", profile), write("axis.json", axis)
            full_profile = write("profile.json", _profile_with_pii(), encoding="utf-8-sig")

            rows = [
                ("valid", [doc], 0),
                ("invalid", [write("invalid.json", invalid)], 1),
                ("broken JSON", [broken], 1),
                ("UTF-8 BOM", [write("bom.json", _valid_fuzzy(), "utf-8-sig")], 0),
                ("--profile で現勤務先の混入", [write("leak.json", leak), "--profile", full_profile], 1),
                ("--profile で混入なし", [doc, "--profile", full_profile], 0),
                ("--axis が現年収を供給する", [write("salary.json", salary_leak), "--profile", career, "--axis", axis_path], 1),
                ("--axis が object でない", [doc, "--axis", write("list.json", [])], 1),
            ]
            for label, argv, expected in rows:
                with self.subTest(label):
                    self.assertEqual(self._main_json(argv)[0], expected)

            warn_rows = [
                ("職歴だけの profile は軸の欠落を警告", [doc, "--profile", career], "--axis"),
                ("--axis に軸が無いファイル", [doc, "--axis", career], "job_change_axis"),
                ("--axis だけでは PII リントが走らない", [doc, "--axis", axis_path], "PII リントは未実施"),
            ]
            for label, argv, expected in warn_rows:
                with self.subTest(label):
                    code, report = self._main_json(argv)
                    self.assertEqual(code, 0)
                    self.assertTrue(any(expected in w for w in report["warnings"]), report["warnings"])

            code, report = self._main_json([doc])
            self.assertEqual(code, 0)
            self.assertEqual(set(report), {"status", "error_count", "warning_count", "errors", "warnings"})
            self.assertEqual(report["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
