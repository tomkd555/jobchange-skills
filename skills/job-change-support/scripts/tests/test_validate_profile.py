"""validate_profile.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_profile
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_profile as vp  # noqa: E402


def _valid_profile() -> dict:
    """schema_version 1.0 の、移行推奨の WARN 以外が出ない完全なプロファイルを返す。"""
    return {
        "schema_version": "1.0",
        "updated_at": "2026-07-12",
        "basic": {
            "current_role": "バックエンドエンジニア",
            "years_of_experience": 6,
            "location": "東京都",
            "education": ["○○大学 情報工学科"],
        },
        "career_history": [
            {
                "company": "架空システム株式会社",
                "period": "2020-04〜2026-06",
                "role": "バックエンドエンジニア",
                "responsibilities": ["API 設計", "チームリード"],
                "achievements": [
                    {"description": "処理時間短縮", "metric": "応答時間を40%削減"}
                ],
            }
        ],
        "skills": {
            "technical": ["Python", "AWS"],
            "business": ["要件定義"],
            "languages": [{"language": "英語", "level": "TOEIC 800"}],
            "certifications": ["応用情報技術者"],
        },
        "strengths": ["設計力"],
        "job_change_axis": {
            "reasons": ["裁量の拡大"],
            "must_conditions": ["リモート可"],
            "want_conditions": ["年収600万以上"],
        },
        "targets": {
            "industries": ["SaaS"],
            "roles": ["テックリード"],
            "companies": ["架空クラウド社"],
        },
        "salary": {"current": 5500000, "desired": 7000000},
        "notes": "",
    }


def _work_character_preferences(**desires: str) -> list[dict]:
    """8特性すべてを持つ work_character_preferences を返す。既定は neutral。"""
    preferences = []
    for trait in vp._WORK_CHARACTER_TRAITS:
        desire = desires.get(trait, "neutral")
        entry = {"trait": trait, "desire": desire}
        if desire == "must":
            entry["statement"] = f"{trait} を満たすこと"
        preferences.append(entry)
    return preferences


def _valid_v2_profile() -> dict:
    """ERROR 0件・WARN 0件になる schema_version 2.0 のプロファイルを返す。"""
    profile = _valid_profile()
    profile["schema_version"] = "2.0"
    profile["job_change_axis"] = {
        "reasons": ["裁量の拡大"],
        "conditions": [
            {
                "id": "cond-remote",
                "level": "must",
                "statement": "フルリモートが制度として保証されていること",
                "axis": "remote_certainty",
                "operator": "==",
                "value": "guaranteed",
                "unit": "none",
                "verification": "posting",
                "priority": 1,
            },
            {
                "id": "cond-salary",
                "level": "want",
                "statement": "年収600万円以上",
                "axis": "salary_condition",
                "operator": ">=",
                "value": 6000000,
                "unit": "yen",
                "verification": "posting",
            },
        ],
        "work_character_preferences": _work_character_preferences(hands_on="important"),
    }
    return profile


class ValidatePassTest(unittest.TestCase):
    def test_full_v1_profile_has_only_the_migration_warning(self):
        result = vp.validate(_valid_profile())
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("2.0 への移行", result.warnings[0])

    def test_full_v2_profile_passes_without_warnings(self):
        result = vp.validate(_valid_v2_profile())
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


class ErrorCaseTest(unittest.TestCase):
    def test_root_not_object(self):
        result = vp.validate(["not", "an", "object"])
        self.assertFalse(result.ok)

    def test_missing_schema_version(self):
        p = _valid_profile()
        del p["schema_version"]
        result = vp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("schema_version" in e for e in result.errors))

    def test_empty_schema_version(self):
        p = _valid_profile()
        p["schema_version"] = "  "
        result = vp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("schema_version" in e for e in result.errors))

    def test_missing_current_role(self):
        p = _valid_profile()
        del p["basic"]["current_role"]
        result = vp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("current_role" in e for e in result.errors))

    def test_basic_not_object(self):
        p = _valid_profile()
        p["basic"] = "文字列"
        result = vp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("basic" in e for e in result.errors))

    def test_empty_career_history(self):
        p = _valid_profile()
        p["career_history"] = []
        result = vp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("career_history" in e for e in result.errors))

    def test_career_history_missing_company(self):
        p = _valid_profile()
        del p["career_history"][0]["company"]
        result = vp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("company" in e for e in result.errors))

    def test_career_history_missing_period(self):
        p = _valid_profile()
        p["career_history"][0]["period"] = ""
        result = vp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("period" in e for e in result.errors))

    def test_career_history_missing_role(self):
        p = _valid_profile()
        del p["career_history"][0]["role"]
        result = vp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("role" in e for e in result.errors))

    def test_empty_job_change_axis_reasons(self):
        p = _valid_profile()
        p["job_change_axis"]["reasons"] = []
        result = vp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("reasons" in e for e in result.errors))

    def test_job_change_axis_reasons_all_blank(self):
        p = _valid_profile()
        p["job_change_axis"]["reasons"] = ["", "   "]
        result = vp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("reasons" in e for e in result.errors))


class WarnCaseTest(unittest.TestCase):
    def test_no_metric_warns_but_passes(self):
        p = _valid_profile()
        p["career_history"][0]["achievements"] = [
            {"description": "改善に貢献", "metric": None}
        ]
        result = vp.validate(p)
        self.assertTrue(result.ok)  # WARN のみは PASS
        self.assertTrue(any("metric" in w for w in result.warnings))

    def test_no_achievements_warns(self):
        p = _valid_profile()
        p["career_history"][0]["achievements"] = []
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("achievements" in w for w in result.warnings))

    def test_all_skills_empty_warns(self):
        p = _valid_profile()
        p["skills"] = {
            "technical": [],
            "business": [],
            "languages": [],
            "certifications": [],
        }
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("skills" in w for w in result.warnings))

    def test_all_targets_empty_warns(self):
        p = _valid_profile()
        p["targets"] = {"industries": [], "roles": [], "companies": []}
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("targets" in w for w in result.warnings))

    def test_missing_updated_at_warns(self):
        p = _valid_profile()
        del p["updated_at"]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("updated_at" in w for w in result.warnings))


class CliTest(unittest.TestCase):
    def _write_tmp(self, obj) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def test_main_returns_0_on_valid(self):
        path = self._write_tmp(_valid_profile())
        self.assertEqual(vp.main([path]), 0)

    def test_main_returns_1_on_invalid(self):
        p = _valid_profile()
        del p["schema_version"]
        path = self._write_tmp(p)
        self.assertEqual(vp.main([path]), 1)

    def test_main_returns_1_on_broken_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{ not valid json ")
        self.addCleanup(os.remove, path)
        self.assertEqual(vp.main([path]), 1)

    def test_main_json_flag_valid(self):
        path = self._write_tmp(_valid_profile())
        self.assertEqual(vp.main([path, "--json"]), 0)

    def test_main_returns_0_on_valid_with_bom(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8-sig") as f:
            json.dump(_valid_profile(), f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        self.assertEqual(vp.main([path]), 0)


def _minimal_v1_0_profile() -> dict:
    """v1.0 の必須項目のみを持つ最小プロファイル（後方互換確認用）。"""
    return {
        "schema_version": "1.0",
        "basic": {"current_role": "エンジニア"},
        "career_history": [
            {"company": "架空株式会社", "period": "2022-04〜現在", "role": "エンジニア"}
        ],
        "job_change_axis": {"reasons": ["裁量の拡大"]},
    }


class BackwardCompatTest(unittest.TestCase):
    def test_minimal_v1_0_profile_still_passes(self):
        result = vp.validate(_minimal_v1_0_profile())
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])


class W1SchemaVersionTest(unittest.TestCase):
    def test_unknown_schema_version_warns(self):
        p = _valid_profile()
        p["schema_version"] = "9.9"
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("既知のバージョン" in w for w in result.warnings))

    def test_schema_version_1_1_is_known(self):
        p = _valid_profile()
        p["schema_version"] = "1.1"
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertFalse(any("既知のバージョン" in w for w in result.warnings))

    def test_schema_version_2_0_is_known(self):
        result = vp.validate(_valid_v2_profile())
        self.assertFalse(any("既知のバージョン" in w for w in result.warnings))

    def test_v1_gets_migration_warning(self):
        for version in ("1.0", "1.1"):
            with self.subTest(version=version):
                p = _valid_profile()
                p["schema_version"] = version
                result = vp.validate(p)
                self.assertTrue(any("2.0 への移行" in w for w in result.warnings))

    def test_v2_does_not_get_migration_warning(self):
        result = vp.validate(_valid_v2_profile())
        self.assertFalse(any("2.0 への移行" in w for w in result.warnings))


class W2PeriodFormatTest(unittest.TestCase):
    def test_malformed_period_warns(self):
        p = _valid_profile()
        p["career_history"][0]["period"] = "2020/04-2026/06"
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(
            any("period" in w and "career_history" in w for w in result.warnings)
        )

    def test_ongoing_period_does_not_warn(self):
        p = _valid_profile()
        p["career_history"][0]["period"] = "2020-04〜現在"
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertFalse(
            any("career_history[0].period" in w for w in result.warnings)
        )


class W3CareerGapTest(unittest.TestCase):
    def test_uncovered_gap_warns(self):
        p = _valid_profile()
        p["career_history"] = [
            {
                "company": "旧職",
                "period": "2018-04〜2019-03",
                "role": "エンジニア",
                "achievements": [{"description": "実績", "metric": "10%改善"}],
            },
            {
                "company": "現職",
                "period": "2020-01〜現在",
                "role": "エンジニア",
                "achievements": [{"description": "実績", "metric": "10%改善"}],
            },
        ]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("career_gaps" in w for w in result.warnings))

    def test_gap_covered_by_career_gaps_does_not_warn(self):
        p = _valid_profile()
        p["career_history"] = [
            {
                "company": "旧職",
                "period": "2018-04〜2019-03",
                "role": "エンジニア",
                "achievements": [{"description": "実績", "metric": "10%改善"}],
            },
            {
                "company": "現職",
                "period": "2020-01〜現在",
                "role": "エンジニア",
                "achievements": [{"description": "実績", "metric": "10%改善"}],
            },
        ]
        p["career_gaps"] = [
            {
                "period": "2019-04〜2019-12",
                "explanation": "資格取得のための学習期間",
            }
        ]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertFalse(any("career_gaps" in w for w in result.warnings))

    def test_short_gap_does_not_warn(self):
        p = _valid_profile()
        p["career_history"] = [
            {
                "company": "旧職",
                "period": "2018-04〜2019-03",
                "role": "エンジニア",
                "achievements": [{"description": "実績", "metric": "10%改善"}],
            },
            {
                "company": "現職",
                "period": "2019-06〜現在",
                "role": "エンジニア",
                "achievements": [{"description": "実績", "metric": "10%改善"}],
            },
        ]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertFalse(any("career_gaps" in w for w in result.warnings))

    def test_unparseable_period_skips_gap_detection(self):
        p = _valid_profile()
        p["career_history"] = [
            {
                "company": "旧職",
                "period": "不明",
                "role": "エンジニア",
                "achievements": [{"description": "実績", "metric": "10%改善"}],
            },
            {
                "company": "現職",
                "period": "2020-01〜現在",
                "role": "エンジニア",
                "achievements": [{"description": "実績", "metric": "10%改善"}],
            },
        ]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertFalse(any("career_gaps" in w for w in result.warnings))


class W4LanguagesShapeTest(unittest.TestCase):
    def test_language_missing_level_warns(self):
        p = _valid_profile()
        p["skills"]["languages"] = [{"language": "英語"}]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("skills.languages" in w for w in result.warnings))

    def test_valid_language_shape_does_not_warn(self):
        p = _valid_profile()
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertFalse(any("skills.languages[" in w for w in result.warnings))


class W5SalaryTypeTest(unittest.TestCase):
    def test_non_numeric_salary_warns(self):
        p = _valid_profile()
        p["salary"]["current"] = "五百万円"
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("salary.current" in w for w in result.warnings))

    def test_null_salary_does_not_warn(self):
        p = _valid_profile()
        p["salary"]["current"] = None
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertFalse(any("salary." in w for w in result.warnings))


class W6MustConditionsCountTest(unittest.TestCase):
    def test_four_or_more_must_conditions_warns(self):
        p = _valid_profile()
        p["job_change_axis"]["must_conditions"] = ["A", "B", "C", "D"]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("must_conditions" in w for w in result.warnings))

    def test_three_must_conditions_does_not_warn(self):
        p = _valid_profile()
        p["job_change_axis"]["must_conditions"] = ["A", "B", "C"]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertFalse(any("must_conditions" in w for w in result.warnings))


class W7CareerGapsShapeTest(unittest.TestCase):
    def test_malformed_gap_period_warns(self):
        p = _valid_profile()
        p["career_gaps"] = [{"period": "2019年4月", "explanation": "休養"}]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("career_gaps[0].period" in w for w in result.warnings))

    def test_missing_explanation_warns(self):
        p = _valid_profile()
        p["career_gaps"] = [{"period": "2019-04〜2019-09", "explanation": ""}]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(
            any("career_gaps[0].explanation" in w for w in result.warnings)
        )

    def test_valid_career_gap_does_not_warn(self):
        p = _valid_profile()
        p["career_gaps"] = [
            {"period": "2019-04〜2019-09", "explanation": "資格取得のための学習期間"}
        ]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertFalse(
            any(
                w.startswith("[WARN] career_gaps[0]")
                for w in result.warnings
            )
        )


class W8SkillsPortableCategoryTest(unittest.TestCase):
    def test_invalid_category_warns(self):
        p = _valid_profile()
        p["skills"]["portable"] = [{"skill": "傾聴力", "category": "その他"}]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(
            any("skills.portable[0].category" in w for w in result.warnings)
        )

    def test_valid_categories_do_not_warn(self):
        p = _valid_profile()
        p["skills"]["portable"] = [
            {"skill": "課題解決力", "category": "対課題"},
            {"skill": "傾聴力", "category": "対人"},
        ]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertFalse(
            any("skills.portable" in w for w in result.warnings)
        )


class ResultShapeTest(unittest.TestCase):
    def test_to_dict_shape(self):
        result = vp.validate(_valid_profile())
        d = result.to_dict()
        self.assertEqual(d["status"], "PASS")
        self.assertEqual(d["error_count"], 0)
        self.assertIn("warnings", d)

    def test_immutability_of_input(self):
        p = _valid_profile()
        snapshot = copy.deepcopy(p)
        vp.validate(p)
        self.assertEqual(p, snapshot)


class V2ConditionsTest(unittest.TestCase):
    def _validate(self, mutate) -> vp.ValidationResult:
        p = _valid_v2_profile()
        mutate(p["job_change_axis"])
        return vp.validate(p)

    def test_conditions_must_be_a_list(self):
        result = self._validate(lambda axis: axis.__setitem__("conditions", {}))
        self.assertFalse(result.ok)
        self.assertTrue(any("conditions" in e for e in result.errors))

    def test_missing_conditions_is_an_error(self):
        result = self._validate(lambda axis: axis.pop("conditions"))
        self.assertFalse(result.ok)

    def test_duplicate_id_is_an_error(self):
        result = self._validate(
            lambda axis: axis["conditions"][1].__setitem__("id", axis["conditions"][0]["id"])
        )
        self.assertFalse(result.ok)
        self.assertTrue(any("重複" in e for e in result.errors))

    def test_malformed_id_is_an_error(self):
        result = self._validate(lambda axis: axis["conditions"][0].__setitem__("id", "Cond Remote"))
        self.assertFalse(result.ok)

    def test_unknown_level_is_an_error(self):
        result = self._validate(lambda axis: axis["conditions"][0].__setitem__("level", "nice"))
        self.assertFalse(result.ok)

    def test_empty_statement_is_an_error(self):
        result = self._validate(lambda axis: axis["conditions"][0].__setitem__("statement", " "))
        self.assertFalse(result.ok)

    def test_unknown_axis_is_an_error(self):
        result = self._validate(lambda axis: axis["conditions"][0].__setitem__("axis", "vibes"))
        self.assertFalse(result.ok)

    def test_null_axis_is_allowed(self):
        def mutate(axis):
            axis["conditions"][0]["axis"] = None
            axis["conditions"][0]["operator"] = "qualitative"
            axis["conditions"][0]["value"] = None
            axis["conditions"][0]["verification"] = "interview"

        self.assertTrue(self._validate(mutate).ok)

    def test_unknown_operator_is_an_error(self):
        result = self._validate(lambda axis: axis["conditions"][0].__setitem__("operator", "~="))
        self.assertFalse(result.ok)

    def test_comparative_operator_without_value_is_an_error(self):
        result = self._validate(lambda axis: axis["conditions"][0].__setitem__("value", None))
        self.assertFalse(result.ok)
        self.assertTrue(any("value" in e for e in result.errors))

    def test_qualitative_operator_allows_null_value(self):
        def mutate(axis):
            axis["conditions"][0]["operator"] = "qualitative"
            axis["conditions"][0]["value"] = None

        self.assertTrue(self._validate(mutate).ok)

    def test_unknown_verification_is_an_error(self):
        result = self._validate(lambda axis: axis["conditions"][0].__setitem__("verification", "guess"))
        self.assertFalse(result.ok)

    def test_no_must_condition_warns(self):
        result = self._validate(lambda axis: axis["conditions"][0].__setitem__("level", "want"))
        self.assertTrue(result.ok)
        self.assertTrue(any("must の条件が1件も無い" in w for w in result.warnings))

    def test_duplicate_must_axis_warns(self):
        def mutate(axis):
            extra = dict(axis["conditions"][0])
            extra["id"] = "cond-remote-2"
            axis["conditions"].append(extra)

        result = self._validate(mutate)
        self.assertTrue(result.ok)
        self.assertTrue(any("同じ軸に必須条件" in w for w in result.warnings))

    def test_missing_priority_on_must_warns(self):
        result = self._validate(lambda axis: axis["conditions"][0].pop("priority"))
        self.assertTrue(result.ok)
        self.assertTrue(any("priority" in w for w in result.warnings))


class V2WorkCharacterTest(unittest.TestCase):
    def _validate(self, mutate) -> vp.ValidationResult:
        p = _valid_v2_profile()
        mutate(p["job_change_axis"])
        return vp.validate(p)

    def test_missing_preferences_is_an_error(self):
        result = self._validate(lambda axis: axis.pop("work_character_preferences"))
        self.assertFalse(result.ok)

    def test_seven_traits_is_an_error(self):
        result = self._validate(lambda axis: axis["work_character_preferences"].pop())
        self.assertFalse(result.ok)
        self.assertTrue(any("欠落" in e for e in result.errors))

    def test_duplicated_trait_is_an_error(self):
        def mutate(axis):
            axis["work_character_preferences"][1]["trait"] = axis["work_character_preferences"][0]["trait"]

        result = self._validate(mutate)
        self.assertFalse(result.ok)
        self.assertTrue(any("重複" in e for e in result.errors))

    def test_unknown_trait_is_an_error(self):
        result = self._validate(
            lambda axis: axis["work_character_preferences"][0].__setitem__("trait", "fun")
        )
        self.assertFalse(result.ok)

    def test_unknown_desire_is_an_error(self):
        result = self._validate(
            lambda axis: axis["work_character_preferences"][0].__setitem__("desire", "maybe")
        )
        self.assertFalse(result.ok)

    def test_must_desire_requires_statement(self):
        def mutate(axis):
            axis["work_character_preferences"][0]["desire"] = "must"
            axis["work_character_preferences"][0].pop("statement", None)

        result = self._validate(mutate)
        self.assertFalse(result.ok)
        self.assertTrue(any("statement" in e for e in result.errors))

    def test_must_desire_with_statement_passes(self):
        def mutate(axis):
            axis["work_character_preferences"][0]["desire"] = "must"
            axis["work_character_preferences"][0]["statement"] = "自分で手を動かせること"

        self.assertTrue(self._validate(mutate).ok)


class V2MustCountTest(unittest.TestCase):
    def test_total_must_count_of_four_warns(self):
        p = _valid_v2_profile()
        axis = p["job_change_axis"]
        axis["conditions"][1]["level"] = "must"
        axis["conditions"][1]["priority"] = 2
        for preference in axis["work_character_preferences"][:2]:
            preference["desire"] = "must"
            preference["statement"] = "満たすこと"
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("合計が4件" in w for w in result.warnings))

    def test_legacy_arrays_left_in_v2_warn(self):
        p = _valid_v2_profile()
        p["job_change_axis"]["must_conditions"] = ["リモート可"]
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("must_conditions" in w for w in result.warnings))

    def test_salary_floor_above_desired_warns(self):
        p = _valid_v2_profile()
        p["job_change_axis"]["conditions"][1]["level"] = "must"
        p["job_change_axis"]["conditions"][1]["priority"] = 2
        p["job_change_axis"]["conditions"][1]["value"] = 9000000
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("希望年収" in w for w in result.warnings))

    def test_v1_profile_is_not_checked_against_v2_rules(self):
        p = _valid_profile()
        p["job_change_axis"]["conditions"] = "これは v1 なので検査されない"
        result = vp.validate(p)
        self.assertTrue(result.ok)


def _company_score_axes() -> list[dict]:
    """ERROR 0件・WARN 0件になる company_score_axes を返す。"""
    return [
        {
            "axis": "compensation_level",
            "kind": "quantitative",
            "weight": 40,
            "thresholds": {"zero": 4500000, "full": 7000000},
        },
        {"axis": "annual_holidays", "kind": "quantitative", "weight": 25},
        {
            "axis": "discretion",
            "kind": "qualitative",
            "weight": 35,
            "label": "裁量の大きさ",
            "definition": "設計方針を自分で決められること",
            "judgment": [
                {"score": 100, "condition": "求人票に設計裁量の記載があり、面接でも確認できた"},
                {"score": 50, "condition": "求人票に記載があるが未確認"},
                {"score": 0, "condition": "上位者の承認が必要と明記されている"},
            ],
        },
    ]


class V2CompanyScoreAxesTest(unittest.TestCase):
    def _validate(self, axes) -> vp.ValidationResult:
        p = _valid_v2_profile()
        p["company_score_axes"] = axes
        return vp.validate(p)

    def test_absent_field_passes_without_warnings(self):
        result = vp.validate(_valid_v2_profile())
        self.assertTrue(result.ok)
        self.assertFalse(any("company_score_axes" in w for w in result.warnings))

    def test_valid_axes_pass_without_warnings(self):
        result = self._validate(_company_score_axes())
        self.assertTrue(result.ok)
        self.assertEqual(result.warnings, [])

    def test_non_list_is_an_error(self):
        result = self._validate({"axis": "compensation_level"})
        self.assertFalse(result.ok)
        self.assertTrue(any("company_score_axes" in e for e in result.errors))

    def test_non_object_element_is_an_error(self):
        result = self._validate(["compensation_level"])
        self.assertFalse(result.ok)
        self.assertTrue(any("company_score_axes[0]" in e for e in result.errors))

    def test_missing_axis_is_an_error(self):
        axes = _company_score_axes()
        del axes[1]["axis"]
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("axis" in e for e in result.errors))

    def test_duplicate_axis_is_an_error(self):
        axes = _company_score_axes()
        axes[1]["axis"] = axes[0]["axis"]
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("重複" in e for e in result.errors))

    def test_unknown_kind_is_an_error(self):
        axes = _company_score_axes()
        axes[0]["kind"] = "mixed"
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("kind" in e for e in result.errors))

    def test_missing_kind_is_an_error(self):
        axes = _company_score_axes()
        del axes[1]["kind"]
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("kind" in e for e in result.errors))

    def test_quantitative_axis_outside_the_candidates_is_an_error(self):
        axes = _company_score_axes()
        axes[1]["axis"] = "vibes"
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("定量候補軸" in e for e in result.errors))

    def test_qualitative_axis_key_is_free(self):
        axes = _company_score_axes()
        axes[2]["axis"] = "onboarding_support"
        result = self._validate(axes)
        self.assertTrue(result.ok)
        self.assertEqual(result.warnings, [])

    def test_non_integer_weight_is_an_error(self):
        axes = _company_score_axes()
        axes[0]["weight"] = 40.5
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("weight" in e for e in result.errors))

    def test_zero_weight_is_an_error(self):
        axes = _company_score_axes()
        axes[0]["weight"] = 0
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("weight" in e for e in result.errors))

    def test_weight_sum_other_than_100_is_an_error(self):
        axes = _company_score_axes()
        axes[1]["weight"] = 20
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("合計" in e for e in result.errors))

    def test_thresholds_on_a_qualitative_axis_is_an_error(self):
        axes = _company_score_axes()
        axes[2]["thresholds"] = {"zero": 0, "full": 100}
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("thresholds" in e for e in result.errors))

    def test_non_numeric_thresholds_is_an_error(self):
        axes = _company_score_axes()
        axes[0]["thresholds"] = {"zero": "450万円", "full": 7000000}
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("thresholds" in e for e in result.errors))

    def test_missing_threshold_key_is_an_error(self):
        axes = _company_score_axes()
        del axes[0]["thresholds"]["full"]
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("thresholds" in e for e in result.errors))

    def test_equal_thresholds_is_an_error(self):
        axes = _company_score_axes()
        axes[0]["thresholds"] = {"zero": 6000000, "full": 6000000}
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("thresholds" in e for e in result.errors))

    def test_qualitative_axis_without_label_is_an_error(self):
        axes = _company_score_axes()
        del axes[2]["label"]
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("label" in e for e in result.errors))

    def test_qualitative_axis_without_definition_is_an_error(self):
        axes = _company_score_axes()
        axes[2]["definition"] = "  "
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("definition" in e for e in result.errors))

    def test_empty_judgment_is_an_error(self):
        axes = _company_score_axes()
        axes[2]["judgment"] = []
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("judgment" in e for e in result.errors))

    def test_judgment_score_out_of_range_is_an_error(self):
        axes = _company_score_axes()
        axes[2]["judgment"][0]["score"] = 120
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("score" in e for e in result.errors))

    def test_judgment_without_condition_is_an_error(self):
        axes = _company_score_axes()
        del axes[2]["judgment"][1]["condition"]
        result = self._validate(axes)
        self.assertFalse(result.ok)
        self.assertTrue(any("condition" in e for e in result.errors))

    def test_judgment_not_in_descending_order_warns(self):
        axes = _company_score_axes()
        axes[2]["judgment"].reverse()
        result = self._validate(axes)
        self.assertTrue(result.ok)
        self.assertTrue(any("降順" in w for w in result.warnings))

    def test_empty_list_warns(self):
        result = self._validate([])
        self.assertTrue(result.ok)
        self.assertTrue(any("company_score_axes" in w for w in result.warnings))

    def test_missing_compensation_level_warns(self):
        axes = [
            {"axis": "annual_holidays", "kind": "quantitative", "weight": 60},
            {"axis": "monthly_overtime", "kind": "quantitative", "weight": 40},
        ]
        result = self._validate(axes)
        self.assertTrue(result.ok)
        self.assertTrue(any("compensation_level" in w for w in result.warnings))

    def test_v1_profile_is_not_checked_against_the_axes_rules(self):
        p = _valid_profile()
        p["company_score_axes"] = "これは v1 なので検査されない"
        result = vp.validate(p)
        self.assertTrue(result.ok)
        self.assertFalse(any("company_score_axes" in w for w in result.warnings))


class ExampleAssetTest(unittest.TestCase):
    def test_bundled_example_passes_without_warnings(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "assets",
            "profile_example.json",
        )
        result = vp.validate(vp.load_profile(path))
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


if __name__ == "__main__":
    unittest.main()
