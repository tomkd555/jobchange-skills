"""validate_interview_intel.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_interview_intel
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_interview_intel as vii  # noqa: E402


def _valid_document() -> dict:
    """ERROR 0件・WARN 0件になる完全な interview_intel.json を返す。"""
    return {
        "schema_version": "1.0",
        "company": "架空クラウドワークス株式会社",
        "role_title": "バックエンドエンジニア",
        "researched_at": "2026-09-04",
        "reported_questions": [
            {
                "id": "RQ001",
                "question": "現職を離れようと考えた理由を教えてください",
                "kind": "reported",
                "category": "転職理由",
                "stage": "一次面接",
                "source_url": "https://example.com/reviews/kuraudo-works/1",
                "source_name": "転職会議",
                "grade": "C",
                "quote": "「現職を離れようと考えた理由を教えてください」と聞かれた",
                "accessed": "2026-09-04",
            },
            {
                "id": "RQ002",
                "question": "チーム内で意見が割れたとき、どのように合意形成しますか",
                "kind": "inferred",
                "category": "ビヘイビアラル",
                "stage": "最終面接",
                "source_url": "https://example.com/reviews/kuraudo-works/culture",
                "source_name": "転職会議の集計ページ",
                "grade": "C",
                "quote": "合議を重んじる文化だという回答が複数あった",
                "accessed": "2026-09-04",
            },
        ],
        "format_facts": [
            {
                "id": "FF001",
                "statement": "選考は書類選考、一次面接、二次面接、最終面接の4段階である。",
                "source_url": "https://example.com/careers/kuraudo-works",
                "source_name": "採用ページ",
                "grade": "A",
                "quote": "選考は書類選考、一次面接、二次面接、最終面接の4段階で進みます",
                "accessed": "2026-09-04",
            },
        ],
        "themes": [
            {
                "id": "TH001",
                "theme": "個人の貢献と組織の成果を切り分けて語れるかを重視する傾向がある。",
                "likely_probe": "「あなた自身が担った部分」を繰り返し確認してくると考えられる。",
                "source_url": "https://example.com/reviews/kuraudo-works/summary",
                "source_name": "転職会議の集計ページ",
                "grade": "C",
                "quote": "個人の貢献と組織の成果を分けて話せるかを聞かれたという回答が複数あった",
                "accessed": "2026-09-04",
                "count_note": "回答12件中5件",
            },
        ],
        "search_log": [
            {
                "query": "架空クラウドワークス 面接 質問",
                "source": "転職会議",
                "url": "https://example.com/reviews/kuraudo-works",
                "fetched_at": "2026-09-04",
                "hit_count": 12,
                "adopted_count": 3,
            },
        ],
        "coverage_notes": "口コミサイトでは一次・二次の質問例が多く見つかったが、最終面接の実例は見つからず推測で補った。",
        "open_questions": ["最終面接で実際に聞かれた質問の実例が見つかっていない。"],
    }


class ValidatePassTest(unittest.TestCase):
    def test_full_document_passes_with_no_warnings(self):
        result = vii.validate(_valid_document())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


class RootErrorTest(unittest.TestCase):
    def test_non_object_root_is_an_error(self):
        result = vii.validate(["reported_questions"])
        self.assertFalse(result.ok)
        self.assertTrue(any("ルート要素" in e for e in result.errors))

    def test_missing_schema_version_is_an_error(self):
        document = _valid_document()
        del document["schema_version"]
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("schema_version は必須" in e for e in result.errors))

    def test_empty_schema_version_is_an_error(self):
        document = _valid_document()
        document["schema_version"] = "  "
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("schema_version は必須" in e for e in result.errors))

    def test_unknown_schema_version_is_a_warning(self):
        document = _valid_document()
        document["schema_version"] = "0.9"
        result = vii.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("既知のバージョン" in w for w in result.warnings))

    def test_missing_company_is_an_error(self):
        document = _valid_document()
        del document["company"]
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("company は必須" in e for e in result.errors))

    def test_empty_company_is_an_error(self):
        document = _valid_document()
        document["company"] = ""
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("company は必須" in e for e in result.errors))

    def test_missing_researched_at_is_an_error(self):
        document = _valid_document()
        del document["researched_at"]
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("researched_at は必須" in e for e in result.errors))

    def test_malformed_researched_at_is_an_error(self):
        document = _valid_document()
        document["researched_at"] = "2026/09/04"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("researched_at" in e and "YYYY-MM-DD" in e for e in result.errors))

    def test_nonexistent_researched_at_date_is_an_error(self):
        document = _valid_document()
        document["researched_at"] = "2026-02-30"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("researched_at" in e for e in result.errors))

    def test_null_role_title_passes(self):
        document = _valid_document()
        document["role_title"] = None
        result = vii.validate(document)
        self.assertEqual(result.errors, [])

    def test_missing_role_title_passes(self):
        document = _valid_document()
        del document["role_title"]
        result = vii.validate(document)
        self.assertEqual(result.errors, [])

    def test_non_string_role_title_is_an_error(self):
        document = _valid_document()
        document["role_title"] = 123
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("role_title" in e for e in result.errors))


class ArrayShapeTest(unittest.TestCase):
    def test_missing_reported_questions_is_an_error(self):
        document = _valid_document()
        del document["reported_questions"]
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("reported_questions は配列" in e for e in result.errors))

    def test_non_list_format_facts_is_an_error(self):
        document = _valid_document()
        document["format_facts"] = {}
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("format_facts は配列" in e for e in result.errors))

    def test_non_object_entry_is_an_error(self):
        document = _valid_document()
        document["themes"][0] = "TH001"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("オブジェクトでなければならない" in e for e in result.errors))

    def test_missing_themes_is_an_error(self):
        document = _valid_document()
        del document["themes"]
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("themes は配列" in e for e in result.errors))


class EmptyArrayWarningTest(unittest.TestCase):
    def test_empty_reported_questions_is_a_warning(self):
        document = _valid_document()
        document["reported_questions"] = []
        result = vii.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("reported_questions が空" in w for w in result.warnings))

    def test_empty_format_facts_is_a_warning(self):
        document = _valid_document()
        document["format_facts"] = []
        result = vii.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("format_facts が空" in w for w in result.warnings))

    def test_empty_themes_is_a_warning(self):
        document = _valid_document()
        document["themes"] = []
        result = vii.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("themes が空" in w for w in result.warnings))

    def test_all_three_empty_with_open_questions_is_not_an_error(self):
        document = _valid_document()
        document["reported_questions"] = []
        document["format_facts"] = []
        document["themes"] = []
        result = vii.validate(document)
        self.assertEqual(result.errors, [])

    def test_all_three_empty_without_open_questions_is_an_error(self):
        document = _valid_document()
        document["reported_questions"] = []
        document["format_facts"] = []
        document["themes"] = []
        document["open_questions"] = []
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("何も語っていない" in e for e in result.errors))

    def test_all_three_empty_with_missing_open_questions_is_an_error(self):
        document = _valid_document()
        document["reported_questions"] = []
        document["format_facts"] = []
        document["themes"] = []
        del document["open_questions"]
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("何も語っていない" in e for e in result.errors))

    def test_shape_error_with_two_empty_arrays_is_a_single_error(self):
        # reported_questions が配列でない（形状エラー）場合、None を空扱いに数えて
        # 「何も語っていない」を重ねて出してはいけない。ERROR は形状エラー1件だけになる。
        document = _valid_document()
        document["reported_questions"] = {}
        document["format_facts"] = []
        document["themes"] = []
        document["open_questions"] = []
        result = vii.validate(document)
        self.assertEqual(len(result.errors), 1)
        self.assertTrue(any("reported_questions は配列" in e for e in result.errors))


class ReportedQuestionTest(unittest.TestCase):
    def test_malformed_id_is_an_error(self):
        document = _valid_document()
        document["reported_questions"][0]["id"] = "Q001"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("RQ001 形式" in e for e in result.errors))

    def test_missing_id_is_an_error(self):
        document = _valid_document()
        del document["reported_questions"][0]["id"]
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("reported_questions[0].id" in e for e in result.errors))

    def test_duplicate_id_is_an_error(self):
        document = _valid_document()
        document["reported_questions"][1]["id"] = "RQ001"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("重複" in e for e in result.errors))

    def test_four_digit_id_passes(self):
        document = _valid_document()
        document["reported_questions"][0]["id"] = "RQ1000"
        result = vii.validate(document)
        self.assertEqual(result.errors, [])

    def test_empty_question_is_an_error(self):
        document = _valid_document()
        document["reported_questions"][0]["question"] = ""
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("question は必須" in e for e in result.errors))

    def test_invalid_kind_is_an_error(self):
        document = _valid_document()
        document["reported_questions"][0]["kind"] = "guessed"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("kind は" in e for e in result.errors))

    def test_source_url_not_http_is_an_error(self):
        document = _valid_document()
        document["reported_questions"][0]["source_url"] = "example.com/foo"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("source_url" in e for e in result.errors))

    def test_invalid_grade_is_an_error(self):
        document = _valid_document()
        document["reported_questions"][0]["grade"] = "E"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("grade は" in e for e in result.errors))

    def test_grade_d_is_a_warning(self):
        document = _valid_document()
        document["reported_questions"][0]["grade"] = "D"
        result = vii.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("grade が D" in w for w in result.warnings))

    def test_empty_quote_is_an_error(self):
        document = _valid_document()
        document["reported_questions"][0]["quote"] = ""
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("quote は必須" in e for e in result.errors))

    def test_missing_accessed_is_a_warning(self):
        document = _valid_document()
        del document["reported_questions"][0]["accessed"]
        result = vii.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("accessed が未記載" in w for w in result.warnings))

    def test_null_accessed_is_a_warning(self):
        document = _valid_document()
        document["reported_questions"][0]["accessed"] = None
        result = vii.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("accessed が未記載" in w for w in result.warnings))

    def test_malformed_accessed_is_an_error(self):
        document = _valid_document()
        document["reported_questions"][0]["accessed"] = "2026/09/04"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("accessed は実在する" in e for e in result.errors))

    def test_reported_kind_quote_overlap_missing_is_a_warning(self):
        document = _valid_document()
        document["reported_questions"][0]["quote"] = "まったく無関係な引用文である"
        result = vii.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("重なっているべきである" in w for w in result.warnings))

    def test_inferred_kind_quote_overlap_not_checked(self):
        document = _valid_document()
        # kind が inferred の RQ002 は question/quote が重ならなくても WARN しない。
        document["reported_questions"][1]["quote"] = "まったく無関係な引用文である"
        result = vii.validate(document)
        self.assertEqual(result.warnings, [])


class FormatFactTest(unittest.TestCase):
    def test_malformed_id_is_an_error(self):
        document = _valid_document()
        document["format_facts"][0]["id"] = "F001"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("FF001 形式" in e for e in result.errors))

    def test_duplicate_id_is_an_error(self):
        document = _valid_document()
        document["format_facts"].append(dict(document["format_facts"][0]))
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("重複" in e for e in result.errors))

    def test_empty_statement_is_an_error(self):
        document = _valid_document()
        document["format_facts"][0]["statement"] = ""
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("statement は必須" in e for e in result.errors))

    def test_invalid_grade_is_an_error(self):
        # format_facts も共通のエビデンス項目の検査（_validate_evidence）を通ることを確認する。
        document = _valid_document()
        document["format_facts"][0]["grade"] = "E"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("format_facts[0].grade" in e for e in result.errors))


class ThemeTest(unittest.TestCase):
    def test_malformed_id_is_an_error(self):
        document = _valid_document()
        document["themes"][0]["id"] = "T001"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("TH001 形式" in e for e in result.errors))

    def test_empty_theme_is_an_error(self):
        document = _valid_document()
        document["themes"][0]["theme"] = ""
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("theme は必須" in e for e in result.errors))

    def test_empty_likely_probe_is_an_error(self):
        document = _valid_document()
        document["themes"][0]["likely_probe"] = ""
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("likely_probe は必須" in e for e in result.errors))

    def test_empty_quote_is_an_error(self):
        # themes も共通のエビデンス項目の検査（_validate_evidence）を通ることを確認する。
        document = _valid_document()
        document["themes"][0]["quote"] = ""
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("themes[0].quote" in e for e in result.errors))

    def test_duplicate_id_is_an_error(self):
        document = _valid_document()
        document["themes"].append(dict(document["themes"][0]))
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("重複" in e for e in result.errors))


class SearchLogTest(unittest.TestCase):
    def test_missing_search_log_is_an_error(self):
        document = _valid_document()
        del document["search_log"]
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_log は必須" in e for e in result.errors))

    def test_non_list_search_log_is_an_error(self):
        document = _valid_document()
        document["search_log"] = {}
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_log は配列" in e for e in result.errors))

    def test_empty_search_log_is_an_error(self):
        document = _valid_document()
        document["search_log"] = []
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_log が空" in e for e in result.errors))

    def test_non_object_entry_is_an_error(self):
        document = _valid_document()
        document["search_log"][0] = "not-a-dict"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("search_log[0]" in e and "オブジェクトでなければならない" in e for e in result.errors)
        )

    def test_missing_query_is_an_error(self):
        document = _valid_document()
        del document["search_log"][0]["query"]
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_log[0].query" in e for e in result.errors))

    def test_missing_source_is_an_error(self):
        document = _valid_document()
        del document["search_log"][0]["source"]
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_log[0].source" in e for e in result.errors))

    def test_missing_key_among_the_four_is_an_error(self):
        document = _valid_document()
        del document["search_log"][0]["hit_count"]
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_log[0].hit_count" in e for e in result.errors))

    def test_null_values_for_the_four_keys_pass(self):
        document = _valid_document()
        document["search_log"][0].update(
            {"url": None, "fetched_at": None, "hit_count": None, "adopted_count": None}
        )
        result = vii.validate(document)
        self.assertEqual(result.errors, [])

    def test_url_not_http_is_an_error(self):
        document = _valid_document()
        document["search_log"][0]["url"] = "ftp://example.com"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_log[0].url" in e for e in result.errors))

    def test_malformed_fetched_at_is_an_error(self):
        document = _valid_document()
        document["search_log"][0]["fetched_at"] = "not-a-date"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_log[0].fetched_at" in e for e in result.errors))

    def test_iso_datetime_fetched_at_passes(self):
        document = _valid_document()
        document["search_log"][0]["fetched_at"] = "2026-09-04T10:00:00Z"
        result = vii.validate(document)
        self.assertEqual(result.errors, [])

    def test_bool_hit_count_is_an_error(self):
        document = _valid_document()
        document["search_log"][0]["hit_count"] = True
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_log[0].hit_count" in e for e in result.errors))

    def test_negative_adopted_count_is_an_error(self):
        document = _valid_document()
        document["search_log"][0]["adopted_count"] = -1
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("search_log[0].adopted_count" in e for e in result.errors))


class OpenQuestionsTest(unittest.TestCase):
    def test_non_list_open_questions_is_an_error(self):
        document = _valid_document()
        document["open_questions"] = "text"
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("open_questions は配列" in e for e in result.errors))

    def test_empty_string_element_is_an_error(self):
        document = _valid_document()
        document["open_questions"] = [""]
        result = vii.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("open_questions[0]" in e for e in result.errors))

    def test_missing_open_questions_passes(self):
        document = _valid_document()
        del document["open_questions"]
        result = vii.validate(document)
        self.assertEqual(result.errors, [])


class CoverageNotesTest(unittest.TestCase):
    def test_missing_coverage_notes_is_a_warning(self):
        document = _valid_document()
        del document["coverage_notes"]
        result = vii.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("coverage_notes が未記載" in w for w in result.warnings))

    def test_empty_coverage_notes_is_a_warning(self):
        document = _valid_document()
        document["coverage_notes"] = "  "
        result = vii.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("coverage_notes が未記載" in w for w in result.warnings))


class ResultShapeTest(unittest.TestCase):
    def test_to_dict_shape(self):
        d = vii.validate(_valid_document()).to_dict()
        self.assertEqual(d["status"], "PASS")
        self.assertEqual(d["error_count"], 0)
        self.assertIn("warnings", d)

    def test_format_report_first_line(self):
        report = vii.format_report(vii.validate(_valid_document()))
        self.assertTrue(report.startswith("検証結果: PASS（ERROR 0件 / WARN 0件）"))

    def test_immutability_of_input(self):
        document = _valid_document()
        snapshot = copy.deepcopy(document)
        vii.validate(document)
        self.assertEqual(document, snapshot)


class CliTest(unittest.TestCase):
    def _write_tmp(self, obj) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def test_main_returns_0_on_valid(self):
        self.assertEqual(vii.main([self._write_tmp(_valid_document())]), 0)

    def test_main_returns_1_on_invalid(self):
        document = _valid_document()
        del document["company"]
        self.assertEqual(vii.main([self._write_tmp(document)]), 1)

    def test_main_returns_1_on_broken_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{ not valid json ")
        self.addCleanup(os.remove, path)
        self.assertEqual(vii.main([path]), 1)

    def test_main_json_flag_valid(self):
        self.assertEqual(vii.main([self._write_tmp(_valid_document()), "--json"]), 0)

    def test_main_returns_0_on_valid_with_bom(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8-sig") as f:
            json.dump(_valid_document(), f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        self.assertEqual(vii.main([path]), 0)


class ExampleAssetTest(unittest.TestCase):
    def _asset_path(self, name: str) -> str:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base, "assets", name)

    def test_bundled_example_passes(self):
        document = vii.load_json(self._asset_path("interview_intel_example.json"))
        result = vii.validate(document)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


if __name__ == "__main__":
    unittest.main()
