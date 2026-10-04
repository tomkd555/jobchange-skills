"""split_profile.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest scripts.tests.test_split_profile
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import split_profile as sp  # noqa: E402
import validate_profile as vp  # noqa: E402
from test_validate_profile import _valid_profile, _valid_v2_profile, _valid_v3_profile  # noqa: E402


class SplitProfileTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name
        self.profile_path = os.path.join(self.dir, "profile.json")
        self.axis_path = os.path.join(self.dir, "axis.json")

    def _write(self, document: dict) -> None:
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(document, f, ensure_ascii=False)

    def _read(self, path: str) -> dict:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def test_v2_profile_is_split_into_two_valid_files(self):
        source = _valid_v2_profile()
        self._write(source)
        report = sp.run(self.profile_path)

        self.assertEqual(report["status"], "PASS")
        profile, axis = self._read(self.profile_path), self._read(self.axis_path)
        self.assertEqual(profile["schema_version"], "3.0")
        self.assertEqual(axis["schema_version"], "2.0")
        for key in vp._AXIS_KEYS:
            self.assertNotIn(key, profile)
            self.assertEqual(axis[key], source[key])
        self.assertEqual(profile["career_history"], source["career_history"])
        self.assertEqual(axis["updated_at"], source["updated_at"])
        self.assertEqual(self._read(report["backup"]), source)
        self.assertEqual(report["profile_validation"]["status"], "PASS")
        self.assertEqual(report["axis_validation"]["status"], "PASS")

    def test_v1_axis_keeps_its_version_and_backup_is_named_after_it(self):
        self._write(_valid_profile())
        self.assertEqual(sp.run(self.profile_path)["status"], "PASS")
        self.assertEqual(self._read(self.axis_path)["schema_version"], "1.0")
        self.assertTrue(os.path.exists(self.profile_path + ".bak-1.0"))

    def test_unknown_key_stays_in_the_profile_and_is_reported(self):
        source = _valid_v2_profile()
        source["memo_by_hand"] = "手で足したキー"
        self._write(source)
        report = sp.run(self.profile_path)
        self.assertEqual(report["unknown_keys"], ["memo_by_hand"])
        self.assertEqual(self._read(self.profile_path)["memo_by_hand"], "手で足したキー")

    def test_unfinished_axis_is_split_and_reported(self):
        source = _valid_v2_profile()
        source["job_change_axis"]["reasons"] = []
        self._write(source)
        report = sp.run(self.profile_path)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["profile_validation"]["status"], "PASS")
        self.assertEqual(report["axis_validation"]["status"], "FAIL")

    def test_existing_files_are_refused_and_left_untouched(self):
        source = _valid_v2_profile()
        for leftover in ("axis.json", "profile.json.bak-2.0", "profile.json.tmp"):
            with self.subTest(leftover=leftover):
                self._write(source)
                leftover_path = os.path.join(self.dir, leftover)
                with open(leftover_path, "w", encoding="utf-8") as f:
                    f.write("利用者のファイル")
                report = sp.run(self.profile_path)
                self.assertEqual(report["status"], "FAIL")
                self.assertEqual(self._read(self.profile_path), source)
                with open(leftover_path, encoding="utf-8") as f:
                    self.assertEqual(f.read(), "利用者のファイル")
                self.assertEqual(sorted(os.listdir(self.dir)), sorted(["profile.json", leftover]))
                os.remove(leftover_path)

    def test_unsupported_input_is_refused_and_left_untouched(self):
        broken = os.path.join(self.dir, "broken.json")
        with open(broken, "w", encoding="utf-8") as f:
            f.write("{ not json")
        for label, document in (("3.0 の profile", _valid_v3_profile()), ("版が数値", {"schema_version": 2.0})):
            with self.subTest(label):
                self._write(document)
                self.assertEqual(sp.run(self.profile_path)["status"], "FAIL")
                self.assertEqual(self._read(self.profile_path), document)
                self.assertEqual(sorted(os.listdir(self.dir)), ["broken.json", "profile.json"])
        with self.subTest("壊れた JSON"):
            self.assertEqual(sp.run(broken)["status"], "FAIL")

    def test_failed_replace_restores_the_original_state(self):
        source = _valid_v2_profile()
        self._write(source)
        for error in (OSError("置き換えに失敗"), UnicodeEncodeError("utf-8", "", 0, 1, "書けない文字")):
            with self.subTest(error=type(error).__name__):
                with mock.patch.object(sp.os, "replace", side_effect=error):
                    report = sp.run(self.profile_path)
                self.assertEqual(report["status"], "FAIL")
                self.assertEqual(self._read(self.profile_path), source)
                self.assertEqual(os.listdir(self.dir), ["profile.json"])

    def test_cli_exit_codes(self):
        self._write(_valid_v2_profile())
        with contextlib.redirect_stdout(io.StringIO()) as out:
            first = sp.main([self.profile_path, "--json"])
        self.assertEqual(first, 0)
        self.assertEqual(
            sorted(json.loads(out.getvalue())),
            ["axis", "axis_validation", "backup", "errors", "profile", "profile_validation", "status", "unknown_keys"],
        )
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sp.main([self.profile_path]), 1)


if __name__ == "__main__":
    unittest.main()
