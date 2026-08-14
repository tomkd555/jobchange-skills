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


def _first_assessment(document: dict) -> dict:
    return document["assessments"][0]


class StructureTest(unittest.TestCase):
    def test_valid_document_has_no_error_and_no_warning(self):
        result = ve.validate(_valid_document())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])
        self.assertTrue(result.ok)

    def test_non_object_root_is_an_error(self):
        result = ve.validate([])
        self.assertFalse(result.ok)
        self.assertTrue(any("ルート要素" in e for e in result.errors))

    def test_missing_company_is_an_error(self):
        document = _valid_document()
        del document["company"]
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("company" in e for e in result.errors))

    def test_empty_company_is_an_error(self):
        document = _valid_document()
        document["company"] = "   "
        result = ve.validate(document)
        self.assertFalse(result.ok)

    def test_assessments_not_list_is_an_error(self):
        document = _valid_document()
        document["assessments"] = {}
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("assessments" in e for e in result.errors))

    def test_empty_assessments_with_open_questions_is_a_warning(self):
        document = _valid_document()
        document["assessments"] = []
        result = ve.validate(document)
        self.assertEqual(result.errors, [])
        self.assertTrue(any("特定できていない" in w for w in result.warnings))

    def test_empty_assessments_without_open_questions_is_an_error(self):
        document = _valid_document()
        document["assessments"] = []
        document["open_questions"] = []
        result = ve.validate(document)
        self.assertFalse(result.ok)

    def test_non_object_assessment_is_an_error(self):
        document = _valid_document()
        document["assessments"] = ["SPI3"]
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("assessments[0]" in e for e in result.errors))

    def test_open_questions_not_list_is_an_error(self):
        document = _valid_document()
        document["open_questions"] = "未確認の点はない"
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("open_questions" in e for e in result.errors))

    def test_non_string_open_question_is_an_error(self):
        document = _valid_document()
        document["open_questions"] = [""]
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("open_questions[0]" in e for e in result.errors))


class AssessmentFieldTest(unittest.TestCase):
    def test_missing_type_is_an_error(self):
        document = _valid_document()
        del _first_assessment(document)["type"]
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any(".type" in e for e in result.errors))

    def test_unknown_type_is_a_warning(self):
        document = _valid_document()
        _first_assessment(document)["type"] = "架空検査ABC"
        result = ve.validate(document)
        self.assertEqual(result.errors, [])
        self.assertTrue(any("assessment-catalog.md" in w for w in result.warnings))

    def test_missing_stage_is_a_warning(self):
        document = _valid_document()
        del _first_assessment(document)["stage"]
        result = ve.validate(document)
        self.assertEqual(result.errors, [])
        self.assertTrue(any(".stage" in w for w in result.warnings))

    def test_missing_format_notes_is_a_warning(self):
        document = _valid_document()
        _first_assessment(document)["format_notes"] = ""
        result = ve.validate(document)
        self.assertEqual(result.errors, [])
        self.assertTrue(any(".format_notes" in w for w in result.warnings))

    def test_prep_recommendations_not_list_is_an_error(self):
        document = _valid_document()
        _first_assessment(document)["prep_recommendations"] = "非言語を反復練習する"
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any(".prep_recommendations" in e for e in result.errors))

    def test_empty_prep_recommendation_item_is_an_error(self):
        document = _valid_document()
        _first_assessment(document)["prep_recommendations"] = [""]
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any(".prep_recommendations[0]" in e for e in result.errors))

    def test_empty_prep_recommendations_is_a_warning(self):
        document = _valid_document()
        _first_assessment(document)["prep_recommendations"] = []
        result = ve.validate(document)
        self.assertEqual(result.errors, [])
        self.assertTrue(any(".prep_recommendations" in w for w in result.warnings))


