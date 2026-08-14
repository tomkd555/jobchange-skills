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
    """指定トピック・レベルの最小 claim を1件返す。"""
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
        "company_metrics": _full_company_metrics(),
        "open_questions": ["職種別の給与内訳は有報からは判別できない。"],
    }


def _metric(value: float, unit: str, grade: str = "A") -> dict:
    """company_metrics の1項目（{value, unit, source_url, grade, as_of}）を返す。"""
    return {
        "value": value,
        "unit": unit,
        "source_url": "https://disclosure2.edinet-fsa.example.go.jp/S9999",
        "grade": grade,
        "as_of": "2026-03",
    }


def _null_metric(unit: str) -> dict:
    """実測値を確認できなかった項目（value が null）を返す。"""
    return {"value": None, "unit": unit, "source_url": None, "grade": None, "as_of": None}


def _full_company_metrics() -> dict:
    """定量候補軸9個と補助指標を値付きで持つ company_metrics を返す（WARN ゼロ）。"""
    return {
        "compensation_level": _metric(6120000, "円"),
        "annual_holidays": _metric(125, "日"),
        "monthly_overtime": _metric(14.2, "時間"),
        "paid_leave_rate": _metric(71.0, "%"),
        "turnover_rate": _metric(8.4, "%"),
        "male_childcare_leave_rate": _metric(62.5, "%"),
        "revenue_growth": _metric(18.0, "%"),
        "operating_margin": _metric(12.5, "%"),
        "equity_ratio": _metric(64.0, "%"),
        "avg_paid_leave_days_taken": _metric(12.5, "日"),
    }


def _all_null_company_metrics() -> dict:
    """全項目の value が null の company_metrics を返す。"""
    return {key: _null_metric(entry["unit"]) for key, entry in _full_company_metrics().items()}


class ValidatePassTest(unittest.TestCase):
    def test_full_research_passes_without_warnings(self):
        result = vcr.validate(_valid_research())
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_low_grade_claim_with_non_high_confidence_passes(self):
        r = _valid_research()
        # reputation を C レベル・confidence=medium にする。ERROR にはならない。
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


class CompanyMetricsTest(unittest.TestCase):
    def test_full_metrics_no_warning(self):
        result = vcr.validate(_valid_research())
        self.assertTrue(result.ok)
        self.assertFalse(any("company_metrics" in w for w in result.warnings))

    def test_partial_metrics_passes(self):
        r = _valid_research()
        m = _full_company_metrics()
        m["annual_holidays"] = _null_metric("日")
        m["turnover_rate"] = _null_metric("%")
        r["company_metrics"] = m
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertEqual(result.warnings, [])

    def test_metrics_missing_errors(self):
        r = _valid_research()
        del r["company_metrics"]
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("company_metrics" in e for e in result.errors))

    def test_metrics_not_object_errors(self):
        r = _valid_research()
        r["company_metrics"] = "年間休日125日"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("company_metrics" in e for e in result.errors))

    def test_unknown_key_errors(self):
        r = _valid_research()
        r["company_metrics"]["brand_power"] = _metric(80, "%")
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("company_metrics.brand_power" in e for e in result.errors))

    def test_non_axis_metric_keys_error(self):
        # 定量候補軸でないキーは、指標として自然な名前でも ERROR にする。
        for key in ("avg_tenure", "mid_career_ratio", "female_manager_ratio"):
            with self.subTest(key=key):
                r = _valid_research()
                r["company_metrics"][key] = _metric(5.8, "年")
                result = vcr.validate(r)
                self.assertFalse(result.ok)
                self.assertTrue(
                    any(f"company_metrics.{key}" in e for e in result.errors)
                )

    def test_auxiliary_key_passes(self):
        r = _valid_research()
        r["company_metrics"]["avg_paid_leave_days_taken"] = _metric(12.4, "日")
        result = vcr.validate(r)
        self.assertTrue(result.ok)

    def test_entry_not_object_errors(self):
        r = _valid_research()
        r["company_metrics"]["annual_holidays"] = 125
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(any("company_metrics.annual_holidays" in e for e in result.errors))

    def test_value_not_number_errors(self):
        r = _valid_research()
        r["company_metrics"]["annual_holidays"]["value"] = "125"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("company_metrics.annual_holidays.value" in e for e in result.errors)
        )

    def test_value_bool_errors(self):
        r = _valid_research()
        r["company_metrics"]["monthly_overtime"]["value"] = True
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("company_metrics.monthly_overtime.value" in e for e in result.errors)
        )

    def test_unit_mismatch_errors(self):
        r = _valid_research()
        r["company_metrics"]["compensation_level"]["unit"] = "万円"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("company_metrics.compensation_level.unit" in e for e in result.errors)
        )

    def test_source_url_missing_errors(self):
        r = _valid_research()
        del r["company_metrics"]["paid_leave_rate"]["source_url"]
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("company_metrics.paid_leave_rate.source_url" in e for e in result.errors)
        )

    def test_source_url_not_http_errors(self):
        r = _valid_research()
        r["company_metrics"]["paid_leave_rate"]["source_url"] = "edinet.example"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("company_metrics.paid_leave_rate.source_url" in e for e in result.errors)
        )

    def test_invalid_grade_errors(self):
        r = _valid_research()
        r["company_metrics"]["annual_holidays"]["grade"] = "E"
        result = vcr.validate(r)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("company_metrics.annual_holidays.grade" in e for e in result.errors)
        )

    def test_all_null_passes_with_warning(self):
        r = _valid_research()
        r["company_metrics"] = _all_null_company_metrics()
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertTrue(any("company_metrics" in w for w in result.warnings))

    def test_null_value_without_source_url_passes(self):
        r = _valid_research()
        r["company_metrics"]["equity_ratio"] = _null_metric("%")
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertEqual(result.warnings, [])

    def test_missing_as_of_warns(self):
        r = _valid_research()
        del r["company_metrics"]["turnover_rate"]["as_of"]
        result = vcr.validate(r)
        self.assertTrue(result.ok)
        self.assertTrue(
            any("company_metrics.turnover_rate.as_of" in w for w in result.warnings)
        )


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
