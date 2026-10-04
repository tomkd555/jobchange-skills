"""validate_company_research.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_company_research
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


def _lowgrade(r: dict, confidence: str) -> None:
    r["claims"][6] = _claim("C007", "reputation", "C", confidence)


def _mixed_grade_high(r: dict) -> None:
    claim = _claim("C007", "reputation", "A", "high")
    claim["evidence"].append({**claim["evidence"][0], "grade": "C"})
    r["claims"][6] = claim


_DEL = object()


def _set(path: list, value=_DEL) -> "callable":
    """path 末端に value を代入する変異を返す（value 省略で削除）。"""

    def mutate(r: dict) -> None:
        node = r
        for key in path[:-1]:
            node = node[key]
        if value is _DEL:
            del node[path[-1]]
        else:
            node[path[-1]] = value

    return mutate


def _without_topic(topic: str) -> "callable":
    def mutate(r: dict) -> None:
        r["claims"] = [c for c in r["claims"] if c["topic"] != topic]

    return mutate


class ValidateTest(unittest.TestCase):
    def test_valid_research_has_no_errors_or_warnings(self):
        r = _valid_research()
        snapshot = copy.deepcopy(r)
        result = vcr.validate(r)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])
        self.assertEqual(r, snapshot)  # 入力を書き換えない

    def test_bundled_example_passes(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        document = vcr.load_research(os.path.join(base, "assets", "company_research_example.json"))
        result = vcr.validate(document)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_error_rules(self):
        rows = [
            ("ルートがオブジェクトでない", None, "(root)"),
            ("company がオブジェクトでない", _set(["company"], "文字列"), "company"),
            ("company.name が無い", _set(["company", "name"]), "company.name"),
            ("claims が空", _set(["claims"], []), "claims"),
            ("claim の statement が空白", _set(["claims", 0, "statement"], "  "), "statement"),
            ("claim の topic が列挙外", _set(["claims", 0, "topic"], "culture"), "topic"),
            ("evidence が空", _set(["claims", 0, "evidence"], []), "evidence"),
            ("evidence の source_url が http でない", _set(["claims", 0, "evidence", 0, "source_url"], "www.example.com"), "source_url"),
            ("必須トピック欠落", _without_topic("financials"), "financials"),
            ("C・D のみの根拠に confidence=high", lambda r: _lowgrade(r, "high"), "C007"),
            ("company_metrics が無い", _set(["company_metrics"]), "company_metrics"),
            ("company_metrics がオブジェクトでない", _set(["company_metrics"], "年間休日125日"), "company_metrics"),
            ("company_metrics が定量候補軸以外のキー", _set(["company_metrics", "avg_tenure"], _metric(5.8, "年")), "company_metrics.avg_tenure"),
            ("company_metrics の項目がオブジェクトでない", _set(["company_metrics", "annual_holidays"], 125), "company_metrics.annual_holidays"),
            ("company_metrics の value が bool", _set(["company_metrics", "monthly_overtime", "value"], True), "company_metrics.monthly_overtime.value"),
            ("company_metrics の unit が軸の単位と違う", _set(["company_metrics", "compensation_level", "unit"], "万円"), "company_metrics.compensation_level.unit"),
            ("非 null の value に source_url が無い", _set(["company_metrics", "paid_leave_rate", "source_url"]), "company_metrics.paid_leave_rate.source_url"),
        ]
        for label, mutate, expected in rows:
            with self.subTest(label):
                r = _valid_research()
                result = vcr.validate(["not", "object"] if mutate is None else (mutate(r), r)[1])
                self.assertFalse(result.ok)
                self.assertTrue(any(expected in e for e in result.errors), result.errors)

    def test_warn_rules(self):
        rows = [
            ("research_date が無い", _set(["research_date"]), "research_date"),
            ("トピックの claim がすべて C・D", lambda r: _lowgrade(r, "medium"), "reputation"),
            ("selection_process が0件", _without_topic("selection_process"), "selection_process"),
            ("非 null の value に as_of が無い", _set(["company_metrics", "turnover_rate", "as_of"]), "company_metrics.turnover_rate.as_of"),
            ("実測値が1件も無い", _set(["company_metrics"], _all_null_company_metrics()), "company_metrics"),
        ]
        for label, mutate, expected in rows:
            with self.subTest(label):
                r = _valid_research()
                mutate(r)
                result = vcr.validate(r)
                self.assertTrue(result.ok, result.errors)
                self.assertTrue(any(expected in w for w in result.warnings), result.warnings)

    def test_accepted_variants_stay_clean(self):
        """ERROR にも WARN にもならない許容形。"""
        rows = [
            ("A と C を併記した claim の confidence=high", _mixed_grade_high),
            ("一部の軸が value=null", _set(["company_metrics", "annual_holidays"], _null_metric("日"))),
            ("補助指標のキー", _set(["company_metrics", "avg_paid_leave_days_taken"], _metric(12.4, "日"))),
        ]
        for label, mutate in rows:
            with self.subTest(label):
                r = _valid_research()
                mutate(r)
                result = vcr.validate(r)
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
        invalid = _valid_research()
        del invalid["company"]["name"]
        rows = [
            ("正常", json.dumps(_valid_research(), ensure_ascii=False), "utf-8", 0),
            ("BOM 付きの正常", json.dumps(_valid_research(), ensure_ascii=False), "utf-8-sig", 0),
            ("ERROR あり", json.dumps(invalid, ensure_ascii=False), "utf-8", 1),
            ("壊れた JSON", "{ not valid json ", "utf-8", 1),
        ]
        for label, text, encoding, code in rows:
            with self.subTest(label):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(vcr.main([self._write(text, encoding)]), code)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            vcr.main([self._write(json.dumps(_valid_research())), "--json"])
        self.assertEqual(
            set(json.loads(buf.getvalue())),
            {"status", "error_count", "warning_count", "errors", "warnings"},
        )


if __name__ == "__main__":
    unittest.main()
