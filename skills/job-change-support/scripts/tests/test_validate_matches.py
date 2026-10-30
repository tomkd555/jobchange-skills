"""validate_matches.py の単体テスト。標準ライブラリの unittest のみを用いる。

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

import validate_matches as vm  # noqa: E402

POSTING_ID = "S_アクメクラウド-20261025-01"


def _cond(cid, kind, field_id, level="must", active=True):
    return {"id": cid, "kind": kind, "field_id": field_id, "level": level, "active": active}


def _wishes() -> dict:
    return {"conditions": [_cond("c001", "salary_min", "salary_min"), _cond("c002", "remote", "remote_policy"),
                           _cond("c003", "value", "custom", "want")]}


def _val(value):
    return {"value": value, "unit": None, "source_url": None, "grade": None, "as_of": None, "quote": None}


def _posting_check() -> dict:
    return {
        "posting_id": POSTING_ID,
        "job": {"salary_min": _val(6500000), "remote_policy": _val(None), "monthly_overtime_h": _val(None)},
        "company": {"avg_tenure_years": [_val(4.2), _val(None)], "labor_violation_date": _val(None)},
    }


def _valid() -> dict:
    return copy.deepcopy({
        "schema_version": "1.0",
        "posting_id": POSTING_ID,
        "checked_at": "2026-10-25",
        "match": [
            {"condition_id": "c001", "result": "meets", "basis_field_id": "salary_min", "note": "下限 650 万円が 600 万円以上"},
            {"condition_id": "c002", "result": "unknown", "basis_field_id": "remote_policy", "note": "記載がない"},
            {"condition_id": "c003", "result": "unknown", "basis_field_id": None, "note": "意思決定で評点する"},
        ],
        "unknowns": ["labor_violation_date", "monthly_overtime_h", "remote_policy"],
    })


class ValidateTest(unittest.TestCase):
    def check(self, doc, errors=0, warnings=0, needle=None, wishes=None, pc="default"):
        pc = _posting_check() if pc == "default" else pc
        r = vm.validate(doc, wishes or _wishes(), pc)
        self.assertEqual((len(r.errors), len(r.warnings)), (errors, warnings), r.errors + r.warnings)
        if needle:
            self.assertTrue(any(needle in m for m in r.errors + r.warnings), r.errors + r.warnings)

    def test_valid_with_and_without_posting_check(self):
        self.check(_valid())
        self.check(_valid(), pc=None)

    def test_root_not_object_fails(self):
        self.assertFalse(vm.validate([], _wishes()).ok)

    def test_missing_required_fields_fails(self):
        for key in ("schema_version", "posting_id", "checked_at", "match", "unknowns"):
            doc = _valid()
            del doc[key]
            self.assertFalse(vm.validate(doc, _wishes()).ok, key)

    def test_unknown_schema_version_warns(self):
        doc = _valid()
        doc["schema_version"] = "2.0"
        self.check(doc, warnings=1)

    def test_posting_id_malformed_error(self):
        doc = _valid()
        doc["posting_id"] = "bad"
        self.check(doc, errors=1, needle="posting_id", pc=None)

    def test_posting_id_differs_from_posting_check_error(self):
        doc = _valid()
        doc["posting_id"] = "S_アクメクラウド-20261025-02"
        self.check(doc, errors=1, needle="異なる")
        self.check(doc, pc=None)

    def test_checked_at_not_date_error(self):
        doc = _valid()
        doc["checked_at"] = "2026-02-30"
        self.check(doc, errors=1, needle="checked_at")

    def test_condition_id_malformed_error(self):
        doc = _valid()
        doc["match"][0]["condition_id"] = "c1"
        self.check(doc, errors=1, needle="3 桁", warnings=1)

    def test_condition_id_duplicated_error(self):
        doc = _valid()
        doc["match"][1]["condition_id"] = "c001"
        self.check(doc, errors=1, needle="重複", warnings=1)

    def test_condition_id_absent_from_wishes_error(self):
        doc = _valid()
        doc["match"][2]["condition_id"] = "c009"
        self.check(doc, errors=1, needle="c009", warnings=1)

    def test_result_outside_enum_error(self):
        doc = _valid()
        doc["match"][0]["result"] = "maybe"
        self.check(doc, errors=1, needle="result")

    def test_basis_required_for_meets_and_not_meets(self):
        for res in ("meets", "not_meets"):
            doc = _valid()
            doc["match"][0]["result"] = res
            doc["match"][0]["basis_field_id"] = None
            self.check(doc, errors=1, needle="basis_field_id")
            doc["match"][0]["basis_field_id"] = "no_such_field"
            self.check(doc, errors=1, needle="basis_field_id")

    def test_basis_null_allowed_for_unknown(self):
        doc = _valid()
        doc["match"][1]["basis_field_id"] = None
        self.check(doc)

    def test_basis_not_in_catalog_for_unknown_error(self):
        doc = _valid()
        doc["match"][1]["basis_field_id"] = "no_such_field"
        self.check(doc, errors=1, needle="辞書に無い")

    def test_note_empty_error(self):
        doc = _valid()
        doc["match"][0]["note"] = "  "
        self.check(doc, errors=1, needle="note")

    def test_unknowns_element_not_in_catalog_error(self):
        doc = _valid()
        doc["unknowns"].append("no_such_field")
        self.check(doc, errors=1, needle="辞書に無い", pc=None)

    def test_unknowns_wrong_type_error(self):
        doc = _valid()
        doc["unknowns"] = "x"
        self.check(doc, errors=1, needle="unknowns")

    def test_unknowns_names_field_with_value_error(self):
        doc = _valid()
        doc["unknowns"].append("salary_min")
        self.check(doc, errors=1, needle="非 null")
        self.check(doc, pc=None)

    def test_unknowns_misses_null_only_field_error(self):
        doc = _valid()
        doc["unknowns"].remove("monthly_overtime_h")
        self.check(doc, errors=1, needle="monthly_overtime_h")

    def test_unknowns_with_partial_null_array_error(self):
        # avg_tenure_years は 1 件に値があるので unknowns に入れると ERROR
        doc = _valid()
        doc["unknowns"].append("avg_tenure_years")
        self.check(doc, errors=1, needle="avg_tenure_years")

    def test_active_must_or_want_without_match_warns(self):
        doc = _valid()
        del doc["match"][2]
        self.check(doc, warnings=1, needle="c003")

    def test_inactive_condition_in_match_warns(self):
        wishes = _wishes()
        wishes["conditions"][2]["active"] = False
        self.check(_valid(), warnings=1, needle="無効", wishes=wishes)

    def test_inactive_condition_unmatched_no_findings(self):
        wishes = _wishes()
        wishes["conditions"][2]["active"] = False
        doc = _valid()
        del doc["match"][2]
        self.check(doc, wishes=wishes)


class CliTest(unittest.TestCase):
    def run_cli(self, doc, with_posting_check, *extra, pc=None):
        with tempfile.TemporaryDirectory() as d:
            paths = {}
            for name, data in (("matches", doc), ("wishes", _wishes()), ("pc", pc or _posting_check())):
                paths[name] = os.path.join(d, name + ".json")
                with open(paths[name], "w", encoding="utf-8") as f:
                    f.write(data if isinstance(data, str) else json.dumps(data, ensure_ascii=False))
            argv = [paths["matches"], "--wishes", paths["wishes"], *extra]
            if with_posting_check:
                argv += ["--posting-check", paths["pc"]]
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = vm.main(argv)
        return code, out.getvalue()

    def test_valid_pass_exit_0(self):
        for flag in (True, False):
            code, out = self.run_cli(_valid(), flag)
            self.assertEqual(code, 0)
            self.assertIn("PASS", out)

    def test_without_wishes_exit_2(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as cm:
            vm.main(["matches.json"])
        self.assertEqual(cm.exception.code, 2)

    def test_posting_check_only_checked_when_given(self):
        doc = _valid()
        doc["unknowns"].append("salary_min")
        self.assertEqual(self.run_cli(doc, False)[0], 0)
        self.assertEqual(self.run_cli(doc, True)[0], 1)

    def test_fail_exit_1(self):
        doc = _valid()
        doc["match"][0]["result"] = "x"
        code, out = self.run_cli(doc, False)
        self.assertEqual(code, 1)
        self.assertIn("FAIL", out)

    def test_invalid_json_exit_1(self):
        self.assertEqual(self.run_cli("{oops", False)[0], 1)

    def test_json_output_warning_status_pass(self):
        doc = _valid()
        doc["schema_version"] = "2.0"
        code, out = self.run_cli(doc, True, "--json")
        data = json.loads(out)
        self.assertEqual((code, data["status"], data["error_count"], data["warning_count"]), (0, "PASS", 0, 1))


class ExampleTest(unittest.TestCase):
    def test_asset_example_passes(self):
        assets = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets")
        load = lambda n: vm.load_json(os.path.join(assets, n))  # noqa: E731
        r = vm.validate(load("matches_example.json"), load("wishes_for_example.json"), load("posting_check_example.json"))
        self.assertEqual((r.errors, r.warnings), ([], []))


if __name__ == "__main__":
    unittest.main()
