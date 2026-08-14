"""validate_job_posting.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_job_posting
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_job_posting as vjp  # noqa: E402


def _valid_posting() -> dict:
    """ERROR 0件・WARN 0件になる完全な job_posting.json を返す。"""
    return {
        "schema_version": "1.0",
        "source_type": "url",
        "source_url": "https://recruit.example.co.jp/jobs/1234",
        "fetched_at": "2026-07-17",
        "company_name": "架空クラウドワークス株式会社",
        "title": "バックエンドエンジニア（中途）",
        "employment_type": "正社員",
        "location": {"work_location": "東京都渋谷区", "remote_policy": "週3リモート可"},
        "salary": {
            "min": 6000000,
            "max": 9000000,
            "currency": "JPY",
            "basis": "年収",
            "notes": "経験・能力を考慮のうえ決定",
        },
        "working_hours": {
            "scheduled_hours": 7.5,
            "break_minutes": 60,
            "discretionary": False,
            "overtime_notes": "月平均20時間程度",
        },
        "metrics": {
            "annual_holidays": {"value": 125, "quote": "年間休日125日"},
            "monthly_overtime_h": {"value": 20, "quote": "月平均残業20時間"},
            "paid_leave_rate": {"value": 71.0, "quote": "有給取得率71%"},
            "paid_leave_days_granted": {"value": 20, "quote": "有給付与20日"},
        },
        "requirements": {
            "must": ["Webアプリのバックエンド開発経験3年以上"],
            "want": ["AWS の実務経験"],
        },
        "benefits": [
            {"name": "健康保険", "quote": "各種社会保険完備"},
            {"name": "書籍購入補助", "quote": "技術書は全額会社負担"},
        ],
        "selection_process": ["書類選考", "適性検査", "一次面接", "最終面接"],
        "open_questions": [],
    }


def _minimal_posting() -> dict:
    """必須項目のみを持つ最小の job_posting.json を返す。"""
    return {
        "schema_version": "1.0",
        "source_type": "url",
        "source_url": "https://recruit.example.co.jp/jobs/1",
        "fetched_at": "2026-07-17",
        "company_name": "架空株式会社",
        "title": "エンジニア",
    }


def _dialogue_posting() -> dict:
    """対話で聞き取った、URL を持たない最小の job_posting.json を返す。"""
    return {
        "schema_version": "1.0",
        "source_type": "dialogue",
        "source_url": None,
        "fetched_at": "2026-07-17",
        "company_name": "架空株式会社",
        "title": "エンジニア",
        "open_questions": ["年間休日と残業時間は未確認である"],
    }


class ValidatePassTest(unittest.TestCase):
    def test_full_posting_passes_without_warnings(self):
        result = vjp.validate(_valid_posting())
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_minimal_posting_passes(self):
        result = vjp.validate(_minimal_posting())
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


class RootErrorTest(unittest.TestCase):
    def test_root_not_object(self):
        result = vjp.validate(["not", "an", "object"])
        self.assertFalse(result.ok)


class SourceTypeTest(unittest.TestCase):
    """取込の入口を表す source_type と、それに応じた source_url の検査。"""

    def test_dialogue_posting_passes(self):
        result = vjp.validate(_dialogue_posting())
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.warnings, [])

    def test_missing_source_type(self):
        p = _valid_posting()
        del p["source_type"]
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("source_type" in e for e in result.errors))

    def test_unknown_source_type(self):
        p = _valid_posting()
        p["source_type"] = "scraped"
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("source_type" in e for e in result.errors))

    def test_text_source_allows_null_source_url(self):
        p = _valid_posting()
        p["source_type"] = "text"
        p["source_url"] = None
        result = vjp.validate(p)
        self.assertTrue(result.ok, result.errors)

    def test_file_source_allows_absent_source_url(self):
        p = _valid_posting()
        p["source_type"] = "file"
        del p["source_url"]
        result = vjp.validate(p)
        self.assertTrue(result.ok, result.errors)

    def test_dialogue_source_allows_absent_source_url(self):
        p = _valid_posting()
        p["source_type"] = "dialogue"
        del p["source_url"]
        result = vjp.validate(p)
        self.assertTrue(result.ok, result.errors)

    def test_non_url_source_keeps_reference_url(self):
        """URL 以外の入口でも、参考の URL を持つこと自体は妨げない。"""
        p = _valid_posting()
        p["source_type"] = "text"
        p["source_url"] = "https://recruit.example.co.jp/jobs/1234"
        result = vjp.validate(p)
        self.assertTrue(result.ok, result.errors)


class RequiredFieldErrorTest(unittest.TestCase):
    def test_missing_schema_version(self):
        p = _valid_posting()
        del p["schema_version"]
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("schema_version" in e for e in result.errors))

    def test_missing_source_url(self):
        p = _valid_posting()
        del p["source_url"]
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("source_url" in e for e in result.errors))

    def test_source_url_not_http(self):
        p = _valid_posting()
        p["source_url"] = "recruit.example.co.jp/jobs/1"
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("source_url" in e for e in result.errors))

    def test_missing_fetched_at(self):
        p = _valid_posting()
        del p["fetched_at"]
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("fetched_at" in e for e in result.errors))

    def test_malformed_fetched_at(self):
        p = _valid_posting()
        p["fetched_at"] = "2026/07/17"
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("fetched_at" in e for e in result.errors))

    def test_invalid_date_fetched_at(self):
        p = _valid_posting()
        p["fetched_at"] = "2026-13-40"
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("fetched_at" in e for e in result.errors))

    def test_missing_company_name(self):
        p = _valid_posting()
        p["company_name"] = "  "
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("company_name" in e for e in result.errors))

    def test_missing_title(self):
        p = _valid_posting()
        del p["title"]
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("title" in e for e in result.errors))


class SchemaVersionWarnTest(unittest.TestCase):
    def test_unknown_schema_version_warns(self):
        p = _valid_posting()
        p["schema_version"] = "2.0"
        result = vjp.validate(p)
        self.assertTrue(result.ok)
        self.assertTrue(any("schema_version" in w for w in result.warnings))


class MetricsTest(unittest.TestCase):
    def test_metrics_absent_is_normal(self):
        p = _minimal_posting()
        result = vjp.validate(p)
        self.assertTrue(result.ok)
        self.assertFalse(any("metrics" in w for w in result.warnings))
        self.assertFalse(any("metrics" in e for e in result.errors))

    def test_metric_null_is_normal(self):
        p = _valid_posting()
        p["metrics"]["annual_holidays"] = None
        result = vjp.validate(p)
        self.assertTrue(result.ok)
        self.assertEqual(result.warnings, [])

    def test_metrics_not_object_errors(self):
        p = _valid_posting()
        p["metrics"] = "125日"
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("metrics" in e for e in result.errors))

    def test_metric_value_not_number_errors(self):
        p = _valid_posting()
        p["metrics"]["annual_holidays"] = {"value": "125", "quote": "年間休日125日"}
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("metrics.annual_holidays.value" in e for e in result.errors))

    def test_metric_value_bool_errors(self):
        p = _valid_posting()
        p["metrics"]["monthly_overtime_h"] = {"value": True, "quote": "残業あり"}
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("metrics.monthly_overtime_h.value" in e for e in result.errors))

    def test_metric_missing_quote_errors(self):
        p = _valid_posting()
        p["metrics"]["paid_leave_rate"] = {"value": 71.0, "quote": ""}
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("metrics.paid_leave_rate.quote" in e for e in result.errors))

    def test_metric_scalar_instead_of_object_errors(self):
        p = _valid_posting()
        p["metrics"]["annual_holidays"] = 125
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("metrics.annual_holidays" in e for e in result.errors))


class OptionalShapeTest(unittest.TestCase):
    def test_salary_not_object_errors(self):
        p = _valid_posting()
        p["salary"] = "年収600万円"
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("salary" in e for e in result.errors))

    def test_selection_process_not_list_errors(self):
        p = _valid_posting()
        p["selection_process"] = "書類選考のみ"
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("selection_process" in e for e in result.errors))

    def test_benefit_missing_name_errors(self):
        p = _valid_posting()
        p["benefits"] = [{"quote": "各種手当あり"}]
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("benefits[0].name" in e for e in result.errors))

    def test_benefit_not_object_errors(self):
        p = _valid_posting()
        p["benefits"] = ["健康保険"]
        result = vjp.validate(p)
        self.assertFalse(result.ok)
        self.assertTrue(any("benefits[0]" in e for e in result.errors))


class CliTest(unittest.TestCase):
    def _write_tmp(self, obj) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def test_main_returns_0_on_valid(self):
        path = self._write_tmp(_valid_posting())
        self.assertEqual(vjp.main([path]), 0)

    def test_main_returns_1_on_invalid(self):
        p = _valid_posting()
        del p["company_name"]
        path = self._write_tmp(p)
        self.assertEqual(vjp.main([path]), 1)

    def test_main_returns_1_on_broken_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{ not valid json ")
        self.addCleanup(os.remove, path)
        self.assertEqual(vjp.main([path]), 1)

    def test_main_json_flag_valid(self):
        path = self._write_tmp(_valid_posting())
        self.assertEqual(vjp.main([path, "--json"]), 0)

    def test_main_returns_0_on_valid_with_bom(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8-sig") as f:
            json.dump(_valid_posting(), f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        self.assertEqual(vjp.main([path]), 0)


class ResultShapeTest(unittest.TestCase):
    def test_to_dict_shape(self):
        result = vjp.validate(_valid_posting())
        d = result.to_dict()
        self.assertEqual(d["status"], "PASS")
        self.assertEqual(d["error_count"], 0)
        self.assertIn("warnings", d)

    def test_immutability_of_input(self):
        p = _valid_posting()
        snapshot = copy.deepcopy(p)
        vjp.validate(p)
        self.assertEqual(p, snapshot)


class ExampleAssetTest(unittest.TestCase):
    def test_bundled_example_passes(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        document = vjp.load_posting(os.path.join(base, "assets", "job_posting_example.json"))
        result = vjp.validate(document)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


if __name__ == "__main__":
    unittest.main()
