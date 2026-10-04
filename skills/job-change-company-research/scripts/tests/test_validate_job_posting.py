"""validate_job_posting.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_job_posting
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


def _v11_posting() -> dict:
    """schema_version 1.1 で scope_of_change を3項目とも埋めた job_posting.json を返す。"""
    p = _valid_posting()
    p["schema_version"] = "1.1"
    p["scope_of_change"] = {
        "duties": {
            "stated": True,
            "unlimited": False,
            "quote": "変更の範囲: バックエンド開発およびこれに関連する業務",
        },
        "work_location": {
            "stated": True,
            "unlimited": True,
            "quote": "変更の範囲: 会社の定める場所",
        },
        "contract_renewal_cap": {
            "stated": False,
            "unlimited": False,
            "quote": "無期雇用のため対象外",
        },
    }
    return p


_DEL = object()


def _set(path: list, value=_DEL):
    """path 末端に value を代入する変異を返す（value 省略で削除）。"""

    def mutate(p: dict) -> None:
        node = p
        for key in path[:-1]:
            node = node[key]
        if value is _DEL:
            del node[path[-1]]
        else:
            node[path[-1]] = value

    return mutate


def _all_scope_null(p: dict) -> None:
    for key in vjp.SCOPE_KEYS:
        p["scope_of_change"][key] = None


class ValidateTest(unittest.TestCase):
    def test_valid_postings_have_no_errors_or_warnings(self):
        """各スキーマ版と取込の入口ごとの正常形。"""
        text = _valid_posting()
        text.update(source_type="text", source_url=None)
        rows = [
            ("1.0 完全形", _valid_posting()),
            ("1.1 scope_of_change 3項目あり", _v11_posting()),
            ("最小形", _minimal_posting()),
            ("dialogue は source_url なし", _dialogue_posting()),
            ("text は source_url が null", text),
        ]
        for label, p in rows:
            with self.subTest(label):
                snapshot = copy.deepcopy(p)
                result = vjp.validate(p)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])
                self.assertEqual(p, snapshot)

    def test_bundled_example_passes(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        document = vjp.load_posting(os.path.join(base, "assets", "job_posting_example.json"))
        result = vjp.validate(document)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_error_rules(self):
        scope = ["scope_of_change"]
        rows = [
            ("ルートがオブジェクトでない", None, None, "(root)"),
            ("必須項目 title が無い", _valid_posting, _set(["title"]), "title"),
            ("source_type が列挙外", _valid_posting, _set(["source_type"], "scraped"), "source_type"),
            ("source_type=url で source_url が http でない", _valid_posting, _set(["source_url"], "recruit.example.co.jp/jobs/1"), "source_url"),
            ("fetched_at の形式違い", _valid_posting, _set(["fetched_at"], "2026/07/17"), "fetched_at"),
            ("fetched_at が実在しない日付", _valid_posting, _set(["fetched_at"], "2026-13-40"), "fetched_at"),
            ("metrics がオブジェクトでない", _valid_posting, _set(["metrics"], "125日"), "metrics"),
            ("metric の value が bool", _valid_posting, _set(["metrics", "monthly_overtime_h", "value"], True), "metrics.monthly_overtime_h.value"),
            ("metric の quote が空", _valid_posting, _set(["metrics", "paid_leave_rate", "quote"], ""), "metrics.paid_leave_rate.quote"),
            ("metric がオブジェクトでも null でもない", _valid_posting, _set(["metrics", "annual_holidays"], 125), "metrics.annual_holidays"),
            ("scope_of_change がオブジェクトでない", _v11_posting, _set(scope, ["会社の定める場所"]), "scope_of_change"),
            ("scope の項目がオブジェクトでも null でもない", _v11_posting, _set(scope + ["duties"], "会社の定める業務"), "scope_of_change.duties"),
            ("scope の stated が真偽値でない", _v11_posting, _set(scope + ["duties", "stated"], "true"), "scope_of_change.duties.stated"),
            ("stated が真で quote が空", _v11_posting, _set(scope + ["duties", "quote"], ""), "scope_of_change.duties.quote"),
            ("stated が偽で quote が文字列でない", _v11_posting, _set(scope + ["contract_renewal_cap", "quote"], 3), "scope_of_change.contract_renewal_cap.quote"),
            ("salary がオブジェクトでない", _valid_posting, _set(["salary"], "年収600万円"), "salary"),
            ("selection_process が配列でない", _valid_posting, _set(["selection_process"], "書類選考のみ"), "selection_process"),
            ("benefits の name が無い", _valid_posting, _set(["benefits"], [{"quote": "各種手当あり"}]), "benefits[0].name"),
        ]
        for label, build, mutate, expected in rows:
            with self.subTest(label):
                if build is None:
                    result = vjp.validate(["not", "object"])
                else:
                    p = build()
                    mutate(p)
                    result = vjp.validate(p)
                self.assertFalse(result.ok)
                self.assertTrue(any(expected in e for e in result.errors), result.errors)

    def test_warn_rules(self):
        rows = [
            ("未知の schema_version", _valid_posting, _set(["schema_version"], "2.0"), "schema_version"),
            ("1.1 で scope_of_change が無い", _valid_posting, _set(["schema_version"], "1.1"), "scope_of_change"),
            ("1.0 以外の後続版でも scope を検査する", _valid_posting, _set(["schema_version"], "1.2"), "scope_of_change"),
            ("scope_of_change が3項目とも null", _v11_posting, _all_scope_null, "scope_of_change"),
        ]
        for label, build, mutate, expected in rows:
            with self.subTest(label):
                p = build()
                mutate(p)
                result = vjp.validate(p)
                self.assertTrue(result.ok, result.errors)
                self.assertTrue(any(expected in w for w in result.warnings), result.warnings)

    def test_accepted_variants_stay_clean(self):
        """ERROR にも WARN にもならない許容形。"""
        scope = ["scope_of_change"]

        def one_filled(p: dict) -> None:
            _all_scope_null(p)
            p["scope_of_change"]["duties"] = _v11_posting()["scope_of_change"]["duties"]

        rows = [
            ("1.0 は壊れた scope_of_change を検査しない", _valid_posting, _set(scope, "会社の定める場所")),
            ("scope は1項目だけ埋まっていれば足りる", _v11_posting, one_filled),
            ("stated が偽なら quote は空でよい", _v11_posting, _set(scope + ["contract_renewal_cap", "quote"], "")),
            ("metric が null", _valid_posting, _set(["metrics", "annual_holidays"], None)),
        ]
        for label, build, mutate in rows:
            with self.subTest(label):
                p = build()
                mutate(p)
                result = vjp.validate(p)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])


class CliTest(unittest.TestCase):
    def _write(self, text: str, encoding: str = "utf-8") -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(text)
        self.addCleanup(os.remove, path)
        return path

    def test_exit_codes_and_json_keys(self):
        invalid = _valid_posting()
        del invalid["company_name"]
        rows = [
            ("正常", json.dumps(_valid_posting(), ensure_ascii=False), "utf-8", 0),
            ("BOM 付きの正常", json.dumps(_valid_posting(), ensure_ascii=False), "utf-8-sig", 0),
            ("ERROR あり", json.dumps(invalid, ensure_ascii=False), "utf-8", 1),
            ("壊れた JSON", "{ not valid json ", "utf-8", 1),
        ]
        for label, text, encoding, code in rows:
            with self.subTest(label):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(vjp.main([self._write(text, encoding)]), code)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            vjp.main([self._write(json.dumps(_valid_posting())), "--json"])
        self.assertEqual(
            set(json.loads(buf.getvalue())),
            {"status", "error_count", "warning_count", "errors", "warnings"},
        )


if __name__ == "__main__":
    unittest.main()
