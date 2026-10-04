"""validate_axis.py の単体テスト。標準ライブラリの unittest のみを用いる。

軸の規則そのものは test_validate_profile.py が検査する。ここでは入口の振る舞い
（受け付ける文書の版、3.0 の拒否、updated_at と既知の版の検査）だけを見る。

実行:
    python -m unittest scripts.tests.test_validate_axis
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import validate_axis as va  # noqa: E402
import validate_profile as vp  # noqa: E402
from test_validate_profile import _valid_profile, _valid_v2_profile, _valid_v3_profile  # noqa: E402


def _valid_axis() -> dict:
    """axis.json（schema_version 2.0）として成立する文書を返す。"""
    profile = _valid_v2_profile()
    axis = {key: profile[key] for key in vp._AXIS_KEYS if key in profile}
    axis["schema_version"] = "2.0"
    axis["updated_at"] = profile["updated_at"]
    return axis


_ASSETS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets"
)


class ValidateAxisTest(unittest.TestCase):
    def test_accepted_documents(self):
        rows = [
            ("職歴キーの無い axis.json", _valid_axis(), None),
            ("軸を内包する 2.0 の profile.json", _valid_v2_profile(), None),
            ("1.x の文書は移行推奨の WARN", _valid_profile(), "2.0 への移行"),
        ]
        for label, document, warn in rows:
            with self.subTest(label):
                result = va.validate_axis(document)
                self.assertEqual(result.errors, [])
                if warn is None:
                    self.assertEqual(result.warnings, [])
                else:
                    self.assertTrue(any(warn in w for w in result.warnings), result.warnings)

    def test_rejected_or_flagged_documents(self):
        def no_version(axis):
            del axis["schema_version"]
            return axis

        def no_updated_at(axis):
            del axis["updated_at"]
            return axis

        rows = [
            ("ルートがオブジェクトでない", lambda: [], "errors", "(root)"),
            ("3.0 の profile.json", _valid_v3_profile, "errors", "axis.json"),
            ("schema_version の欠落", lambda: no_version(_valid_axis()), "errors", "schema_version"),
            ("axis の版として未知（9.9）", lambda: {**_valid_axis(), "schema_version": "9.9"}, "warnings", "既知のバージョン"),
            ("1.1 の axis は移行推奨の WARN", lambda: {**_valid_axis(), "schema_version": "1.1"}, "warnings", "2.0 への移行"),
            ("updated_at の欠落", lambda: no_updated_at(_valid_axis()), "warnings", "updated_at"),
        ]
        for label, build, bucket, expected in rows:
            with self.subTest(label):
                result = va.validate_axis(build())
                self.assertTrue(any(expected in m for m in getattr(result, bucket)), getattr(result, bucket))

    def test_bundled_examples(self):
        axis = vp.load_profile(os.path.join(_ASSETS, "axis_example.json"))
        result = va.validate_axis(axis)
        self.assertEqual((result.errors, result.warnings), ([], []))

        # 2つの記入例を重ねた 2.0 の profile.json は、両方の検証で全体として PASS する
        merged = {
            **vp.load_profile(os.path.join(_ASSETS, "profile_example.json")),
            **axis,
            "schema_version": "2.0",
        }
        for validate in (vp.validate, va.validate_axis):
            with self.subTest(validate.__module__):
                result = validate(merged)
                self.assertEqual((result.errors, result.warnings), ([], []))


class MainTest(unittest.TestCase):
    def _run(self, document, *flags) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "axis.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(document, f, ensure_ascii=False)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = va.main([path, *flags])
        return code, out.getvalue()

    def test_exit_codes_and_json_keys(self):
        self.assertEqual(self._run(_valid_axis())[0], 0)
        code, out = self._run(_valid_v3_profile(), "--json")
        self.assertEqual(code, 1)
        data = json.loads(out)
        self.assertEqual(data["status"], "FAIL")
        self.assertEqual(
            sorted(data), ["error_count", "errors", "status", "warning_count", "warnings"]
        )


if __name__ == "__main__":
    unittest.main()
