"""validate_company_research.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_company_research
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_company_research as vcr  # noqa: E402


def _claim(cid: str, topic: str, grade: str = "A", confidence: str = "medium") -> dict:
    """指定トピック・グレードの最小 claim を1件返す。"""
    return {
        "id": cid,
        "topic": topic,
        "statement": f"{topic} に関する反証可能な命題。",
        "evidence": [
            {
                "source_url": "https://example.co.jp/source",
                "source_name": "出典名",
                "grade": grade,
                "quote": "根拠となる引用。",
                "accessed": "2026-07-12",
            }
        ],
        "confidence": confidence,
    }


def _valid_research() -> dict:
    """ERROR 0件・WARN 0件になる完全な company_research.json を返す。

    必須7トピック＋selection_process を網羅し、各トピックに A または B の裏付けを持たせて
    「トピックが全てC・D」WARN を避ける。
    """
    return {
        "company": {
            "name": "架空クラウドワークス株式会社",
            "securities_code": "9999",
            "edinet_code": "E99999",
        },
        "research_date": "2026-07-12",
        "claims": [
            _claim("C001", "philosophy", "A"),
            _claim("C002", "business", "A"),
            _claim("C003", "financials", "A", "high"),
            _claim("C004", "compensation", "A"),
            _claim("C005", "benefits", "A"),
            _claim("C006", "workstyle", "B"),
            _claim("C007", "reputation", "B"),
            _claim("C008", "selection_process", "B"),
        ],
        "workstyle_metrics": _full_workstyle_metrics(),
        "tier": _valid_tier(),
        "open_questions": ["職種別の給与内訳は有報からは判別できない。"],
    }


def _valid_tier() -> dict:
    """ERROR 0件・WARN 0件になる完全な tier オブジェクトを返す。

    claim_ids は _valid_research() の claims（C001〜C008）に実在する id を指す。
    """
    return {
        "rubric_version": 2,
        "assessed_date": "2026-07-12",
        "axes": {
            "compensation_level": {
                "rating": "high",
                "basis": "平均年間給与が業界上位。",
                "claim_ids": ["C004"],
            },
            "financial_soundness": {
                "rating": "high",
                "basis": "増収増益で利益率も高水準。",
                "claim_ids": ["C003"],
            },
            "retention": {
                "rating": "medium",
                "basis": "平均勤続年数は同業と同水準。",
                "claim_ids": ["C007"],
            },
        },
    }


def _metric(value: float, grade: str = "A") -> dict:
    """workstyle_metrics の1メトリック（{value, source_url, grade}）を返す。"""
    return {
        "value": value,
        "source_url": "https://disclosure2.edinet-fsa.example.go.jp/S9999",
        "grade": grade,
    }


def _full_workstyle_metrics() -> dict:
    """5メトリックすべてを値付きで持つ workstyle_metrics を返す（WARN ゼロ）。"""
    return {
        "annual_holidays": _metric(125),
        "monthly_overtime_h": _metric(14.2),
        "paid_leave_rate": _metric(71.0),
        "avg_paid_leave_days_taken": _metric(12.5),
        "avg_annual_salary": _metric(6120000),
    }


class ValidatePassTest(unittest.TestCase):
    def test_full_research_passes_without_warnings(self):
        result = vcr.validate(_valid_research())
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_low_grade_claim_with_non_high_confidence_passes(self):
        r = _valid_research()
        # reputation を C グレード・confidence=medium にする。ERROR にはならない。
        r["claims"][6] = _claim("C007", "reputation", "C", "medium")
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        # トピック reputation が全て C になるため WARN は出る。
        self.assertTrue(any("reputation" in w for w in result.warnings))


class RootAndCompanyErrorTest(unittest.TestCase):
    def test_root_not_object(self):
        result = vcr.validate(["not", "an", "object"])
        self.assertFalse(result.ok)

    def test_company_not_object(self):
        r = _valid_research()
        r["company"] = "文字列"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("company" in e for e in result.errors))

    def test_company_name_missing(self):
        r = _valid_research()
        del r["company"]["name"]
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("company.name" in e for e in result.errors))


class ClaimsErrorTest(unittest.TestCase):
    def test_claims_empty(self):
        r = _valid_research()
        r["claims"] = []
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("claims" in e for e in result.errors))

    def test_claims_missing(self):
        r = _valid_research()
        del r["claims"]
        result = vcr.validate(r)
        self.assertFalse(result.ok)

    def test_claim_missing_id(self):
        r = _valid_research()
        del r["claims"][0]["id"]
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("id" in e for e in result.errors))

    def test_claim_missing_statement(self):
        r = _valid_research()
        r["claims"][0]["statement"] = "  "
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("statement" in e for e in result.errors))

    def test_claim_missing_topic(self):
        r = _valid_research()
        del r["claims"][0]["topic"]
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("topic" in e for e in result.errors))

    def test_claim_invalid_topic(self):
        r = _valid_research()
        r["claims"][0]["topic"] = "culture"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        # philosophy が欠けるため必須トピック欠落 ERROR も併発する。
        self.assertTrue(any("topic" in e for e in result.errors))

    def test_claim_missing_confidence(self):
        r = _valid_research()
        del r["claims"][0]["confidence"]
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("confidence" in e for e in result.errors))

    def test_claim_invalid_confidence(self):
        r = _valid_research()
        r["claims"][0]["confidence"] = "確定"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("confidence" in e for e in result.errors))


class EvidenceErrorTest(unittest.TestCase):
    def test_evidence_empty(self):
        r = _valid_research()
        r["claims"][0]["evidence"] = []
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("evidence" in e for e in result.errors))

    def test_evidence_missing(self):
        r = _valid_research()
        del r["claims"][0]["evidence"]
        result = vcr.validate(r)
        self.assertFalse(result.ok)

    def test_source_url_not_http(self):
        r = _valid_research()
        r["claims"][0]["evidence"][0]["source_url"] = "www.example.com"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("source_url" in e for e in result.errors))

    def test_grade_out_of_range(self):
        r = _valid_research()
        r["claims"][0]["evidence"][0]["grade"] = "E"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("grade" in e for e in result.errors))

    def test_quote_empty(self):
        r = _valid_research()
        r["claims"][0]["evidence"][0]["quote"] = ""
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("quote" in e for e in result.errors))


class RequiredTopicErrorTest(unittest.TestCase):
    def test_missing_required_topic_errors(self):
        r = _valid_research()
        # financials の claim を除去する。
        r["claims"] = [c for c in r["claims"] if c["topic"] != "financials"]
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("financials" in e for e in result.errors))

    def test_selection_process_not_required_error(self):
        r = _valid_research()
        # selection_process を除いても ERROR にはならず WARN になる。
        r["claims"] = [c for c in r["claims"] if c["topic"] != "selection_process"]
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertTrue(any("selection_process" in w for w in result.warnings))


class LowGradeConfidenceErrorTest(unittest.TestCase):
    def test_cd_only_with_high_confidence_errors(self):
        r = _valid_research()
        r["claims"][6] = _claim("C007", "reputation", "C", "high")
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("C007" in e for e in result.errors))

    def test_mixed_grade_with_high_confidence_passes(self):
        r = _valid_research()
        # C と A を併記した claim は low_only ではないため confidence=high でも ERROR にならない。
        claim = _claim("C007", "reputation", "A", "high")
        claim["evidence"].append(
            {
                "source_url": "https://openwork.example/reviews",
                "source_name": "口コミ集計サイト",
                "grade": "C",
                "quote": "口コミの引用。",
                "accessed": "2026-07-12",
            }
        )
        r["claims"][6] = claim
        result = vcr.validate(r)
        self.assertTrue(result.ok)


class WarnTest(unittest.TestCase):
    def test_all_cd_topic_warns(self):
        r = _valid_research()
        r["claims"][6] = _claim("C007", "reputation", "C", "medium")
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertTrue(any("reputation" in w for w in result.warnings))

    def test_missing_research_date_warns(self):
        r = _valid_research()
        del r["research_date"]
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertTrue(any("research_date" in w for w in result.warnings))


class CliTest(unittest.TestCase):
    def _write_tmp(self, obj) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def test_main_returns_0_on_valid(self):
        path = self._write_tmp(_valid_research())
        self.assertEqual(vcr.main([path]), 0)

    def test_main_returns_1_on_invalid(self):
        r = _valid_research()
        del r["company"]["name"]
        path = self._write_tmp(r)
        self.assertEqual(vcr.main([path]), 1)

    def test_main_returns_1_on_broken_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{ not valid json ")
        self.addCleanup(os.remove, path)
        self.assertEqual(vcr.main([path]), 1)

    def test_main_json_flag_valid(self):
        path = self._write_tmp(_valid_research())
        self.assertEqual(vcr.main([path, "--json"]), 0)

    def test_main_returns_0_on_valid_with_bom(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8-sig") as f:
            json.dump(_valid_research(), f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        self.assertEqual(vcr.main([path]), 0)


class WorkstyleMetricsTest(unittest.TestCase):
    def test_full_metrics_no_warning(self):
        result = vcr.validate(_valid_research())
        self.assertTrue(result.ok)
        self.assertFalse(any("workstyle_metrics" in w for w in result.warnings))

    def test_absent_metrics_warns_but_passes(self):
        r = _valid_research()
        del r["workstyle_metrics"]
        result = vcr.validate(r)
        self.assertTrue(result.ok)  # 後方互換。欠落は WARN で PASS を維持する
        self.assertTrue(any("workstyle_metrics" in w for w in result.warnings))

    def test_individual_null_warns_but_passes(self):
        r = _valid_research()
        r["workstyle_metrics"]["avg_annual_salary"] = None
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertTrue(any("avg_annual_salary" in w for w in result.warnings))

    def test_metrics_not_object_errors(self):
        r = _valid_research()
        r["workstyle_metrics"] = "年間休日125日"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("workstyle_metrics" in e for e in result.errors))

    def test_metric_value_not_number_errors(self):
        r = _valid_research()
        r["workstyle_metrics"]["annual_holidays"]["value"] = "125"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("workstyle_metrics.annual_holidays.value" in e for e in result.errors)
        )

    def test_metric_value_bool_errors(self):
        r = _valid_research()
        r["workstyle_metrics"]["monthly_overtime_h"]["value"] = True
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("workstyle_metrics.monthly_overtime_h.value" in e for e in result.errors)
        )

    def test_metric_source_url_not_http_errors(self):
        r = _valid_research()
        r["workstyle_metrics"]["paid_leave_rate"]["source_url"] = "edinet.example"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("workstyle_metrics.paid_leave_rate.source_url" in e for e in result.errors)
        )

    def test_metric_invalid_grade_errors(self):
        r = _valid_research()
        r["workstyle_metrics"]["annual_holidays"]["grade"] = "E"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("workstyle_metrics.annual_holidays.grade" in e for e in result.errors)
        )

    def test_metric_scalar_instead_of_object_errors(self):
        r = _valid_research()
        r["workstyle_metrics"]["annual_holidays"] = 125
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("workstyle_metrics.annual_holidays" in e for e in result.errors)
        )


class TierTest(unittest.TestCase):
    def test_full_tier_no_warning(self):
        result = vcr.validate(_valid_research())
        self.assertTrue(result.ok)
        self.assertFalse(any("tier" in w for w in result.warnings))

    def test_tier_missing_errors(self):
        r = _valid_research()
        del r["tier"]
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("tier" in e for e in result.errors))

    def test_tier_not_object_errors(self):
        r = _valid_research()
        r["tier"] = "A"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("tier" in e for e in result.errors))

    def test_level_present_warns(self):
        r = _valid_research()
        r["tier"]["level"] = "A"
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertTrue(any("tier.level" in w for w in result.warnings))

    def test_axes_missing_errors(self):
        r = _valid_research()
        del r["tier"]["axes"]
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("tier.axes" in e for e in result.errors))

    def test_axes_empty_errors(self):
        r = _valid_research()
        r["tier"]["axes"] = {}
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("tier.axes" in e for e in result.errors))

    def test_single_axis_passes(self):
        r = _valid_research()
        r["tier"]["axes"] = {
            "compensation_level": {
                "rating": "high",
                "basis": "平均年間給与が業界上位。",
                "claim_ids": ["C004"],
            }
        }
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertFalse(any("tier" in w for w in result.warnings))

    def test_unknown_axis_key_errors(self):
        r = _valid_research()
        r["tier"]["axes"]["brand_power"] = {
            "rating": "high",
            "basis": "知名度が高い。",
            "claim_ids": ["C002"],
        }
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("tier.axes.brand_power" in e for e in result.errors))

    def test_axis_rating_invalid_errors(self):
        r = _valid_research()
        r["tier"]["axes"]["retention"]["rating"] = "強い"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("tier.axes.retention.rating" in e for e in result.errors))

    def test_axis_basis_empty_errors(self):
        r = _valid_research()
        r["tier"]["axes"]["financial_soundness"]["basis"] = ""
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("tier.axes.financial_soundness.basis" in e for e in result.errors))

    def test_claim_ids_not_list_errors(self):
        r = _valid_research()
        r["tier"]["axes"]["retention"]["claim_ids"] = "C007"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("tier.axes.retention.claim_ids" in e for e in result.errors))

    def test_claim_ids_dangling_reference_errors(self):
        r = _valid_research()
        r["tier"]["axes"]["retention"]["claim_ids"] = ["C999"]
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("tier.axes.retention.claim_ids" in e for e in result.errors))

    def test_unknown_rating_with_empty_claim_ids_passes(self):
        r = _valid_research()
        r["tier"]["axes"]["retention"] = {
            "rating": "unknown",
            "basis": "定着を判定できる一次・二次情報が得られなかった。",
            "claim_ids": [],
        }
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertFalse(any("retention.claim_ids" in w for w in result.warnings))

    def test_rated_axis_with_empty_claim_ids_warns(self):
        r = _valid_research()
        r["tier"]["axes"]["retention"]["claim_ids"] = []
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertTrue(any("tier.axes.retention.claim_ids" in w for w in result.warnings))

    def test_rubric_version_missing_warns(self):
        r = _valid_research()
        del r["tier"]["rubric_version"]
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertTrue(any("tier.rubric_version" in w for w in result.warnings))


class ResultShapeTest(unittest.TestCase):
    def test_to_dict_shape(self):
        result = vcr.validate(_valid_research())
        d = result.to_dict()
        self.assertEqual(d["status"], "PASS")
        self.assertEqual(d["error_count"], 0)
        self.assertIn("warnings", d)

    def test_immutability_of_input(self):
        r = _valid_research()
        snapshot = copy.deepcopy(r)
        vcr.validate(r)
        self.assertEqual(r, snapshot)


if __name__ == "__main__":
    unittest.main()