class EvidenceTest(unittest.TestCase):
    def test_evidence_not_list_is_an_error(self):
        document = _valid_document()
        _first_assessment(document)["evidence"] = {}
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any(".evidence" in e for e in result.errors))

    def test_empty_evidence_is_an_error(self):
        document = _valid_document()
        _first_assessment(document)["evidence"] = []
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("出典のない断定" in e for e in result.errors))

    def test_non_object_evidence_is_an_error(self):
        document = _valid_document()
        _first_assessment(document)["evidence"] = ["https://example.com/careers/process"]
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any(".evidence[0]" in e for e in result.errors))

    def test_missing_source_url_is_an_error(self):
        document = _valid_document()
        del _first_assessment(document)["evidence"][0]["source_url"]
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any(".source_url" in e for e in result.errors))

    def test_non_http_source_url_is_an_error(self):
        document = _valid_document()
        _first_assessment(document)["evidence"][0]["source_url"] = "採用ページ"
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any(".source_url" in e for e in result.errors))

    def test_unknown_grade_is_an_error(self):
        document = _valid_document()
        _first_assessment(document)["evidence"][0]["grade"] = "S"
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any(".grade" in e for e in result.errors))

    def test_empty_quote_is_an_error(self):
        document = _valid_document()
        _first_assessment(document)["evidence"][0]["quote"] = ""
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any(".quote" in e for e in result.errors))


class ConfidenceTest(unittest.TestCase):
    def test_unknown_confidence_is_an_error(self):
        document = _valid_document()
        _first_assessment(document)["confidence"] = "たぶん"
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any(".confidence" in e for e in result.errors))

    def test_missing_confidence_is_an_error(self):
        document = _valid_document()
        del _first_assessment(document)["confidence"]
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any(".confidence" in e for e in result.errors))

    def test_confirmed_without_grade_a_is_an_error(self):
        document = _valid_document()
        _first_assessment(document)["evidence"][0]["grade"] = "C"
        result = ve.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("レベル A の根拠" in e for e in result.errors))

    def test_confirmed_with_grade_a_passes(self):
        document = _valid_document()
        _first_assessment(document)["evidence"][1]["grade"] = "D"
        result = ve.validate(document)
        self.assertEqual(result.errors, [])

    def test_estimated_with_single_evidence_is_a_warning(self):
        document = _valid_document()
        assessment = _first_assessment(document)
        assessment["confidence"] = "推定"
        assessment["evidence"] = [
            {
                "source_url": "https://example.com/taikenki/2087",
                "grade": "C",
                "quote": "一次面接のあとに文章と図形の検査を受けた。",
            }
        ]
        result = ve.validate(document)
        self.assertEqual(result.errors, [])
        self.assertTrue(any("根拠が1件のみ" in w for w in result.warnings))

    def test_estimated_with_two_evidence_has_no_warning(self):
        document = _valid_document()
        assessment = _first_assessment(document)
        assessment["confidence"] = "推定"
        assessment["evidence"][0]["grade"] = "C"
        result = ve.validate(document)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


class MainTest(unittest.TestCase):
    def _run(self, argv: list[str]) -> tuple[int, str]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = ve.main(argv)
        return code, buffer.getvalue()

    def test_valid_file_returns_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "exam_assessment.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(_valid_document(), f, ensure_ascii=False)
            code, output = self._run([path])
        self.assertEqual(code, 0)
        self.assertIn("PASS", output)

    def test_broken_json_returns_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "exam_assessment.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{")
            code, output = self._run([path])
        self.assertEqual(code, 1)
        self.assertIn("読み込めない", output)

    def test_invalid_document_returns_1_with_json_output(self):
        document = _valid_document()
        del document["company"]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "exam_assessment.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(document, f, ensure_ascii=False)
            code, output = self._run([path, "--json"])
        self.assertEqual(code, 1)
        payload = json.loads(output)
        self.assertEqual(payload["status"], "FAIL")
        self.assertEqual(payload["error_count"], len(payload["errors"]))


class ExampleAssetTest(unittest.TestCase):
    def test_bundled_example_passes(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        document = ve.load_assessment(os.path.join(base, "assets", "exam_assessment_example.json"))
        result = ve.validate(document)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


if __name__ == "__main__":
    unittest.main()
