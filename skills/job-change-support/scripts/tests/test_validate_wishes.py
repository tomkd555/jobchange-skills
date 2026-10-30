"""validate_wishes.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_wishes
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

import validate_wishes as vw  # noqa: E402


def _valid() -> dict:
    """ERROR 0件・WARN 0件になる完全な wishes を返す。"""
    return {
        "schema_version": "1.0",
        "updated": "2026-11-01",
        "conditions": [
            {
                "id": "c001", "kind": "salary_min", "field_id": "salary_min", "operator": ">=",
                "text": "年収 600 万円以上", "value": 6000000, "unit": "円", "level": "must",
                "source": "user", "how_to_judge": None, "created": "2026-10-25",
                "updated": "2026-11-01", "active": True,
            },
            {
                "id": "c002", "kind": "remote", "field_id": "remote_policy", "operator": "in",
                "text": "リモート中心", "value": ["full_remote", "hybrid"], "unit": None, "level": "must",
                "source": "user", "how_to_judge": None, "created": "2026-10-25",
                "updated": "2026-10-25", "active": True,
            },
            {
                "id": "c003", "kind": "value", "field_id": "custom", "operator": None,
                "text": "知的な挑戦", "value": None, "unit": None, "level": "want",
                "source": "intellectual_challenge", "how_to_judge": "新しい技術の導入を含むか",
                "created": "2026-11-01", "updated": "2026-11-01", "active": True,
            },
        ],
        "history": [
            {"date": "2026-11-01", "condition_id": "c001", "field": "value",
             "before": 5500000, "after": 6000000, "reason": "求人の下限がそろって 600 万円を超えていた"},
        ],
        "used_in": ["20261115-infra-2sha"],
    }


def _mutated(mutate) -> vw.ValidationResult:
    doc = _valid()
    mutate(doc)
    return vw.validate(doc)


def _cond(doc: dict, index: int = 0) -> dict:
    return doc["conditions"][index]


class ValidFixtureTest(unittest.TestCase):
    def test_valid_no_findings(self) -> None:
        result = vw.validate(_valid())
        self.assertEqual((result.errors, result.warnings), ([], []))

    def test_example_asset_passes(self) -> None:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            "assets", "wishes_example.json")
        result = vw.validate(vw.load_json(path))
        self.assertEqual(result.errors, [])


class ErrorRuleTest(unittest.TestCase):
    def test_each_error_rule(self) -> None:
        def drop(key):
            return lambda d: d.pop(key)

        def cond_set(index, **kw):
            return lambda d: _cond(d, index).update(kw)

        def cond_drop(key):
            return lambda d: _cond(d).pop(key)

        rows = [
            ("ルートが配列", None, "ルート要素"),
            ("updated 欠落", drop("updated"), "updated"),
            ("conditions が配列でない", lambda d: d.update(conditions={}), "conditions は配列"),
            ("history 欠落", drop("history"), "history は配列"),
            ("used_in 欠落", drop("used_in"), "used_in は配列"),
            ("条件の必須欠落", cond_drop("level"), "level は必須"),
            ("id の形", cond_set(0, id="x1"), "id は c と 3 桁"),
            ("id の重複", cond_set(1, id="c001"), "重複"),
            ("kind が列挙外", cond_set(0, kind="nope"), "kind は"),
            ("level が列挙外", cond_set(0, level="maybe"), "level は"),
            ("operator が列挙外", cond_set(0, operator="~"), "operator は"),
            ("field_id が辞書外", cond_set(0, field_id="nope"), "辞書にない"),
            ("operator が null で value あり", cond_set(0, operator=None), "operator が null"),
            ("value が null で operator あり", cond_set(0, value=None), "value が null"),
            ("整数項目に文字列", cond_set(0, value="600"), "整数"),
            ("列挙外の値", cond_set(1, value=["full_remote", "nowhere"]), "のいずれか"),
            ("unit 不一致", cond_set(0, unit="万円"), "unit は"),
            ("custom で how_to_judge が空", cond_set(2, how_to_judge=""), "how_to_judge"),
            ("created が実在しない日付", cond_set(0, created="2026-02-30"), "created は"),
            ("updated が created より前", cond_set(0, created="2026-12-01"), "created より前"),
            ("履歴の condition_id が未知", lambda d: d["history"][0].update(condition_id="c999"), "conditions にない"),
            ("履歴の reason が空", lambda d: d["history"][0].update(reason=" "), "reason"),
            ("used_in の形", lambda d: d.update(used_in=["infra"]), "意思決定 id"),
        ]
        for label, mutate, needle in rows:
            with self.subTest(label):
                if mutate is None:
                    result = vw.validate([])
                else:
                    result = _mutated(mutate)
                self.assertFalse(result.ok)
                self.assertTrue(any(needle in e for e in result.errors), result.errors)


class WarnRuleTest(unittest.TestCase):
    def test_each_warn_rule(self) -> None:
        rows = [
            ("未知のバージョン", lambda d: d.update(schema_version="9.9"), "schema_version"),
            ("conditions が空", lambda d: d.update(conditions=[], history=[]), "conditions が空"),
            ("必須条件が無効", lambda d: _cond(d).update(active=False), "無効になっている"),
            ("salary_min が無い", lambda d: _cond(d).update(active=False), "kind salary_min"),
            ("remote が無い", lambda d: d["conditions"].pop(1), "kind remote"),
        ]
        for label, mutate, needle in rows:
            with self.subTest(label):
                result = _mutated(mutate)
                self.assertTrue(result.ok, result.errors)
                self.assertTrue(any(needle in w for w in result.warnings), result.warnings)


class MainTest(unittest.TestCase):
    def _run(self, document: dict, *flags: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "wishes.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(document, f, ensure_ascii=False)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = vw.main([path, *flags])
        return code, buffer.getvalue()

    def _broken(self) -> dict:
        broken = copy.deepcopy(_valid())
        _cond(broken)["kind"] = "nope"
        return broken

    def test_valid_json_exit_0_status_pass(self) -> None:
        code, output = self._run(_valid(), "--json")
        payload = json.loads(output)
        self.assertEqual((code, payload["status"], payload["error_count"], payload["warning_count"]), (0, "PASS", 0, 0))

    def test_broken_json_exit_1_status_fail(self) -> None:
        code, output = self._run(self._broken(), "--json")
        self.assertEqual((code, json.loads(output)["status"]), (1, "FAIL"))

    def test_broken_text_exit_1_prints_fail(self) -> None:
        code, output = self._run(self._broken())
        self.assertEqual(code, 1)
        self.assertIn("検証結果: FAIL", output)

    def test_unreadable_file_fails(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = vw.main([os.path.join(tempfile.gettempdir(), "no-such-wishes.json")])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
