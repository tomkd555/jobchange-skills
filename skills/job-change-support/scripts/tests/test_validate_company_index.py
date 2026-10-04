"""validate_company_index.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_company_index
"""
from __future__ import annotations

import contextlib
import io
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


def _entry(name: str, aliases=None) -> dict:
    return {"name": name, "aliases": aliases or [], "created": "2026-07-12"}


def _acme(idx: dict) -> dict:
    return idx["companies"]["acme-cloud"]


class ValidateTest(unittest.TestCase):
    def test_valid_indexes_pass_without_warnings(self):
        rows = [
            ("完全な一覧", _valid_index()),
            ("companies が空", {"schema_version": 1, "companies": {}}),
            (
                "接頭辞付きと日本語のスラッグ",
                {
                    "schema_version": 1,
                    "companies": {
                        "S_acme-cloud": _entry("アクメクラウド株式会社"),
                        "A_ベータシステムズ": _entry("株式会社ベータシステムズ"),
                    },
                },
            ),
        ]
        for label, idx in rows:
            with self.subTest(label):
                result = vci.validate(idx)
                self.assertEqual((result.errors, result.warnings), ([], []))

    def test_bundled_example_passes(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        document = vci.load_index(os.path.join(base, "assets", "company_index_example.json"))
        result = vci.validate(document)
        self.assertEqual((result.errors, result.warnings), ([], []))

    def test_error_rules(self):
        # (ラベル, 変更, 期待する ERROR の部分文字列)。変更が値を返したらそれを文書とする
        rows = [
            ("ルートがオブジェクトでない", lambda i: ["x"], "(root)"),
            ("schema_version の欠落", lambda i: i.pop("schema_version"), "schema_version"),
            ("schema_version の型違い（bool）", lambda i: i.__setitem__("schema_version", True), "schema_version"),
            ("companies の欠落", lambda i: i.pop("companies"), "companies"),
            ("スラッグが大文字の接頭辞外", lambda i: i["companies"].__setitem__("Acme_Cloud", _entry("x")), "Acme_Cloud"),
            ("スラッグ先頭のハイフン", lambda i: i["companies"].__setitem__("-acme", _entry("x")), "-acme"),
            ("エントリがオブジェクトでない", lambda i: i["companies"].__setitem__("acme-cloud", "文字列"), "acme-cloud"),
            ("name が空白", lambda i: _acme(i).__setitem__("name", "  "), ".name"),
            ("aliases が配列でない", lambda i: _acme(i).__setitem__("aliases", "x"), "aliases"),
            ("aliases に文字列以外", lambda i: _acme(i).__setitem__("aliases", ["a", 1]), "aliases"),
            ("status が列挙外", lambda i: _acme(i).__setitem__("status", "pending"), ".status"),
            ("score が範囲外", lambda i: _acme(i).__setitem__("score", 101), ".score"),
            ("score が bool", lambda i: _acme(i).__setitem__("score", True), ".score"),
            (
                "name が他スラッグの name と衝突",
                lambda i: i["companies"].__setitem__("gamma", _entry("アクメクラウド株式会社")),
                "複数のスラッグ",
            ),
            (
                "alias が他スラッグの alias と衝突",
                lambda i: i["companies"].__setitem__("gamma", _entry("ガンマ", ["Acme Cloud"])),
                "Acme Cloud",
            ),
            (
                "name が他スラッグの alias と衝突",
                lambda i: i["companies"].__setitem__("gamma", _entry("ガンマ", ["アクメクラウド株式会社"])),
                "複数のスラッグ",
            ),
        ]
        for label, mutate, expected in rows:
            with self.subTest(label):
                idx = _valid_index()
                replaced = mutate(idx)
                if isinstance(replaced, list):
                    idx = replaced
                result = vci.validate(idx)
                self.assertFalse(result.ok)
                self.assertTrue(any(expected in e for e in result.errors), result.errors)

    def test_warn_rules(self):
        rows = [
            ("created の欠落", lambda i: _acme(i).pop("created"), "created"),
            ("aliases の重複", lambda i: _acme(i).__setitem__("aliases", ["a", "a"]), "重複"),
            ("name と同一の alias", lambda i: _acme(i).__setitem__("aliases", ["アクメクラウド株式会社"]), "name と同一"),
            ("未知の schema_version", lambda i: i.__setitem__("schema_version", 2), "既知のバージョン"),
        ]
        for label, mutate, expected in rows:
            with self.subTest(label):
                idx = _valid_index()
                mutate(idx)
                result = vci.validate(idx)
                self.assertEqual(result.errors, [])
                self.assertTrue(any(expected in w for w in result.warnings), result.warnings)

    def test_optional_fields_accept_boundary_values(self):
        for field, value in (("status", "active"), ("status", "closed"), ("score", 0), ("score", 100)):
            with self.subTest(f"{field}={value}"):
                idx = _valid_index()
                _acme(idx)[field] = value
                result = vci.validate(idx)
                self.assertEqual((result.errors, result.warnings), ([], []))


class CliTest(unittest.TestCase):
    def _write(self, text: str, encoding: str = "utf-8") -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(text)
        self.addCleanup(os.remove, path)
        return path

    def _run(self, argv) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = vci.main(argv)
        return code, buf.getvalue()

    def test_exit_codes(self):
        valid = json.dumps(_valid_index(), ensure_ascii=False)
        invalid = _valid_index()
        del invalid["schema_version"]
        rows = [
            ("正常", self._write(valid), 0),
            ("BOM 付きの正常", self._write(valid, "utf-8-sig"), 0),
            ("検証エラー", self._write(json.dumps(invalid)), 1),
            ("壊れた JSON", self._write("{ not valid json "), 1),
            ("存在しないファイル", os.path.join(tempfile.gettempdir(), "no-such-index.json"), 1),
        ]
        for label, path, expected in rows:
            with self.subTest(label):
                self.assertEqual(self._run([path])[0], expected)

    def test_json_output_keys(self):
        path = self._write(json.dumps(_valid_index()))
        code, out = self._run([path, "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(
            sorted(data),
            ["error_count", "errors", "status", "warning_count", "warnings"],
        )


if __name__ == "__main__":
    unittest.main()
