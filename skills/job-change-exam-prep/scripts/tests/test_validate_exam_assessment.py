"""validate_exam_assessment.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_exam_assessment
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_exam_assessment as ve  # noqa: E402


def _valid_document() -> dict:
    """ERROR 0件・WARN 0件になる調査結果を返す。"""
    return {
        "company": "架空クラウドワークス株式会社",
        "assessments": [
            {
                "type": "SPI3",
                "stage": "書類選考通過後・一次面接前",
                "evidence": [
                    {
                        "source_url": "https://example.com/careers/process",
                        "grade": "A",
                        "quote": "一次面接の前に SPI3（テストセンター）の受検をご案内します。",
                    },
                    {
                        "source_url": "https://example.com/taikenki/1024",
                        "grade": "C",
                        "quote": "書類通過の直後にテストセンターの予約案内が届いた。",
                    },
                ],
                "confidence": "確定",
                "format_notes": "テストセンター方式。言語・非言語と性格検査で構成される。",
                "prep_recommendations": ["非言語を反復練習する"],
            }
        ],
        "open_questions": ["性格検査が同一日程かどうかは確認できていない。"],
    }


def _a(document: dict) -> dict:
    return document["assessments"][0]


def _no_assessments(d):
    d["assessments"] = []


def _no_assessments_no_questions(d):
    d["assessments"] = []
    d["open_questions"] = []


def _confirmed_without_a(d):
    _a(d)["evidence"][0]["grade"] = "C"


def _estimated_single(d):
    _a(d)["confidence"] = "推定"
    _a(d)["evidence"] = [_a(d)["evidence"][1]]


class ValidateTest(unittest.TestCase):
    def test_valid_document_has_no_error_and_no_warning(self):
        result = ve.validate(_valid_document())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_bundled_example_passes(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        document = ve.load_assessment(os.path.join(base, "assets", "exam_assessment_example.json"))
        result = ve.validate(document)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_error_rules(self):
        rows = [
            ("ルートが配列", None, "ルート要素"),
            ("company 欠落（必須文字列）", lambda d: d.pop("company"), "company"),
            ("assessments が配列でない", lambda d: d.__setitem__("assessments", {}), "assessments"),
            ("assessments 空かつ open_questions 空", _no_assessments_no_questions, "未特定の事情"),
            ("open_questions の空要素（文字列リスト）", lambda d: d.__setitem__("open_questions", [""]), "open_questions[0]"),
            ("要素がオブジェクトでない", lambda d: d.__setitem__("assessments", ["SPI3"]), "assessments[0]"),
            ("evidence 空", lambda d: _a(d).__setitem__("evidence", []), "出典のない断定"),
            ("source_url が http でない", lambda d: _a(d)["evidence"][0].__setitem__("source_url", "採用ページ"), ".source_url"),
            ("grade が語彙外", lambda d: _a(d)["evidence"][0].__setitem__("grade", "S"), ".grade"),
            ("confidence が語彙外", lambda d: _a(d).__setitem__("confidence", "たぶん"), ".confidence"),
            ("確定にレベルAが無い", _confirmed_without_a, "レベル A の根拠"),
        ]
        for label, mutate, expected in rows:
            with self.subTest(label):
                document = _valid_document()
                if mutate is None:
                    result = ve.validate([])
                else:
                    mutate(document)
                    result = ve.validate(document)
                self.assertFalse(result.ok)
                self.assertTrue(any(expected in e for e in result.errors), result.errors)

    def test_warn_rules(self):
        rows = [
            ("assessments 空（open_questions あり）", _no_assessments, "特定できていない"),
            ("カタログ外の type", lambda d: _a(d).__setitem__("type", "架空検査ABC"), "assessment-catalog.md"),
            ("stage 欠落", lambda d: _a(d).pop("stage"), ".stage"),
            ("推定で根拠1件", _estimated_single, "根拠が1件のみ"),
            ("prep_recommendations 空", lambda d: _a(d).__setitem__("prep_recommendations", []), ".prep_recommendations"),
        ]
        for label, mutate, expected in rows:
            with self.subTest(label):
                document = _valid_document()
                mutate(document)
                result = ve.validate(document)
                self.assertEqual(result.errors, [])
                self.assertTrue(any(expected in w for w in result.warnings), result.warnings)


class MainTest(unittest.TestCase):
    def _run(self, content: str, *extra: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "exam_assessment.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = ve.main([path, *extra])
        return code, buffer.getvalue()

    def test_exit_codes(self):
        invalid = _valid_document()
        del invalid["company"]
        rows = [
            ("valid", json.dumps(_valid_document(), ensure_ascii=False), 0, "PASS"),
            ("invalid", json.dumps(invalid, ensure_ascii=False), 1, "FAIL"),
            ("broken json", "{", 1, "読み込めない"),
        ]
        for label, content, expected_code, expected_text in rows:
            with self.subTest(label):
                code, output = self._run(content)
                self.assertEqual(code, expected_code)
                self.assertIn(expected_text, output)

    def test_json_output_keys(self):
        _, output = self._run(json.dumps(_valid_document(), ensure_ascii=False), "--json")
        self.assertEqual(
            set(json.loads(output)),
            {"status", "error_count", "warning_count", "errors", "warnings"},
        )


if __name__ == "__main__":
    unittest.main()
