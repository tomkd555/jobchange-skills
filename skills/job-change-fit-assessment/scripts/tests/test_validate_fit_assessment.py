"""validate_fit_assessment.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_fit_assessment
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_fit_assessment as vf  # noqa: E402


def _dimension(dim_id: str, score=3) -> dict:
    return {
        "id": dim_id,
        "score": score,
        "verdict": f"{dim_id} の判定根拠",
        "evidence": [
            {"source": "company_research", "ref": "C001", "note": "根拠"}
        ],
    }


def _valid_fit() -> dict:
    """ERROR 0件・WARN 0件になる完全な fit_assessment を返す。"""
    return {
        "schema_version": "1.0",
        "slug": "kakuu-cloudworks",
        "assessed_at": "2026-07-15",
        "inputs": {
            "job_posting": True,
            "company_research": True,
            "self_analysis": True,
            "time_analysis": True,
        },
        "dimensions": [
            _dimension("skill_fit", 4),
            _dimension("condition_fit", 4),
            _dimension("culture_fit", 3),
            _dimension("compensation_fit", 3),
            _dimension("time_fit", 4),
        ],
        "must_condition_results": [
            {
                "condition": "リモート勤務が可能であること",
                "met": "yes",
                "evidence": [
                    {"source": "job_posting", "ref": "location.remote_policy", "note": "可"}
                ],
            },
            {
                "condition": "副業が許可されていること",
                "met": "unknown",
                "evidence": [],
            },
        ],
        "overall": {
            "recommendation": "条件付き推奨",
            "rationale": "必須条件は概ね満たすが副業可否が未確認である。",
            "open_questions": ["副業許可の有無"],
        },
    }


class ValidatePassTest(unittest.TestCase):
    def test_full_fit_passes_without_warnings(self):
        result = vf.validate(_valid_fit())
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


class TopLevelErrorTest(unittest.TestCase):
    def test_root_not_object(self):
        result = vf.validate(["not", "an", "object"])
        self.assertFalse(result.ok)

    def test_missing_schema_version(self):
        d = _valid_fit()
        del d["schema_version"]
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("schema_version" in e for e in result.errors))

    def test_missing_slug(self):
        d = _valid_fit()
        del d["slug"]
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("slug" in e for e in result.errors))

    def test_invalid_slug_format(self):
        d = _valid_fit()
        d["slug"] = "Kakuu_CloudWorks"
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("slug" in e for e in result.errors))

    def test_missing_assessed_at(self):
        d = _valid_fit()
        d["assessed_at"] = ""
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("assessed_at" in e for e in result.errors))


class InputsErrorTest(unittest.TestCase):
    def test_inputs_not_object(self):
        d = _valid_fit()
        d["inputs"] = "文字列"
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("inputs" in e for e in result.errors))

    def test_inputs_missing_key(self):
        d = _valid_fit()
        del d["inputs"]["time_analysis"]
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("time_analysis" in e for e in result.errors))

    def test_inputs_non_bool_value(self):
        d = _valid_fit()
        d["inputs"]["job_posting"] = "yes"
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("job_posting" in e for e in result.errors))


class DimensionErrorTest(unittest.TestCase):
    def test_missing_dimension_id_errors(self):
        d = _valid_fit()
        d["dimensions"] = d["dimensions"][:4]  # time_fit を欠落
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("time_fit" in e for e in result.errors))

    def test_unknown_dimension_id_errors(self):
        d = _valid_fit()
        d["dimensions"][0]["id"] = "growth_fit"
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("dimensions" in e for e in result.errors))

    def test_duplicate_dimension_id_errors(self):
        d = _valid_fit()
        d["dimensions"].append(_dimension("skill_fit", 3))
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("重複" in e for e in result.errors))

    def test_score_out_of_range_errors(self):
        d = _valid_fit()
        d["dimensions"][0]["score"] = 6
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("score" in e for e in result.errors))

    def test_score_bool_errors(self):
        d = _valid_fit()
        d["dimensions"][0]["score"] = True
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("score" in e for e in result.errors))

    def test_empty_evidence_errors(self):
        d = _valid_fit()
        d["dimensions"][0]["evidence"] = []
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("evidence" in e for e in result.errors))

    def test_missing_verdict_errors(self):
        d = _valid_fit()
        d["dimensions"][0]["verdict"] = ""
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("verdict" in e for e in result.errors))

    def test_invalid_evidence_source_errors(self):
        d = _valid_fit()
        d["dimensions"][0]["evidence"][0]["source"] = "hearsay"
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("source" in e for e in result.errors))


class DimensionWarnTest(unittest.TestCase):
    def test_null_score_warns_but_passes(self):
        d = _valid_fit()
        d["dimensions"][2]["score"] = None
        result = vf.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("score" in w for w in result.warnings))

    def test_empty_ref_warns_but_passes(self):
        d = _valid_fit()
        d["dimensions"][0]["evidence"][0]["ref"] = ""
        result = vf.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("ref" in w for w in result.warnings))


class MustConditionTest(unittest.TestCase):
    def test_invalid_met_errors(self):
        d = _valid_fit()
        d["must_condition_results"][0]["met"] = "maybe"
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("met" in e for e in result.errors))

    def test_missing_condition_errors(self):
        d = _valid_fit()
        d["must_condition_results"][0]["condition"] = ""
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("condition" in e for e in result.errors))

    def test_yes_with_empty_evidence_errors(self):
        d = _valid_fit()
        d["must_condition_results"][0]["evidence"] = []
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("evidence" in e for e in result.errors))

    def test_unknown_with_empty_evidence_passes(self):
        d = _valid_fit()
        # 既定の unknown 条件は evidence 空。これは許容される
        result = vf.validate(d)
        self.assertTrue(result.ok)


class OverallTest(unittest.TestCase):
    def test_invalid_recommendation_errors(self):
        d = _valid_fit()
        d["overall"]["recommendation"] = "たぶん推奨"
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("recommendation" in e for e in result.errors))

    def test_missing_rationale_errors(self):
        d = _valid_fit()
        d["overall"]["rationale"] = ""
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("rationale" in e for e in result.errors))

    def test_open_questions_not_list_errors(self):
        d = _valid_fit()
        d["overall"]["open_questions"] = "なし"
        result = vf.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("open_questions" in e for e in result.errors))


class ConsistencyWarnTest(unittest.TestCase):
    def test_unmet_must_with_recommend_warns(self):
        d = _valid_fit()
        d["must_condition_results"][1]["met"] = "no"
        d["must_condition_results"][1]["evidence"] = [
            {"source": "job_posting", "ref": "benefits", "note": "副業禁止"}
        ]
        d["overall"]["recommendation"] = "推奨"
        result = vf.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("recommendation" in w for w in result.warnings))

    def test_all_inputs_false_warns(self):
        d = _valid_fit()
        for k in d["inputs"]:
            d["inputs"][k] = False
        result = vf.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("inputs" in w for w in result.warnings))

    def test_unknown_schema_version_warns(self):
        d = _valid_fit()
        d["schema_version"] = "9.9"
        result = vf.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("schema_version" in w for w in result.warnings))

    def test_malformed_assessed_at_warns(self):
        d = _valid_fit()
        d["assessed_at"] = "2026/07/15"
        result = vf.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("assessed_at" in w for w in result.warnings))


class ExampleAssetTest(unittest.TestCase):
    def test_bundled_example_passes(self):
        example_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "assets",
            "fit_assessment_example.json",
        )
        with open(example_path, "r", encoding="utf-8-sig") as f:
            example = json.load(f)
        result = vf.validate(example)
        self.assertTrue(result.ok, msg=f"記入例が PASS しない: {result.errors}")


class CliTest(unittest.TestCase):
    def _write_tmp(self, obj, encoding="utf-8") -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding=encoding) as f:
            json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def test_main_returns_0_on_valid(self):
        path = self._write_tmp(_valid_fit())
        self.assertEqual(vf.main([path]), 0)

    def test_main_returns_1_on_invalid(self):
        d = _valid_fit()
        del d["schema_version"]
        path = self._write_tmp(d)
        self.assertEqual(vf.main([path]), 1)

    def test_main_returns_1_on_broken_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{ not valid json ")
        self.addCleanup(os.remove, path)
        self.assertEqual(vf.main([path]), 1)

    def test_main_json_flag_valid(self):
        path = self._write_tmp(_valid_fit())
        self.assertEqual(vf.main([path, "--json"]), 0)

    def test_main_returns_0_on_valid_with_bom(self):
        path = self._write_tmp(_valid_fit(), encoding="utf-8-sig")
        self.assertEqual(vf.main([path]), 0)


class ResultShapeTest(unittest.TestCase):
    def test_to_dict_shape(self):
        result = vf.validate(_valid_fit())
        d = result.to_dict()
        self.assertEqual(d["status"], "PASS")
        self.assertEqual(d["error_count"], 0)
        self.assertIn("warnings", d)

    def test_immutability_of_input(self):
        d = _valid_fit()
        snapshot = copy.deepcopy(d)
        vf.validate(d)
        self.assertEqual(d, snapshot)


# --- schema_version 2.0（7次元）の検査 ----------------------------------------


def _v2_dimension(dim_id: str, score=3) -> dict:
    dimension = {
        "id": dim_id,
        "score": score,
        "verdict": f"{dim_id} の判定根拠",
        "evidence": [{"source": "company_research", "ref": "C001", "note": "根拠"}],
    }
    if dim_id == "experience_proximity":
        dimension["skill_gap"] = "none"
        dimension["skill_gap_items"] = []
    if dim_id == "aspiration_alignment":
        dimension["evidence"] = [
            {"source": "self_analysis", "ref": "career_narrative.future_direction", "note": "根拠"}
        ]
    return dimension


def _must_result(ref: str, met: str = "yes", **extra) -> dict:
    entry = {
        "ref": ref,
        "condition": f"{ref} の条件文",
        "met": met,
        "evidence": [{"source": "job_posting", "ref": "location.remote_policy", "note": "根拠"}],
    }
    if met == "unknown":
        entry["evidence"] = []
    entry.update(extra)
    return entry


def _valid_v2_fit(**overrides) -> dict:
    document = {
        "schema_version": "2.0",
        "slug": "kakuu-cloudworks",
        "assessed_at": "2026-07-25",
        "inputs": {
            "job_posting": True,
            "company_research": True,
            "self_analysis": True,
            "time_analysis": True,
            "job_search_screening": False,
        },
        "dimensions": [_v2_dimension(d) for d in vf._V2_DIMENSION_IDS],
        "must_condition_results": [_must_result("cond-remote"), _must_result("no_oncall")],
        "overall": {
            "recommendation": "推奨",
            "rationale": "必須条件を満たす",
            "open_questions": [],
        },
    }
    document.update(overrides)
    return document


def _v2_profile() -> dict:
    return {
        "schema_version": "2.0",
        "job_change_axis": {
            "conditions": [
                {"id": "cond-remote", "level": "must"},
                {"id": "cond-salary", "level": "want"},
            ],
            "work_character_preferences": [
                {"trait": "no_oncall", "desire": "must"},
                {"trait": "hands_on", "desire": "important"},
            ],
        },
    }


class V2BaselineTest(unittest.TestCase):
    def test_valid_v2_passes_with_profile(self):
        result = vf.validate(_valid_v2_fit(), profile=_v2_profile())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_v1_dimension_ids_in_v2_are_an_error(self):
        document = _valid_v2_fit()
        document["dimensions"][0]["id"] = "skill_fit"
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)

    def test_v2_dimension_ids_in_v1_are_an_error(self):
        d = _valid_fit()
        d["dimensions"][0]["id"] = "experience_proximity"
        result = vf.validate(d)
        self.assertFalse(result.ok)

    def test_job_search_screening_input_key_is_required_in_v2(self):
        document = _valid_v2_fit()
        del document["inputs"]["job_search_screening"]
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)

    def test_screening_evidence_source_is_allowed_in_v2(self):
        document = _valid_v2_fit()
        document["dimensions"][2]["evidence"] = [
            {"source": "job_search_screening", "ref": "results[0]", "note": "根拠"}
        ]
        result = vf.validate(document, profile=_v2_profile())
        self.assertEqual(result.errors, [])

    def test_screening_evidence_source_is_rejected_in_v1(self):
        d = _valid_fit()
        d["dimensions"][0]["evidence"] = [
            {"source": "job_search_screening", "ref": "results[0]", "note": "根拠"}
        ]
        result = vf.validate(d)
        self.assertFalse(result.ok)


class V2SkillGapTest(unittest.TestCase):
    def _experience(self, document: dict) -> dict:
        return next(d for d in document["dimensions"] if d["id"] == "experience_proximity")

    def test_unknown_gap_value_is_an_error(self):
        document = _valid_v2_fit()
        self._experience(document)["skill_gap"] = "soon"
        self.assertFalse(vf.validate(document, profile=_v2_profile()).ok)

    def test_missing_gap_items_is_an_error(self):
        document = _valid_v2_fit()
        del self._experience(document)["skill_gap_items"]
        self.assertFalse(vf.validate(document, profile=_v2_profile()).ok)

    def test_gap_must_match_the_heaviest_item(self):
        document = _valid_v2_fit()
        experience = self._experience(document)
        experience["skill_gap"] = "complementable_within_3m"
        experience["skill_gap_items"] = [
            {
                "requirement": "Kubernetes 運用",
                "gap_level": "needs_6_12m_study",
                "basis": "隣接経験が無い",
                "evidence": [{"source": "job_posting", "ref": "requirements.must[1]", "note": "根拠"}],
            }
        ]
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("最も重い段階" in e for e in result.errors))

    def test_gap_item_needs_basis_and_evidence(self):
        document = _valid_v2_fit()
        experience = self._experience(document)
        experience["skill_gap"] = "needs_6_12m_study"
        experience["skill_gap_items"] = [
            {"requirement": "Kubernetes 運用", "gap_level": "needs_6_12m_study", "basis": "", "evidence": []}
        ]
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("basis" in e for e in result.errors))

    def test_not_applicable_now_cannot_be_recommended(self):
        document = _valid_v2_fit()
        experience = self._experience(document)
        experience["skill_gap"] = "not_applicable_now"
        experience["skill_gap_items"] = [
            {
                "requirement": "10年以上のマネジメント経験",
                "gap_level": "not_applicable_now",
                "basis": "経験年数が届かない",
                "evidence": [{"source": "job_posting", "ref": "requirements.must[0]", "note": "根拠"}],
            }
        ]
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("応募困難" in e for e in result.errors))


class V2MustConditionTest(unittest.TestCase):
    def test_missing_ref_is_an_error(self):
        document = _valid_v2_fit()
        del document["must_condition_results"][0]["ref"]
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)

    def test_refs_must_match_profile_one_to_one(self):
        document = _valid_v2_fit()
        document["must_condition_results"] = [_must_result("cond-remote")]
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("対応する判定が無い" in e for e in result.errors))

    def test_extra_ref_not_in_profile_is_an_error(self):
        document = _valid_v2_fit()
        document["must_condition_results"].append(_must_result("cond-salary"))
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("存在しない必須条件" in e for e in result.errors))

    def test_duplicate_ref_is_an_error(self):
        document = _valid_v2_fit()
        document["must_condition_results"].append(_must_result("cond-remote"))
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)

    def test_missing_profile_warns_about_unverified_mapping(self):
        result = vf.validate(_valid_v2_fit())
        self.assertTrue(any("未検証" in w for w in result.warnings))

    def test_negotiable_without_evidence_is_an_error(self):
        document = _valid_v2_fit()
        document["must_condition_results"][0] = _must_result("cond-remote", "no", negotiable=True)
        document["must_condition_results"][0]["evidence"] = []
        document["overall"]["recommendation"] = "条件付き推奨"
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("negotiable" in e for e in result.errors))


class V2RecommendationTest(unittest.TestCase):
    def test_unmet_must_with_recommend_is_an_error(self):
        document = _valid_v2_fit()
        document["must_condition_results"][0] = _must_result("cond-remote", "no")
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("「推奨」" in e for e in result.errors))

    def test_negotiable_unmet_allows_conditional_recommendation(self):
        document = _valid_v2_fit()
        document["must_condition_results"][0] = _must_result("cond-remote", "no", negotiable=True)
        document["overall"]["recommendation"] = "条件付き推奨"
        result = vf.validate(document, profile=_v2_profile())
        self.assertEqual(result.errors, [])

    def test_non_negotiable_unmet_forbids_conditional_recommendation(self):
        document = _valid_v2_fit()
        document["must_condition_results"][0] = _must_result("cond-remote", "no")
        document["overall"]["recommendation"] = "条件付き推奨"
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("交渉で解消できない" in e for e in result.errors))

    def test_non_negotiable_unmet_allows_rejection(self):
        document = _valid_v2_fit()
        document["must_condition_results"][0] = _must_result("cond-remote", "no")
        document["overall"]["recommendation"] = "非推奨"
        result = vf.validate(document, profile=_v2_profile())
        self.assertEqual(result.errors, [])


class V2AspirationTest(unittest.TestCase):
    def _aspiration(self, document: dict) -> dict:
        return next(d for d in document["dimensions"] if d["id"] == "aspiration_alignment")

    def test_high_score_without_self_analysis_is_an_error(self):
        document = _valid_v2_fit()
        document["inputs"]["self_analysis"] = False
        self._aspiration(document)["score"] = 4
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("志向の一致を高く評価" in e for e in result.errors))

    def test_evidence_without_self_analysis_or_profile_is_an_error(self):
        document = _valid_v2_fit()
        self._aspiration(document)["evidence"] = [
            {"source": "job_posting", "ref": "responsibilities[0]", "note": "根拠"}
        ]
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("志向を断定しない" in e for e in result.errors))

    def test_null_score_skips_the_checks(self):
        document = _valid_v2_fit()
        aspiration = self._aspiration(document)
        aspiration["score"] = None
        aspiration["evidence"] = [{"source": "job_posting", "ref": "responsibilities[0]", "note": "根拠"}]
        result = vf.validate(document, profile=_v2_profile())
        self.assertEqual(result.errors, [])


def _company_score(**overrides) -> dict:
    score = {
        "total": 72,
        "coverage": 85,
        "provisional": False,
        "axes": [
            {
                "axis": "compensation_level",
                "kind": "quantitative",
                "weight": 50,
                "value": 6480000,
                "unit": "円",
                "score": 65,
                "threshold_source": "user",
                "thresholds": {"zero": 4500000, "full": 7000000},
                "grade": "A",
                "source_url": "https://example.go.jp/ir",
            },
            {
                "axis": "tech_discretion",
                "kind": "qualitative",
                "weight": 35,
                "value": None,
                "unit": None,
                "score": 82,
                "threshold_source": None,
                "thresholds": None,
                "grade": None,
                "source_url": None,
                "evidence": "求人票の記載に合致した",
            },
            {
                "axis": "annual_holidays",
                "kind": "quantitative",
                "weight": 15,
                "value": None,
                "unit": "日",
                "score": None,
                "threshold_source": None,
                "thresholds": None,
                "grade": None,
                "source_url": None,
                "reason": "企業研究に実測値が無い",
            },
        ],
        "rationale": "総合点 72 点は、判定できた2軸の加重平均である。",
    }
    score.update(overrides)
    return score


class CompanyScoreTest(unittest.TestCase):
    """任意フィールド company_score（企業スコアの総合点と内訳）の検査。"""

    def test_absent_company_score_passes(self):
        result = vf.validate(_valid_v2_fit(), profile=_v2_profile())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_valid_company_score_passes(self):
        document = _valid_v2_fit(company_score=_company_score())
        result = vf.validate(document, profile=_v2_profile())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_non_object_company_score_is_an_error(self):
        document = _valid_v2_fit(company_score=72)
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("company_score" in e for e in result.errors))

    def test_total_out_of_range_is_an_error(self):
        document = _valid_v2_fit(company_score=_company_score(total=120))
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("company_score.total" in e for e in result.errors))

    def test_non_integer_total_is_an_error(self):
        document = _valid_v2_fit(company_score=_company_score(total=72.4))
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("company_score.total" in e for e in result.errors))

    def test_null_total_warns_but_passes(self):
        document = _valid_v2_fit(
            company_score=_company_score(
                total=None, coverage=0, provisional=True, axes=[],
                rationale="判定できた軸が1つも無いため、総合点は算出しない。",
            )
        )
        result = vf.validate(document, profile=_v2_profile())
        self.assertTrue(result.ok)
        self.assertTrue(any("company_score.total" in w for w in result.warnings))

    def test_coverage_out_of_range_is_an_error(self):
        document = _valid_v2_fit(company_score=_company_score(coverage=150))
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("company_score.coverage" in e for e in result.errors))

    def test_null_coverage_is_an_error(self):
        document = _valid_v2_fit(company_score=_company_score(coverage=None))
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("company_score.coverage" in e for e in result.errors))

    def test_non_boolean_provisional_is_an_error(self):
        document = _valid_v2_fit(company_score=_company_score(provisional="false"))
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("company_score.provisional" in e for e in result.errors))

    def test_provisional_warns_but_passes(self):
        document = _valid_v2_fit(company_score=_company_score(provisional=True, coverage=50))
        result = vf.validate(document, profile=_v2_profile())
        self.assertTrue(result.ok)
        self.assertTrue(any("company_score.provisional" in w for w in result.warnings))

    def test_axes_not_list_is_an_error(self):
        document = _valid_v2_fit(company_score=_company_score(axes={}))
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("company_score.axes" in e for e in result.errors))

    def test_empty_axis_key_is_an_error(self):
        score = _company_score()
        score["axes"][0]["axis"] = ""
        document = _valid_v2_fit(company_score=score)
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("axes[0].axis" in e for e in result.errors))

    def test_unknown_kind_is_an_error(self):
        score = _company_score()
        score["axes"][1]["kind"] = "numeric"
        document = _valid_v2_fit(company_score=score)
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("axes[1].kind" in e for e in result.errors))

    def test_weight_out_of_range_is_an_error(self):
        score = _company_score()
        score["axes"][2]["weight"] = 0
        document = _valid_v2_fit(company_score=score)
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("axes[2].weight" in e for e in result.errors))

    def test_axis_score_out_of_range_is_an_error(self):
        score = _company_score()
        score["axes"][0]["score"] = 101
        document = _valid_v2_fit(company_score=score)
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("axes[0].score" in e for e in result.errors))

    def test_null_axis_score_passes(self):
        result = vf.validate(_valid_v2_fit(company_score=_company_score()), profile=_v2_profile())
        self.assertEqual(result.errors, [])

    def test_axis_entry_not_object_is_an_error(self):
        document = _valid_v2_fit(company_score=_company_score(axes=["compensation_level"]))
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)

    def test_empty_rationale_is_an_error(self):
        document = _valid_v2_fit(company_score=_company_score(rationale=""))
        result = vf.validate(document, profile=_v2_profile())
        self.assertFalse(result.ok)
        self.assertTrue(any("company_score.rationale" in e for e in result.errors))


class ExampleAssetTest(unittest.TestCase):
    def test_bundled_example_passes(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        document = vf.load_fit_assessment(os.path.join(base, "assets", "fit_assessment_example.json"))
        profile = vf.load_fit_assessment(
            os.path.join(os.path.dirname(base), "job-change-support", "assets", "profile_example.json")
        )
        result = vf.validate(document, profile=profile)
        self.assertEqual(result.errors, [])
        # 記入例の企業スコアは判定できない軸を含むため、暫定であることの WARN だけが出る。
        self.assertTrue(all("company_score.provisional" in w for w in result.warnings))


if __name__ == "__main__":
    unittest.main()
