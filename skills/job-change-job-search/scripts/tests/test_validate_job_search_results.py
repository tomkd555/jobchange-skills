"""validate_job_search_results.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_job_search_results
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_job_search_results as vj  # noqa: E402


def _valid_fuzzy() -> dict:
    """ERROR 0件・WARN 0件になる fuzzy モードの結果を返す。"""
    return {
        "schema_version": "1.0",
        "search_id": "20260717-remote-saas-be",
        "mode": "fuzzy",
        "executed_at": "2026-07-17",
        "conditions": {
            "roles": ["バックエンドエンジニア"],
            "industries": ["SaaS"],
            "salary_min": 6000000,
            "remote_policy": "リモート中心",
        },
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
                "quote": "【給与】年収600万〜850万円　【勤務】フルリモート可　【休日】年間休日125日",
            }
        ],
        "coverage_notes": "求人ボックスの検索結果1ページ目を対象とした。",
        "open_questions": [],
    }


def _valid_similar_better() -> dict:
    """ERROR 0件・WARN 0件になる similar_better モードの結果を返す。"""
    return {
        "schema_version": "1.0",
        "search_id": "20260717-better-than-cloudworks",
        "mode": "similar_better",
        "executed_at": "2026-07-17",
        "baseline": {"slug": "kakuu-cloudworks"},
        "conditions": {
            "roles": ["バックエンドエンジニア"],
            "salary_min": 6200000,
            "improve_axes": ["年収", "年間休日"],
        },
        "results": [
            {
                "title": "サーバーサイドエンジニア",
                "company_name": "架空ソフト株式会社",
                "url": "https://example.com/jobs/9",
                "source_site": "Green",
                "salary_range": "700万〜950万円",
                "location": "東京都",
                "remote_policy": "週2出社",
                "annual_holidays": 128,
                "match_notes": "基準求人と同職種で待遇が上回る。",
                "better_points": ["年収レンジの下限が100万円高い", "年間休日が3日多い"],
                "quote": "年収700万〜950万円／年間休日128日／リモート週3",
            }
        ],
        "coverage_notes": "Green の類似求人を対象とした。",
    }


class ValidatePassTest(unittest.TestCase):
    def test_fuzzy_passes_without_warnings(self):
        result = vj.validate(_valid_fuzzy(), pii_terms=[])
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_similar_better_passes_without_warnings(self):
        result = vj.validate(_valid_similar_better(), pii_terms=[])
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_missing_profile_is_reported_as_unverified(self):
        result = vj.validate(_valid_fuzzy())
        self.assertTrue(result.ok)
        self.assertTrue(any("未実施" in w for w in result.warnings))


class RootAndTopLevelErrorTest(unittest.TestCase):
    def test_root_not_object(self):
        result = vj.validate(["not", "object"])
        self.assertFalse(result.ok)

    def test_missing_schema_version(self):
        p = _valid_fuzzy()
        del p["schema_version"]
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("schema_version" in e for e in result.errors))

    def test_missing_search_id(self):
        p = _valid_fuzzy()
        del p["search_id"]
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_id" in e for e in result.errors))

    def test_empty_search_id(self):
        p = _valid_fuzzy()
        p["search_id"] = "  "
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_id" in e for e in result.errors))

    def test_search_id_without_date_prefix(self):
        p = _valid_fuzzy()
        p["search_id"] = "remote-saas-be"
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_id" in e for e in result.errors))

    def test_search_id_with_disallowed_characters(self):
        for value in ("20260717-リモート", "20260717-Remote", "20260717--", "20260717-remote saas"):
            with self.subTest(search_id=value):
                p = _valid_fuzzy()
                p["search_id"] = value
                result = vj.validate(p)
                self.assertFalse(result.ok)
                self.assertTrue(any("search_id" in e for e in result.errors))

    def test_missing_executed_at(self):
        p = _valid_fuzzy()
        del p["executed_at"]
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("executed_at" in e for e in result.errors))

    def test_conditions_not_object(self):
        p = _valid_fuzzy()
        p["conditions"] = "リモート"
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("conditions" in e for e in result.errors))

    def test_results_not_list(self):
        p = _valid_fuzzy()
        p["results"] = {}
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("results" in e for e in result.errors))


class ModeTest(unittest.TestCase):
    def test_invalid_mode(self):
        p = _valid_fuzzy()
        p["mode"] = "broad"
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("mode" in e for e in result.errors))

    def test_missing_mode(self):
        p = _valid_fuzzy()
        del p["mode"]
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("mode" in e for e in result.errors))


class ResultItemErrorTest(unittest.TestCase):
    def test_result_missing_title(self):
        p = _valid_fuzzy()
        del p["results"][0]["title"]
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("title" in e for e in result.errors))

    def test_result_missing_quote(self):
        p = _valid_fuzzy()
        p["results"][0]["quote"] = ""
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("quote" in e for e in result.errors))

    def test_result_bad_url(self):
        p = _valid_fuzzy()
        p["results"][0]["url"] = "www.example.com/jobs/1"
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("url" in e for e in result.errors))

    def test_result_missing_company_name(self):
        p = _valid_fuzzy()
        del p["results"][0]["company_name"]
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("company_name" in e for e in result.errors))

    def test_salary_range_null_is_allowed(self):
        p = _valid_fuzzy()
        p["results"][0]["salary_range"] = None
        result = vj.validate(p)
        self.assertTrue(result.ok)

    def test_salary_range_wrong_type(self):
        p = _valid_fuzzy()
        p["results"][0]["salary_range"] = 600
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("salary_range" in e for e in result.errors))

    def test_better_points_not_list(self):
        p = _valid_similar_better()
        p["results"][0]["better_points"] = "年収が高い"
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("better_points" in e for e in result.errors))


class ModeConsistencyWarnTest(unittest.TestCase):
    def test_similar_better_without_baseline_warns(self):
        p = _valid_similar_better()
        del p["baseline"]
        result = vj.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("baseline" in w for w in result.warnings))

    def test_similar_better_result_without_better_points_warns(self):
        p = _valid_similar_better()
        del p["results"][0]["better_points"]
        result = vj.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("better_points" in w for w in result.warnings))

    def test_fuzzy_with_better_points_warns(self):
        p = _valid_fuzzy()
        p["results"][0]["better_points"] = ["年収が高い"]
        result = vj.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("better_points" in w for w in result.warnings))

    def test_empty_results_warns_but_passes(self):
        p = _valid_fuzzy()
        p["results"] = []
        result = vj.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("results" in w for w in result.warnings))

    def test_baseline_bad_slug(self):
        p = _valid_similar_better()
        p["baseline"] = {"slug": "Kakuu_Cloud"}
        result = vj.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("baseline.slug" in e for e in result.errors))


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


class CollectPiiTermsTest(unittest.TestCase):
    def test_collects_current_employer_name_and_salary(self):
        terms = vj.collect_pii_terms(_profile_with_pii())
        values = [v for _, v in terms]
        self.assertIn("架空プロダクツ株式会社", values)
        self.assertIn("山田太郎", values)
        self.assertIn("5500000", values)

    def test_only_ongoing_employer_is_current(self):
        terms = vj.collect_pii_terms(_profile_with_pii())
        labels = {label: v for label, v in terms}
        current_values = [v for label, v in terms if label == "現勤務先名"]
        self.assertIn("架空プロダクツ株式会社", current_values)
        self.assertNotIn("架空システムズ株式会社", current_values)

    def test_fallback_to_first_when_no_ongoing(self):
        p = _profile_with_pii()
        p["career_history"][0]["period"] = "2021-04〜2026-06"
        terms = vj.collect_pii_terms(p)
        current_values = [v for label, v in terms if label == "現勤務先名"]
        self.assertEqual(current_values, ["架空プロダクツ株式会社"])


class PiiLintTest(unittest.TestCase):
    def test_current_employer_leak_is_error(self):
        doc = _valid_fuzzy()
        doc["results"][0]["match_notes"] = "架空プロダクツ株式会社より好条件である。"
        terms = vj.collect_pii_terms(_profile_with_pii())
        result = vj.validate(doc, pii_terms=terms)
        self.assertFalse(result.ok)
        self.assertTrue(any("現勤務先名" in e for e in result.errors))

    def test_current_salary_leak_is_error(self):
        doc = _valid_fuzzy()
        doc["conditions"]["current_salary"] = 5500000
        terms = vj.collect_pii_terms(_profile_with_pii())
        result = vj.validate(doc, pii_terms=terms)
        self.assertFalse(result.ok)
        self.assertTrue(any("現年収" in e for e in result.errors))

    def test_name_leak_is_error(self):
        doc = _valid_fuzzy()
        doc["conditions"]["applicant"] = "山田太郎"
        terms = vj.collect_pii_terms(_profile_with_pii())
        result = vj.validate(doc, pii_terms=terms)
        self.assertFalse(result.ok)
        self.assertTrue(any("氏名" in e for e in result.errors))

    def test_clean_document_passes_pii_lint(self):
        doc = _valid_fuzzy()
        terms = vj.collect_pii_terms(_profile_with_pii())
        result = vj.validate(doc, pii_terms=terms)
        self.assertTrue(result.ok)

    def test_desired_salary_lower_bound_not_flagged(self):
        doc = _valid_fuzzy()
        doc["conditions"]["salary_min"] = 7000000  # 希望年収の下限は許容
        terms = vj.collect_pii_terms(_profile_with_pii())
        result = vj.validate(doc, pii_terms=terms)
        self.assertTrue(result.ok)


class CliTest(unittest.TestCase):
    def _write_tmp(self, obj, bom: bool = False) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        encoding = "utf-8-sig" if bom else "utf-8"
        with os.fdopen(fd, "w", encoding=encoding) as f:
            json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def test_main_returns_0_on_valid(self):
        path = self._write_tmp(_valid_fuzzy())
        self.assertEqual(vj.main([path]), 0)

    def test_main_returns_1_on_invalid(self):
        p = _valid_fuzzy()
        del p["mode"]
        path = self._write_tmp(p)
        self.assertEqual(vj.main([path]), 1)

    def test_main_returns_1_on_broken_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{ not valid json ")
        self.addCleanup(os.remove, path)
        self.assertEqual(vj.main([path]), 1)

    def test_main_json_flag_valid(self):
        path = self._write_tmp(_valid_fuzzy())
        self.assertEqual(vj.main([path, "--json"]), 0)

    def test_main_returns_0_on_valid_with_bom(self):
        path = self._write_tmp(_valid_fuzzy(), bom=True)
        self.assertEqual(vj.main([path]), 0)

    def test_main_profile_flag_detects_leak(self):
        doc = _valid_fuzzy()
        doc["results"][0]["match_notes"] = "架空プロダクツ株式会社の同業。"
        doc_path = self._write_tmp(doc)
        profile_path = self._write_tmp(_profile_with_pii(), bom=True)
        self.assertEqual(vj.main([doc_path, "--profile", profile_path]), 1)

    def test_main_profile_flag_clean_passes(self):
        doc_path = self._write_tmp(_valid_fuzzy())
        profile_path = self._write_tmp(_profile_with_pii())
        self.assertEqual(vj.main([doc_path, "--profile", profile_path]), 0)


class ResultShapeTest(unittest.TestCase):
    def test_to_dict_shape(self):
        result = vj.validate(_valid_fuzzy())
        d = result.to_dict()
        self.assertEqual(d["status"], "PASS")
        self.assertEqual(d["error_count"], 0)
        self.assertIn("warnings", d)

    def test_immutability_of_input(self):
        p = _valid_similar_better()
        snapshot = copy.deepcopy(p)
        terms = vj.collect_pii_terms(_profile_with_pii())
        vj.validate(p, pii_terms=terms)
        self.assertEqual(p, snapshot)

    def test_collect_pii_terms_does_not_mutate_profile(self):
        profile = _profile_with_pii()
        snapshot = copy.deepcopy(profile)
        vj.collect_pii_terms(profile)
        self.assertEqual(profile, snapshot)


# --- schema_version 2.0（スクリーニング）の検査 -------------------------------


def _duty_items(build: int = 4, coordinate: int = 1) -> list[dict]:
    items = [{"quote": f"構築業務{i}", "category": "build"} for i in range(build)]
    items += [{"quote": f"調整業務{i}", "category": "coordinate"} for i in range(coordinate)]
    return items


def _observation(axis: str, stated: bool = True, value=1, **extra) -> dict:
    entry = {
        "axis": axis,
        "stated": stated,
        "value": value,
        "value_text": None,
        "quote": "掲載ページからの引用" if stated else None,
    }
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
        _observation(
            "experience_distance",
            value=None,
            value_text="必須要件の引用文",
            required_experience=["AWS を用いたインフラ構築の実務経験3年以上"],
            job_family="インフラエンジニア",
        ),
        _observation("salary_condition", value=6500000),
    ]


def _judgement(axis: str, level: str = "want", verdict: str = "meets") -> dict:
    return {
        "axis": axis,
        "level": level,
        "judgement": verdict,
        "threshold_ref": None if level == "none" else f"ref-{axis}",
        "rationale": "観測値としきい値を対比した根拠",
    }


def _judgements(**overrides) -> list[dict]:
    levels = {"remote_certainty": "must", "overtime_hours": "must"}
    entries = []
    for axis in vj.SCREENING_AXES:
        level = levels.get(axis, "want")
        verdict = "meets"
        if axis == "experience_distance":
            level, verdict = "none", "unknown"
        if axis in overrides:
            level, verdict = overrides[axis]
        entries.append(_judgement(axis, level, verdict))
    return entries


def _result_item(classification: str = "apply_candidate", **overrides) -> dict:
    duty_items = _duty_items()
    item = {
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
    return item


def _screening(items: list[dict], recommendation: str = "応募推奨あり") -> dict:
    counts = {name: 0 for name in vj.CLASSIFICATIONS}
    for item in items:
        counts[item["classification"]] += 1
    counts["total"] = len(items)

    summary = []
    for axis in vj.SCREENING_AXES:
        not_meets = unknown = 0
        for item in items:
            for judgement in item["axis_judgements"]:
                if judgement["axis"] != axis:
                    continue
                if judgement["judgement"] == "not_meets":
                    not_meets += 1
                elif judgement["judgement"] == "unknown":
                    unknown += 1
        summary.append({"axis": axis, "not_meets": not_meets, "unknown": unknown})

    return {
        "screened_at": "2026-07-25",
        "profile_schema_version": "2.0",
        "axes_source": "job_change_axis.conditions",
        "counts": counts,
        "recommendation": recommendation,
        "rationale": "必須条件を満たす求人がある",
        "unmet_axis_summary": summary,
        "current_employer_exclusion": {
            "performed": True,
            "excluded_count": 0,
            "method": "career_history の在職中エントリと company_name を照合した",
        },
    }


def _valid_v2(items: list[dict] | None = None, recommendation: str = "応募推奨あり") -> dict:
    items = [_result_item()] if items is None else items
    document = _valid_fuzzy()
    document["schema_version"] = "2.0"
    document["results"] = items
    document["screening"] = _screening(items, recommendation)
    return document


class V2BaselineTest(unittest.TestCase):
    def test_valid_v2_passes_without_warnings(self):
        result = vj.validate(_valid_v2(), pii_terms=[])
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_v1_document_is_not_checked_against_v2_rules(self):
        document = _valid_fuzzy()
        document["results"][0].pop("axis_observations", None)
        result = vj.validate(document, pii_terms=[])
        self.assertTrue(result.ok)

    def test_v2_without_screening_is_an_error(self):
        document = _valid_v2()
        del document["screening"]
        result = vj.validate(document, pii_terms=[])
        self.assertFalse(result.ok)
        self.assertTrue(any("screening" in e for e in result.errors))


class V2ObservationTest(unittest.TestCase):
    def _validate(self, mutate) -> vj.ValidationResult:
        document = _valid_v2()
        mutate(document["results"][0])
        return vj.validate(document, pii_terms=[])

    def test_missing_axis_is_an_error(self):
        result = self._validate(lambda item: item["axis_observations"].pop())
        self.assertFalse(result.ok)
        self.assertTrue(any("欠落" in e for e in result.errors))

    def test_duplicated_axis_is_an_error(self):
        def mutate(item):
            item["axis_observations"][1]["axis"] = item["axis_observations"][0]["axis"]

        self.assertFalse(self._validate(mutate).ok)

    def test_stated_without_quote_is_an_error(self):
        result = self._validate(lambda item: item["axis_observations"][0].__setitem__("quote", ""))
        self.assertFalse(result.ok)
        self.assertTrue(any("掲載ページからの引用" in e for e in result.errors))

    def test_stated_with_null_value_needs_value_text(self):
        def mutate(item):
            item["axis_observations"][1]["value"] = None
            item["axis_observations"][1]["value_text"] = None

        result = self._validate(mutate)
        self.assertFalse(result.ok)
        self.assertTrue(any("value_text" in e for e in result.errors))

    def test_duty_item_needs_quote_and_category(self):
        result = self._validate(lambda item: item["duty_items"].append({"quote": "", "category": "nope"}))
        self.assertFalse(result.ok)

    def test_ratio_with_too_few_duty_items_is_an_error(self):
        def mutate(item):
            item["duty_items"] = [{"quote": "構築", "category": "build"}]

        result = self._validate(mutate)
        self.assertFalse(result.ok)
        self.assertTrue(any("件未満" in e for e in result.errors))

    def test_ratio_mismatch_with_duty_items_is_an_error(self):
        def mutate(item):
            for observation in item["axis_observations"]:
                if observation["axis"] == "hands_on_ratio":
                    observation["value"] = 0.1

        result = self._validate(mutate)
        self.assertFalse(result.ok)
        self.assertTrue(any("再計算" in e for e in result.errors))


class V2ObservationValueTest(unittest.TestCase):
    """軸ごとの観測値の型と値域の検査。"""

    def _validate(self, axis: str, **changes) -> vj.ValidationResult:
        document = _valid_v2()
        for observation in document["results"][0]["axis_observations"]:
            if observation["axis"] == axis:
                observation.update(changes)
        return vj.validate(document, pii_terms=[])

    def test_enum_axes_accept_every_defined_value(self):
        for axis, values in vj.AXIS_ENUM_VALUES.items():
            for value in values:
                with self.subTest(axis=axis, value=value):
                    self.assertEqual(self._validate(axis, value=value).errors, [])

    def test_remote_certainty_unknown_value_is_an_error(self):
        result = self._validate("remote_certainty", value="banana")
        self.assertFalse(result.ok)
        self.assertTrue(any("guaranteed" in e for e in result.errors))

    def test_oncall_load_number_is_an_error(self):
        result = self._validate("oncall_load", value=42)
        self.assertFalse(result.ok)
        self.assertTrue(any("none_stated/exists" in e for e in result.errors))

    def test_unstated_axis_with_a_bogus_value_is_an_error(self):
        result = self._validate("oncall_load", stated=False, value="banana", quote=None)
        self.assertFalse(result.ok)
        self.assertTrue(any("none_stated/exists" in e for e in result.errors))

    def test_overtime_hours_string_is_an_error(self):
        result = self._validate("overtime_hours", value="少なめ")
        self.assertFalse(result.ok)
        self.assertTrue(any("数値でなければならない" in e for e in result.errors))

    def test_overtime_hours_negative_is_an_error(self):
        result = self._validate("overtime_hours", value=-5)
        self.assertFalse(result.ok)
        self.assertTrue(any("範囲" in e for e in result.errors))

    def test_annual_holidays_negative_is_an_error(self):
        result = self._validate("annual_holidays", value=-1)
        self.assertFalse(result.ok)
        self.assertTrue(any("範囲" in e for e in result.errors))

    def test_annual_holidays_boolean_is_an_error(self):
        result = self._validate("annual_holidays", value=True)
        self.assertFalse(result.ok)
        self.assertTrue(any("数値でなければならない" in e for e in result.errors))

    def test_ratio_above_one_is_an_error(self):
        result = self._validate("hands_on_ratio", value=1.5)
        self.assertFalse(result.ok)
        self.assertTrue(any("範囲" in e for e in result.errors))

    def test_ratio_below_zero_is_an_error(self):
        result = self._validate("coordination_ratio", value=-0.2)
        self.assertFalse(result.ok)
        self.assertTrue(any("範囲" in e for e in result.errors))

    def test_salary_condition_negative_is_an_error(self):
        result = self._validate("salary_condition", value=-6500000)
        self.assertFalse(result.ok)
        self.assertTrue(any("範囲" in e for e in result.errors))

    def test_salary_condition_in_man_yen_warns_but_passes(self):
        result = self._validate("salary_condition", value=650)
        self.assertTrue(result.ok)
        self.assertTrue(any("万円単位" in w for w in result.warnings))

    def test_experience_distance_with_a_value_is_an_error(self):
        result = self._validate("experience_distance", value="near")
        self.assertFalse(result.ok)
        self.assertTrue(any("null 固定" in e for e in result.errors))

    def test_experience_distance_without_required_experience_is_an_error(self):
        document = _valid_v2()
        for observation in document["results"][0]["axis_observations"]:
            if observation["axis"] == "experience_distance":
                del observation["required_experience"]
        result = vj.validate(document, pii_terms=[])
        self.assertFalse(result.ok)
        self.assertTrue(any("required_experience" in e for e in result.errors))

    def test_experience_distance_required_experience_must_hold_strings(self):
        result = self._validate("experience_distance", required_experience=["", 3])
        self.assertFalse(result.ok)
        self.assertTrue(any("required_experience" in e for e in result.errors))

    def test_experience_distance_without_job_family_is_an_error(self):
        result = self._validate("experience_distance", job_family="")
        self.assertFalse(result.ok)
        self.assertTrue(any("job_family" in e for e in result.errors))


class V2JudgementTest(unittest.TestCase):
    def _validate(self, mutate) -> vj.ValidationResult:
        document = _valid_v2()
        mutate(document["results"][0])
        return vj.validate(document, pii_terms=[])

    def test_unstated_axis_cannot_be_decided(self):
        def mutate(item):
            for observation in item["axis_observations"]:
                if observation["axis"] == "annual_holidays":
                    observation["stated"] = False
                    observation["value"] = None
                    observation["quote"] = None

        result = self._validate(mutate)
        self.assertFalse(result.ok)
        self.assertTrue(any("記載が無い軸" in e for e in result.errors))

    def test_null_value_cannot_be_decided(self):
        def mutate(item):
            for observation in item["axis_observations"]:
                if observation["axis"] == "annual_holidays":
                    observation["value"] = None
                    observation["value_text"] = "年間休日は多め"

        result = self._validate(mutate)
        self.assertFalse(result.ok)
        self.assertTrue(any("観測値が null" in e for e in result.errors))

    def test_must_level_without_threshold_ref_is_an_error(self):
        def mutate(item):
            item["axis_judgements"][0]["threshold_ref"] = None

        result = self._validate(mutate)
        self.assertFalse(result.ok)
        self.assertTrue(any("threshold_ref" in e for e in result.errors))

    def test_missing_rationale_is_an_error(self):
        result = self._validate(lambda item: item["axis_judgements"][0].__setitem__("rationale", " "))
        self.assertFalse(result.ok)

    def test_unknown_judgement_value_is_an_error(self):
        result = self._validate(lambda item: item["axis_judgements"][0].__setitem__("judgement", "maybe"))
        self.assertFalse(result.ok)


class V2ClassificationTest(unittest.TestCase):
    def test_must_not_meets_derives_excluded(self):
        item = _result_item("excluded", remote_certainty=("must", "not_meets"))
        result = vj.validate(_valid_v2([item], "応募推奨なし"), pii_terms=[])
        self.assertEqual(result.errors, [])

    def test_must_not_meets_classified_as_apply_is_an_error(self):
        item = _result_item("apply_candidate", remote_certainty=("must", "not_meets"))
        result = vj.validate(_valid_v2([item]), pii_terms=[])
        self.assertFalse(result.ok)
        self.assertTrue(any("classification" in e for e in result.errors))

    def test_must_unknown_derives_needs_more_research(self):
        item = _result_item("needs_more_research", overtime_hours=("must", "unknown"))
        result = vj.validate(_valid_v2([item], "応募推奨なし"), pii_terms=[])
        self.assertEqual(result.errors, [])

    def test_four_unknowns_derive_needs_more_research(self):
        item = _result_item(
            "needs_more_research",
            annual_holidays=("want", "unknown"),
            oncall_load=("want", "unknown"),
            hands_on_ratio=("want", "unknown"),
        )
        result = vj.validate(_valid_v2([item], "応募推奨なし"), pii_terms=[])
        self.assertEqual(result.errors, [])

    def test_override_towards_stricter_is_allowed(self):
        item = _result_item("needs_more_research")
        item["classification_override"] = {
            "from": "apply_candidate",
            "to": "needs_more_research",
            "reason": "掲載が古く条件が変わっている可能性がある",
        }
        result = vj.validate(_valid_v2([item], "応募推奨なし"), pii_terms=[])
        self.assertEqual(result.errors, [])

    def test_override_towards_looser_is_an_error(self):
        item = _result_item("apply_candidate", remote_certainty=("must", "not_meets"))
        item["classification_override"] = {
            "from": "excluded",
            "to": "apply_candidate",
            "reason": "交渉できるはず",
        }
        result = vj.validate(_valid_v2([item]), pii_terms=[])
        self.assertFalse(result.ok)
        self.assertTrue(any("厳しくする方向" in e for e in result.errors))

    def test_empty_classification_reasons_is_an_error(self):
        item = _result_item()
        item["classification_reasons"] = []
        result = vj.validate(_valid_v2([item]), pii_terms=[])
        self.assertFalse(result.ok)


class V2ScreeningTest(unittest.TestCase):
    def test_count_mismatch_is_an_error(self):
        document = _valid_v2()
        document["screening"]["counts"]["apply_candidate"] = 5
        result = vj.validate(document, pii_terms=[])
        self.assertFalse(result.ok)

    def test_zero_apply_candidates_must_say_no_recommendation(self):
        item = _result_item("excluded", remote_certainty=("must", "not_meets"))
        document = _valid_v2([item], "応募推奨あり")
        result = vj.validate(document, pii_terms=[])
        self.assertFalse(result.ok)
        self.assertTrue(any("応募推奨なし" in e for e in result.errors))

    def test_apply_candidates_cannot_say_no_recommendation(self):
        document = _valid_v2(recommendation="応募推奨なし")
        result = vj.validate(document, pii_terms=[])
        self.assertFalse(result.ok)

    def test_degraded_source_must_be_undecidable(self):
        document = _valid_v2()
        document["screening"]["axes_source"] = "degraded"
        result = vj.validate(document, pii_terms=[])
        self.assertFalse(result.ok)
        self.assertTrue(any("判定不能" in e for e in result.errors))

    def test_all_excluded_warns(self):
        item = _result_item("excluded", remote_certainty=("must", "not_meets"))
        document = _valid_v2([item], "応募推奨なし")
        result = vj.validate(document, pii_terms=[])
        self.assertTrue(result.ok)
        self.assertTrue(any("全件が除外候補" in w for w in result.warnings))

    def test_unperformed_exclusion_cannot_claim_a_count(self):
        document = _valid_v2()
        document["screening"]["current_employer_exclusion"]["performed"] = False
        result = vj.validate(document, pii_terms=[])
        self.assertFalse(result.ok)
        self.assertTrue(any("件数を主張してはならない" in e for e in result.errors))

    def test_unperformed_exclusion_with_null_count_passes(self):
        document = _valid_v2()
        document["screening"]["current_employer_exclusion"]["performed"] = False
        document["screening"]["current_employer_exclusion"]["excluded_count"] = None
        result = vj.validate(document, pii_terms=[])
        self.assertTrue(result.ok)

    def test_performed_exclusion_needs_an_integer_count(self):
        document = _valid_v2()
        document["screening"]["current_employer_exclusion"]["excluded_count"] = None
        result = vj.validate(document, pii_terms=[])
        self.assertFalse(result.ok)

    def test_unmet_axis_summary_mismatch_is_an_error(self):
        document = _valid_v2()
        document["screening"]["unmet_axis_summary"][0]["not_meets"] = 3
        result = vj.validate(document, pii_terms=[])
        self.assertFalse(result.ok)


class V2ThresholdRefTest(unittest.TestCase):
    def _profile(self) -> dict:
        return {
            "job_change_axis": {
                "conditions": [
                    {"id": "ref-remote_certainty", "level": "must"},
                    {"id": "ref-overtime_hours", "level": "must"},
                    {"id": "ref-annual_holidays", "level": "want"},
                    {"id": "ref-oncall_load", "level": "want"},
                    {"id": "ref-hands_on_ratio", "level": "want"},
                    {"id": "ref-coordination_ratio", "level": "want"},
                    {"id": "ref-salary_condition", "level": "want"},
                ],
                "work_character_preferences": [],
            }
        }

    def test_existing_refs_pass(self):
        result = vj.validate(_valid_v2(), pii_terms=[], profile=self._profile())
        self.assertEqual(result.errors, [])

    def test_unknown_ref_is_an_error(self):
        document = _valid_v2()
        document["results"][0]["axis_judgements"][0]["threshold_ref"] = "ref-does-not-exist"
        result = vj.validate(document, pii_terms=[], profile=self._profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("存在しない条件" in e for e in result.errors))

    def test_level_mismatch_is_an_error(self):
        profile = self._profile()
        profile["job_change_axis"]["conditions"][0]["level"] = "want"
        result = vj.validate(_valid_v2(), pii_terms=[], profile=profile)
        self.assertFalse(result.ok)
        self.assertTrue(any("必須度" in e for e in result.errors))


class ExampleAssetTest(unittest.TestCase):
    def test_bundled_example_passes(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        document = vj.load_json(os.path.join(base, "assets", "job_search_results_example.json"))
        profile_path = os.path.join(
            os.path.dirname(base), "job-change-support", "assets", "profile_example.json"
        )
        profile = vj.load_json(profile_path)
        result = vj.validate(document, pii_terms=vj.collect_pii_terms(profile), profile=profile)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


if __name__ == "__main__":
    unittest.main()
