"""validate_company_index.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_company_index
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_company_index as vci  # noqa: E402


def _valid_index() -> dict:
    """ERROR 0件・WARN 0件になる完全な company_index を返す。"""
    return {
        "schema_version": 1,
        "companies": {
            "acme-cloud": {
                "name": "アクメクラウド株式会社",
                "aliases": ["アクメクラウド", "Acme Cloud"],
                "created": "2026-07-12",
            },
            "beta-systems": {
                "name": "ベータシステムズ株式会社",
                "aliases": ["ベータシステムズ"],
                "created": "2026-07-12",
            },
        },
    }


class ValidatePassTest(unittest.TestCase):
    def test_full_index_passes_without_warnings(self):
        result = vci.validate(_valid_index())
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_empty_companies_passes(self):
        result = vci.validate({"schema_version": 1, "companies": {}})
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])

    def test_prefixed_slug_passes(self):
        idx = {
            "schema_version": 1,
            "companies": {
                "S_acme-cloud": {
                    "name": "アクメクラウド株式会社",
                    "aliases": [],
                    "created": "2026-07-18",
                }
            },
        }
        result = vci.validate(idx)
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])

    def test_japanese_slug_passes(self):
        idx = {
            "schema_version": 1,
            "companies": {
                "S_アクメクラウド": {
                    "name": "アクメクラウド株式会社",
                    "aliases": [],
                    "created": "2026-07-18",
                },
                "A_ベータシステムズ": {
                    "name": "株式会社ベータシステムズ",
                    "aliases": ["ベータシステムズ"],
                    "created": "2026-07-18",
                },
                "D_ガンマロボティクス": {
                    "name": "ガンマロボティクス株式会社",
                    "aliases": [],
                    "created": "2026-07-18",
                },
            },
        }
        result = vci.validate(idx)
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])


class ErrorCaseTest(unittest.TestCase):
    def test_root_not_object(self):
        result = vci.validate(["not", "an", "object"])
        self.assertFalse(result.ok)

    def test_missing_schema_version(self):
        idx = _valid_index()
        del idx["schema_version"]
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("schema_version" in e for e in result.errors))

    def test_missing_companies(self):
        idx = _valid_index()
        del idx["companies"]
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("companies" in e for e in result.errors))

    def test_companies_not_object(self):
        idx = _valid_index()
        idx["companies"] = ["acme-cloud"]
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("companies" in e for e in result.errors))

    def test_invalid_slug_uppercase(self):
        idx = {
            "schema_version": 1,
            "companies": {
                "Acme_Cloud": {"name": "アクメ", "aliases": [], "created": "2026-07-12"}
            },
        }
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("Acme_Cloud" in e for e in result.errors))

    def test_invalid_slug_leading_hyphen(self):
        idx = {
            "schema_version": 1,
            "companies": {
                "-acme": {"name": "アクメ", "aliases": [], "created": "2026-07-12"}
            },
        }
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("-acme" in e for e in result.errors))

    def test_entry_not_object(self):
        idx = _valid_index()
        idx["companies"]["acme-cloud"] = "文字列"
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("acme-cloud" in e for e in result.errors))

    def test_missing_name(self):
        idx = _valid_index()
        del idx["companies"]["acme-cloud"]["name"]
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("name" in e for e in result.errors))

    def test_empty_name(self):
        idx = _valid_index()
        idx["companies"]["acme-cloud"]["name"] = "   "
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("name" in e for e in result.errors))

    def test_aliases_not_list(self):
        idx = _valid_index()
        idx["companies"]["acme-cloud"]["aliases"] = "アクメクラウド"
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("aliases" in e for e in result.errors))

    def test_aliases_contains_non_string(self):
        idx = _valid_index()
        idx["companies"]["acme-cloud"]["aliases"] = ["アクメクラウド", 123]
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("aliases" in e for e in result.errors))

    def test_same_name_across_slugs(self):
        idx = _valid_index()
        idx["companies"]["gamma-corp"] = {
            "name": "アクメクラウド株式会社",
            "aliases": [],
            "created": "2026-07-12",
        }
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("アクメクラウド株式会社" in e for e in result.errors))

    def test_same_alias_across_slugs(self):
        idx = _valid_index()
        idx["companies"]["gamma-corp"] = {
            "name": "ガンマ株式会社",
            "aliases": ["Acme Cloud"],
            "created": "2026-07-12",
        }
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("Acme Cloud" in e for e in result.errors))

    def test_name_collides_with_other_alias(self):
        idx = _valid_index()
        idx["companies"]["gamma-corp"] = {
            "name": "ガンマ株式会社",
            "aliases": ["アクメクラウド株式会社"],
            "created": "2026-07-12",
        }
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("アクメクラウド株式会社" in e for e in result.errors))


class StatusFieldTest(unittest.TestCase):
    def test_status_active_passes_without_warnings(self):
        idx = _valid_index()
        idx["companies"]["acme-cloud"]["status"] = "active"
        result = vci.validate(idx)
        self.assertTrue(result.ok)
        self.assertFalse(any("status" in w for w in result.warnings))

    def test_status_closed_passes(self):
        idx = _valid_index()
        idx["companies"]["acme-cloud"]["status"] = "closed"
        result = vci.validate(idx)
        self.assertTrue(result.ok)

    def test_status_missing_is_not_checked(self):
        idx = _valid_index()
        result = vci.validate(idx)
        self.assertTrue(result.ok)
        self.assertFalse(any("status" in e for e in result.errors))
        self.assertFalse(any("status" in w for w in result.warnings))

    def test_status_invalid_value_errors(self):
        idx = _valid_index()
        idx["companies"]["acme-cloud"]["status"] = "pending"
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("status" in e for e in result.errors))

    def test_status_wrong_type_errors(self):
        idx = _valid_index()
        idx["companies"]["acme-cloud"]["status"] = 1
        result = vci.validate(idx)
        self.assertFalse(result.ok)
        self.assertTrue(any("status" in e for e in result.errors))


class ScoreFieldTest(unittest.TestCase):
    def test_score_value_passes_without_warnings(self):
        idx = _valid_index()
        idx["companies"]["acme-cloud"]["score"] = 72
        result = vci.validate(idx)
        self.assertTrue(result.ok)
        self.assertFalse(any("score" in w for w in result.warnings))

    def test_boundary_scores_pass(self):
        for value in (0, 100):
            idx = _valid_index()
            idx["companies"]["acme-cloud"]["score"] = value
            result = vci.validate(idx)
            self.assertTrue(result.ok, f"score={value} should pass")

    def test_score_missing_is_not_checked(self):
        idx = _valid_index()
        result = vci.validate(idx)
        self.assertTrue(result.ok)
        self.assertFalse(any("score" in e for e in result.errors))
        self.assertFalse(any("score" in w for w in result.warnings))

    def test_score_out_of_range_errors(self):
        for value in (-1, 101):
            idx = _valid_index()
            idx["companies"]["acme-cloud"]["score"] = value
            result = vci.validate(idx)
            self.assertFalse(result.ok, f"score={value} should fail")
            self.assertTrue(any("score" in e for e in result.errors))

    def test_score_wrong_type_errors(self):
        for value in ("A", 72.5, True, None):
            idx = _valid_index()
            idx["companies"]["acme-cloud"]["score"] = value
            result = vci.validate(idx)
            self.assertFalse(result.ok, f"score={value!r} should fail")
            self.assertTrue(any("score" in e for e in result.errors))


class WarnCaseTest(unittest.TestCase):
    def test_missing_created_warns_but_passes(self):
        idx = _valid_index()
        del idx["companies"]["acme-cloud"]["created"]
        result = vci.validate(idx)
        self.assertTrue(result.ok)
        self.assertTrue(any("created" in w for w in result.warnings))

    def test_duplicate_aliases_within_entry_warns(self):
        idx = _valid_index()
        idx["companies"]["acme-cloud"]["aliases"] = ["アクメクラウド", "アクメクラウド"]
        result = vci.validate(idx)
        self.assertTrue(result.ok)
        self.assertTrue(any("aliases" in w for w in result.warnings))

    def test_name_equals_own_alias_warns(self):
        idx = _valid_index()
        idx["companies"]["acme-cloud"]["aliases"] = ["アクメクラウド株式会社", "Acme Cloud"]
        result = vci.validate(idx)
        self.assertTrue(result.ok)
        self.assertTrue(any("aliases" in w for w in result.warnings))


class CliTest(unittest.TestCase):
    def _write_tmp(self, obj) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def test_main_returns_0_on_valid(self):
        path = self._write_tmp(_valid_index())
        self.assertEqual(vci.main([path]), 0)

    def test_main_returns_1_on_invalid(self):
        idx = _valid_index()
        del idx["schema_version"]
        path = self._write_tmp(idx)
        self.assertEqual(vci.main([path]), 1)

    def test_main_returns_1_on_broken_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{ not valid json ")
        self.addCleanup(os.remove, path)
        self.assertEqual(vci.main([path]), 1)

    def test_main_json_flag_valid(self):
        path = self._write_tmp(_valid_index())
        self.assertEqual(vci.main([path, "--json"]), 0)

    def test_main_returns_0_on_valid_with_bom(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8-sig") as f:
            json.dump(_valid_index(), f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        self.assertEqual(vci.main([path]), 0)


class ResultShapeTest(unittest.TestCase):
    def test_to_dict_shape(self):
        result = vci.validate(_valid_index())
        d = result.to_dict()
        self.assertEqual(d["status"], "PASS")
        self.assertEqual(d["error_count"], 0)
        self.assertIn("warnings", d)

    def test_immutability_of_input(self):
        idx = _valid_index()
        snapshot = copy.deepcopy(idx)
        vci.validate(idx)
        self.assertEqual(idx, snapshot)


if __name__ == "__main__":
    unittest.main()
