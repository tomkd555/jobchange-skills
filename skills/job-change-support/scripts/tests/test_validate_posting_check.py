"""validate_posting_check.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_posting_check as vpc  # noqa: E402

URL = "https://example.com/careers/123"


def _v(value, unit=None, as_of="2026-10-25"):
    if value is None:
        return {"value": None, "unit": unit, "source_url": None, "grade": None, "as_of": None, "quote": None}
    return {"value": value, "unit": unit, "source_url": URL, "grade": "A", "as_of": as_of, "quote": "引用"}


# 値の型と単位を辞書に合わせた、必ず書く項目の全部を持つ完全な例
_JOB = {
    "company_name": _v("アクメクラウド株式会社"), "job_title": _v("インフラエンジニア"), "industry": _v("SaaS"),
    "employment_type": _v("full_time"), "work_location": _v("東京都"), "remote_policy": _v("hybrid"),
    "salary_min": _v(6500000, "円"), "salary_max": _v(9000000, "円"), "salary_basis": _v("annual"),
    "fixed_overtime_included": _v(True), "fixed_overtime_hours": _v(30, "時間"),
    "scheduled_hours": _v(7.5, "時間"), "annual_holidays": _v(125, "日"),
    "monthly_overtime_h": _v(20, "時間"), "paid_leave_rate": _v(70, "%"),
    "scope_of_change_duties": _v("会社の定める業務"), "scope_of_change_location": _v("会社の定める事業所"),
    "contract_renewal_cap": _v("なし"), "requirements_must": _v(["AWS 経験"]),
    "requirements_want": _v(["Terraform"]), "selection_process": _v(["書類", "面接"]),
    "posted_at": _v("2026-10-20"),
}
_COMPANY = {
    "legal_entity_name": _v("アクメクラウド株式会社", as_of="2026-03"), "employee_count": _v(820, "人", "2026-03"),
    "avg_age": _v(35.2, "歳", "2026-03"),
    "avg_tenure_years": [_v(4.2, "年", "2026-03"), _v(4.5, "年", "2025")],
    "avg_annual_salary": _v(7200000, "円", "2026-03"), "revenue_growth": _v(12.5, "%", "2026-03"),
    "operating_margin": _v(8.1, "%", "2026-03"), "equity_ratio": _v(55.0, "%", "2026-03"),
    "labor_violation_listed": _v(False, as_of="2026-09-30"), "labor_violation_date": _v(None),
}


def _valid() -> dict:
    """ERROR 0件・WARN 0件になる完全な posting-check を返す。"""
    return copy.deepcopy({
        "schema_version": "1.0",
        "posting_id": "S_アクメクラウド-20261025-01",
        "company_slug": "S_アクメクラウド",
        "source_type": "url",
        "source_url": URL,
        "fetched_at": "2026-10-25",
        "job": _JOB,
        "company": _COMPANY,
        "open_questions": ["確認事項"],
    })


class ValidateTest(unittest.TestCase):
    def check(self, doc, errors=0, warnings=0, needle=None):
        r = vpc.validate(doc)
        self.assertEqual((len(r.errors), len(r.warnings)), (errors, warnings), r.errors + r.warnings)
        if needle:
            self.assertTrue(any(needle in m for m in r.errors + r.warnings), r.errors + r.warnings)

    def test_valid_doc_no_findings(self):
        self.check(_valid())

    def test_catalog_complete_for_always_write(self):
        # 必ず書く項目の一覧が辞書の項目と食い違うと、完全な例が WARN を出す
        doc = _valid()
        self.assertEqual(set(doc["job"]), set(vpc.ALWAYS_WRITE_JOB))
        self.assertEqual(set(doc["company"]), set(vpc.ALWAYS_WRITE_COMPANY))

    def test_root_not_object_error(self):
        self.check([], errors=1)

    def test_missing_root_fields_fails(self):
        for key in ("schema_version", "posting_id", "source_type", "fetched_at", "job", "company", "open_questions"):
            doc = _valid()
            del doc[key]
            self.assertFalse(vpc.validate(doc).ok, key)

    def test_unknown_schema_version_warns(self):
        doc = _valid()
        doc["schema_version"] = "9.9"
        self.check(doc, warnings=1)

    def test_posting_id_malformed_error(self):
        doc = _valid()
        doc["posting_id"] = "S_アクメクラウド-2026-1"
        self.check(doc, errors=1, needle="posting_id")

    def test_posting_id_slug_mismatch_error(self):
        doc = _valid()
        doc["company_slug"] = "S_別会社"
        self.check(doc, errors=1, needle="company_slug")

    def test_posting_id_date_mismatch_error(self):
        doc = _valid()
        doc["fetched_at"] = "2026-10-26"
        self.check(doc, errors=1, needle="日付部分")

    def test_parse_posting_id_valid_returns_slug_date_seq(self):
        self.assertEqual(vpc.parse_posting_id("S_アクメクラウド-20261025-01"), ("S_アクメクラウド", "20261025", "01"))
        self.assertEqual(vpc.parse_posting_id("a-b-20261025-02"), ("a-b", "20261025", "02"))

    def test_parse_posting_id_malformed_returns_none(self):
        self.assertIsNone(vpc.parse_posting_id("-20261025-01"))
        self.assertIsNone(vpc.parse_posting_id(None))

    def test_source_type_invalid_error(self):
        doc = _valid()
        doc["source_type"] = "mail"
        self.check(doc, errors=1, needle="source_type")

    def test_source_url_missing_for_url_and_search_error(self):
        for st in ("url", "search"):
            doc = _valid()
            doc["source_type"] = st
            doc["source_url"] = None
            self.check(doc, errors=1, needle="source_url")

    def test_source_url_ftp_scheme_error(self):
        doc = _valid()
        doc["source_url"] = "ftp://x"
        self.check(doc, errors=1, needle="source_url")

    def test_source_url_null_allowed_for_text(self):
        doc = _valid()
        doc["source_type"] = "scout"
        doc["source_url"] = None
        self.check(doc)

    def test_fetched_at_not_date_fails(self):
        doc = _valid()
        doc["fetched_at"] = "2026-13-40"
        self.assertFalse(vpc.validate(doc).ok)

    def test_unknown_key_error(self):
        doc = _valid()
        doc["job"]["bogus"] = _v("x")
        self.check(doc, errors=1, needle="辞書に無い")

    def test_wrong_section_error(self):
        doc = _valid()
        doc["job"]["employee_count"] = _v(10, "人")
        self.check(doc, errors=1, needle="company の項目")
        doc = _valid()
        doc["company"]["job_title"] = _v("x")
        self.check(doc, errors=1, needle="posting の項目")

    def test_job_value_array_error(self):
        doc = _valid()
        doc["job"]["salary_min"] = [_v(6500000, "円")]
        self.check(doc, errors=1, needle="配列にせず")

    def test_company_array_checks_each_entry(self):
        doc = _valid()
        doc["company"]["avg_tenure_years"][1]["unit"] = "月"
        self.check(doc, errors=1, needle="avg_tenure_years[1]")

    def test_value_object_missing_key_error(self):
        doc = _valid()
        del doc["job"]["salary_min"]["as_of"]
        self.check(doc, errors=1, needle="as_of")

    def test_value_type_mismatch_fails(self):
        for field, bad in (("salary_min", "650万"), ("employment_type", "forever"),
                           ("posted_at", "2026-02-30"), ("requirements_must", ["a", 1])):
            doc = _valid()
            doc["job"][field]["value"] = bad
            self.assertFalse(vpc.validate(doc).ok, field)

    def test_unit_mismatch_error(self):
        doc = _valid()
        doc["job"]["salary_min"]["unit"] = "万円"
        self.check(doc, errors=1, needle="unit")

    def test_value_without_source_url_error(self):
        doc = _valid()
        doc["job"]["salary_min"]["source_url"] = None
        self.check(doc, errors=1, needle="source_url")

    def test_value_grade_outside_enum_error(self):
        doc = _valid()
        doc["job"]["salary_min"]["grade"] = "Z"
        self.check(doc, errors=1, needle="grade")

    def test_value_as_of_not_date_error(self):
        doc = _valid()
        doc["job"]["salary_min"]["as_of"] = "令和8年"
        self.check(doc, errors=1, needle="as_of")

    def test_open_questions_non_string_error(self):
        doc = _valid()
        doc["open_questions"] = ["ok", 3]
        self.check(doc, errors=1, needle="open_questions")

    def test_missing_always_write_field_warns(self):
        doc = _valid()
        del doc["job"]["annual_holidays"]
        del doc["company"]["equity_ratio"]
        self.check(doc, warnings=2, needle="必ず書く")

    def test_legal_fields_null_warn(self):
        for field in vpc.LEGAL_JOB_FIELDS:
            doc = _valid()
            doc["job"][field] = _v(None)
            self.check(doc, warnings=1, needle=field)

    def test_fixed_term_without_renewal_cap_warns(self):
        for et in ("contract", "temporary"):
            doc = _valid()
            doc["job"]["employment_type"]["value"] = et
            doc["job"]["contract_renewal_cap"] = _v(None)
            self.check(doc, warnings=1, needle="更新上限")

    def test_full_time_without_renewal_cap_no_findings(self):
        doc = _valid()
        doc["job"]["contract_renewal_cap"] = _v(None)
        self.check(doc)

    def test_grade_c_warns(self):
        doc = _valid()
        doc["job"]["salary_min"]["grade"] = "C"
        self.check(doc, warnings=1, needle="grade が C")


class CliTest(unittest.TestCase):
    def run_cli(self, doc, *extra):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "posting-check.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(doc if isinstance(doc, str) else json.dumps(doc, ensure_ascii=False))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = vpc.main([path, *extra])
        return code, out.getvalue()

    def test_pass_exit_0(self):
        code, out = self.run_cli(_valid())
        self.assertEqual(code, 0)
        self.assertIn("PASS", out)

    def test_warn_only_exit_0(self):
        doc = _valid()
        doc["schema_version"] = "9.9"
        self.assertEqual(self.run_cli(doc)[0], 0)

    def test_fail_exit_1(self):
        doc = _valid()
        doc["source_type"] = "x"
        code, out = self.run_cli(doc)
        self.assertEqual(code, 1)
        self.assertIn("FAIL", out)

    def test_invalid_json_exit_1(self):
        self.assertEqual(self.run_cli("{not json")[0], 1)

    def test_missing_file_exit_1(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(vpc.main(["no-such-file.json"]), 1)

    def test_json_output_warning_status_pass(self):
        doc = _valid()
        doc["schema_version"] = "9.9"
        code, out = self.run_cli(doc, "--json")
        data = json.loads(out)
        self.assertEqual((code, data["status"], data["error_count"], data["warning_count"]), (0, "PASS", 0, 1))


def _always_write_terms(section: str) -> tuple[str, ...]:
    """posting-check-format.md の「Always write in `job`:」の行からバックティック囲みの項目を順に返す。"""
    import re
    md = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                      "references", "posting-check-format.md")
    with open(md, encoding="utf-8") as f:
        for line in f:
            if line.startswith(f"Always write in `{section}`:"):
                return tuple(re.findall(r"`([^`]+)`", line)[1:])
    raise AssertionError(f"posting-check-format.md に Always write in `{section}` の行が無い")


class VocabularySyncTest(unittest.TestCase):
    """必ず書く項目の一覧が、形式の文書と検証スクリプトで一致すること。"""

    def test_always_write_lists_match_format(self):
        self.assertEqual(_always_write_terms("job"), vpc.ALWAYS_WRITE_JOB)
        self.assertEqual(_always_write_terms("company"), vpc.ALWAYS_WRITE_COMPANY)


class ExampleTest(unittest.TestCase):
    def test_asset_example_passes(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            "assets", "posting_check_example.json")
        r = vpc.validate(vpc.load_json(path))
        self.assertEqual((r.errors, r.warnings), ([], []))


if __name__ == "__main__":
    unittest.main()
