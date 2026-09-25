"""validate_interview_artifacts.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_interview_artifacts
"""
from __future__ import annotations

import copy
import json
import os
import re
import sys
import tempfile
import unittest

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKILL_DIR = os.path.dirname(_SCRIPTS_DIR)
_INTERVIEW_FORMAT_MD = os.path.join(_SKILL_DIR, "references", "interview-format.md")

sys.path.insert(0, _SCRIPTS_DIR)

import validate_interview_artifacts as via  # noqa: E402

_CODE_RE = re.compile(r"`([^`]+)`")


def _known_category_terms(md_path: str) -> list[str]:
    """「既知の質問類型は…である。」の文からバックティック囲みの語彙を順に取り出す。

    後続の `question-bank.md` 等の参照を巻き込まないよう、最初の「である。」までで区切る。
    """
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    start = text.index("The known question categories are ")
    end = text.index(".", start) + len(".")
    return _CODE_RE.findall(text[start:end])


def _field_enum_terms(md_path: str, field_name: str) -> list[str]:
    """`| \\`field_name\\` |` で始まる表行から、フィールド名自身を除く語彙を順に取り出す。"""
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    marker = f"| `{field_name}` |"
    for line in lines:
        if line.startswith(marker):
            return _CODE_RE.findall(line)[1:]
    raise AssertionError(f"{md_path} に `{field_name}` の表行が無い")


def _valid_questions() -> dict:
    """ERROR 0件・WARN 0件になる完全な interview_questions.json を返す。"""
    return {
        "degraded": False,
        "degraded_reason": None,
        "questions": [
            {
                "id": "Q001",
                "category": "転職理由",
                "question": "現職を離れようと考えた理由を聞かせてください。",
                "interviewer_intent": "定着性と転職理由の一貫性を確認する。",
                "basis": "profile.job_change_axis.reasons[0]",
                "provenance": "general",
                "stage": "一次面接",
            },
            {
                "id": "Q002",
                "category": "志望動機",
                "question": "理念のどこに共感しましたか。",
                "interviewer_intent": "共感が経験に裏付けられているかを確認する。",
                "basis": "company_research claim C001",
                "provenance": "inferred",
                "stage": "二次面接",
            },
        ],
    }


def _valid_answers() -> dict:
    """ERROR 0件・WARN 0件になる完全な interview_answers.json を返す。"""
    return {
        "answers": [
            {
                "question_id": "Q001",
                "answer": "設計から運用まで一貫して担える環境で力を伸ばしたいと考えています。",
                "answered_at": "2026-08-14",
            },
            {
                "question_id": "Q002",
                "answer": "申請フローの自動化で月末の作業時間を短くした経験があるためです。",
                "answered_at": "2026-08-15",
            },
        ]
    }


def _valid_evaluation() -> dict:
    """ERROR 0件・WARN 0件になる完全な interview_evaluation.json を返す。"""
    return {
        "degraded": False,
        "degraded_reason": None,
        "evaluations": [
            {
                "question_id": "Q001",
                "scores": {
                    "star": "一部",
                    "specificity": "一部",
                    "consistency": "充足",
                    "company_fit": "不足",
                },
                "feedback": "profile.job_change_axis.reasons[0] と矛盾なく述べている。",
                "improvement": "claim C001 と結び付けて志望先での目標まで続ける。",
            }
        ],
    }


class ValidatePassTest(unittest.TestCase):
    def test_questions_pass(self):
        result = via.validate(_valid_questions())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_answers_pass(self):
        result = via.validate(_valid_answers())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_evaluation_pass(self):
        result = via.validate(_valid_evaluation())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


class KindDetectionTest(unittest.TestCase):
    def test_detect_kind_per_artifact(self):
        self.assertEqual(via.detect_kind(_valid_questions()), "questions")
        self.assertEqual(via.detect_kind(_valid_answers()), "answers")
        self.assertEqual(via.detect_kind(_valid_evaluation()), "evaluation")

    def test_non_object_root_is_an_error(self):
        result = via.validate(["questions"])
        self.assertFalse(result.ok)
        self.assertTrue(any("ルート要素" in e for e in result.errors))

    def test_no_kind_key_is_an_error(self):
        result = via.validate({"degraded": False, "degraded_reason": None})
        self.assertFalse(result.ok)
        self.assertTrue(any("判別できない" in e for e in result.errors))

    def test_two_kind_keys_is_an_error(self):
        document = _valid_questions()
        document["answers"] = []
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("判別できない" in e for e in result.errors))


class DegradedTest(unittest.TestCase):
    def test_degraded_true_with_reason_passes(self):
        document = _valid_questions()
        document["degraded"] = True
        document["degraded_reason"] = "company_research.json が無いためフォールバックした"
        result = via.validate(document)
        self.assertEqual(result.errors, [])

    def test_missing_degraded_is_an_error(self):
        document = _valid_questions()
        del document["degraded"]
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("degraded は真偽値" in e for e in result.errors))

    def test_non_bool_degraded_is_an_error(self):
        document = _valid_questions()
        document["degraded"] = "false"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("degraded は真偽値" in e for e in result.errors))

    def test_missing_degraded_reason_is_an_error(self):
        document = _valid_questions()
        del document["degraded_reason"]
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("degraded_reason は必須" in e for e in result.errors))

    def test_degraded_true_without_reason_is_an_error(self):
        document = _valid_questions()
        document["degraded"] = True
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("理由の文字列" in e for e in result.errors))

    def test_degraded_true_with_empty_reason_is_an_error(self):
        document = _valid_evaluation()
        document["degraded"] = True
        document["degraded_reason"] = "   "
        document["evaluations"][0]["scores"]["company_fit"] = "対象外"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("理由の文字列" in e for e in result.errors))

    def test_degraded_false_with_reason_is_an_error(self):
        document = _valid_questions()
        document["degraded_reason"] = "理由を書いてはならない"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("null でなければならない" in e for e in result.errors))


class QuestionsTest(unittest.TestCase):
    def test_non_list_questions_is_an_error(self):
        document = _valid_questions()
        document["questions"] = {}
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("配列でなければならない" in e for e in result.errors))

    def test_empty_questions_is_a_warning(self):
        document = _valid_questions()
        document["questions"] = []
        result = via.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("questions が空" in w for w in result.warnings))

    def test_non_object_entry_is_an_error(self):
        document = _valid_questions()
        document["questions"][0] = "Q001"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("オブジェクトでなければならない" in e for e in result.errors))

    def test_missing_id_is_an_error(self):
        document = _valid_questions()
        del document["questions"][0]["id"]
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("questions[0].id" in e for e in result.errors))

    def test_malformed_id_is_an_error(self):
        document = _valid_questions()
        document["questions"][0]["id"] = "1"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("Q001 形式" in e for e in result.errors))

    def test_four_digit_id_passes(self):
        document = _valid_questions()
        document["questions"][0]["id"] = "Q1000"
        result = via.validate(document)
        self.assertEqual(result.errors, [])

    def test_duplicate_id_is_an_error(self):
        document = _valid_questions()
        document["questions"][1]["id"] = "Q001"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("重複" in e for e in result.errors))

    def test_missing_category_is_an_error(self):
        document = _valid_questions()
        document["questions"][0]["category"] = ""
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("category は必須" in e for e in result.errors))

    def test_unknown_category_is_a_warning(self):
        document = _valid_questions()
        document["questions"][0]["category"] = "雑談"
        result = via.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("既知の質問類型" in w for w in result.warnings))

    def test_foreign_categories_pass(self):
        document = _valid_questions()
        document["questions"][0]["category"] = "ビヘイビアラル"
        document["questions"][1]["category"] = "ケース"
        result = via.validate(document)
        self.assertEqual(result.warnings, [])

    def test_missing_interviewer_intent_is_an_error(self):
        document = _valid_questions()
        del document["questions"][0]["interviewer_intent"]
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("interviewer_intent は必須" in e for e in result.errors))

    def test_empty_basis_is_an_error(self):
        document = _valid_questions()
        document["questions"][0]["basis"] = "  "
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("basis は必須" in e for e in result.errors))

    def test_empty_question_is_an_error(self):
        document = _valid_questions()
        document["questions"][0]["question"] = ""
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("question は必須" in e for e in result.errors))

    def test_known_provenance_passes(self):
        document = _valid_questions()
        document["questions"][0]["provenance"] = "reported"
        result = via.validate(document)
        self.assertEqual(result.warnings, [])

    def test_unknown_provenance_is_a_warning(self):
        document = _valid_questions()
        document["questions"][0]["provenance"] = "guessed"
        result = via.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("既知の出所" in w for w in result.warnings))

    def test_non_string_provenance_is_a_warning(self):
        document = _valid_questions()
        document["questions"][0]["provenance"] = 1
        result = via.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("既知の出所" in w for w in result.warnings))

    def test_missing_provenance_is_a_warning(self):
        document = _valid_questions()
        del document["questions"][0]["provenance"]
        result = via.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("questions[0].provenance" in w and "欠落" in w for w in result.warnings))

    def test_missing_stage_is_a_warning(self):
        document = _valid_questions()
        del document["questions"][0]["stage"]
        result = via.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("questions[0].stage" in w and "欠落" in w for w in result.warnings))

    def test_known_stage_passes(self):
        document = _valid_questions()
        document["questions"][0]["stage"] = "一次面接"
        result = via.validate(document)
        self.assertEqual(result.warnings, [])

    def test_unknown_stage_is_a_warning(self):
        document = _valid_questions()
        document["questions"][0]["stage"] = "三次面接"
        result = via.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("既知の選考段階" in w for w in result.warnings))

    def test_non_string_stage_is_a_warning(self):
        document = _valid_questions()
        document["questions"][0]["stage"] = 3
        result = via.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("既知の選考段階" in w for w in result.warnings))


class NotesTest(unittest.TestCase):
    def test_notes_on_answers_kind_is_not_checked(self):
        """notes は questions 種別だけで検査される。answers 種別に不正な notes があっても無視する。"""
        document = _valid_answers()
        document["notes"] = "配列でない不正な notes"
        result = via.validate(document)
        self.assertFalse(any("notes" in e for e in result.errors))

    def test_valid_notes_passes(self):
        document = _valid_questions()
        document["notes"] = ["配慮事項に該当する質問は聞かれても答えなくてよい。"]
        result = via.validate(document)
        self.assertEqual(result.errors, [])

    def test_empty_notes_array_passes(self):
        document = _valid_questions()
        document["notes"] = []
        result = via.validate(document)
        self.assertEqual(result.errors, [])

    def test_non_array_notes_is_an_error(self):
        document = _valid_questions()
        document["notes"] = "配慮事項に該当する質問は聞かれても答えなくてよい。"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("notes は配列でなければならない" in e for e in result.errors))

    def test_notes_with_empty_string_is_an_error(self):
        document = _valid_questions()
        document["notes"] = ["面接は二段階である。", ""]
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("notes[1]" in e for e in result.errors))

    def test_questions_with_notes_is_still_detected_as_questions(self):
        document = _valid_questions()
        document["notes"] = ["面接は二段階である。"]
        self.assertEqual(via.detect_kind(document), "questions")


class AnswersTest(unittest.TestCase):
    def test_non_list_answers_is_an_error(self):
        result = via.validate({"answers": "Q001"})
        self.assertFalse(result.ok)
        self.assertTrue(any("配列でなければならない" in e for e in result.errors))

    def test_empty_answers_is_a_warning(self):
        result = via.validate({"answers": []})
        self.assertTrue(result.ok)
        self.assertTrue(any("answers が空" in w for w in result.warnings))

    def test_missing_question_id_is_an_error(self):
        document = _valid_answers()
        del document["answers"][0]["question_id"]
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("answers[0].question_id" in e for e in result.errors))

    def test_duplicate_question_id_is_an_error(self):
        document = _valid_answers()
        document["answers"][1]["question_id"] = "Q001"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("重複" in e for e in result.errors))

    def test_empty_answer_is_an_error(self):
        document = _valid_answers()
        document["answers"][0]["answer"] = ""
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("answer は必須" in e for e in result.errors))

    def test_missing_answered_at_is_an_error(self):
        document = _valid_answers()
        del document["answers"][0]["answered_at"]
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("answered_at は必須" in e for e in result.errors))

    def test_malformed_answered_at_is_an_error(self):
        document = _valid_answers()
        document["answers"][0]["answered_at"] = "2026/08/14"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("YYYY-MM-DD" in e for e in result.errors))


class ScoresTest(unittest.TestCase):
    def test_non_object_scores_is_an_error(self):
        document = _valid_evaluation()
        document["evaluations"][0]["scores"] = "充足"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("scores はオブジェクト" in e for e in result.errors))

    def test_unknown_level_is_an_error(self):
        document = _valid_evaluation()
        document["evaluations"][0]["scores"]["star"] = "良い"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("scores.star" in e for e in result.errors))

    def test_missing_core_score_is_an_error(self):
        document = _valid_evaluation()
        del document["evaluations"][0]["scores"]["consistency"]
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("scores.consistency" in e for e in result.errors))

    def test_excluded_company_fit_with_degraded_true_passes(self):
        document = _valid_evaluation()
        document["degraded"] = True
        document["degraded_reason"] = "company_research.json が無い"
        document["evaluations"][0]["scores"]["company_fit"] = "対象外"
        result = via.validate(document)
        self.assertEqual(result.errors, [])

    def test_missing_company_fit_with_degraded_true_passes(self):
        document = _valid_evaluation()
        document["degraded"] = True
        document["degraded_reason"] = "company_research.json が無い"
        del document["evaluations"][0]["scores"]["company_fit"]
        result = via.validate(document)
        self.assertEqual(result.errors, [])

    def test_graded_company_fit_with_degraded_true_is_an_error(self):
        document = _valid_evaluation()
        document["degraded"] = True
        document["degraded_reason"] = "company_research.json が無い"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("対象外」または欠落" in e for e in result.errors))

    def test_excluded_company_fit_with_degraded_false_is_an_error(self):
        document = _valid_evaluation()
        document["evaluations"][0]["scores"]["company_fit"] = "対象外"
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("対象外」にできない" in e for e in result.errors))

    def test_missing_company_fit_with_degraded_false_is_an_error(self):
        document = _valid_evaluation()
        del document["evaluations"][0]["scores"]["company_fit"]
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("scores.company_fit" in e for e in result.errors))


class EvaluationTest(unittest.TestCase):
    def test_empty_evaluations_is_a_warning(self):
        document = _valid_evaluation()
        document["evaluations"] = []
        result = via.validate(document)
        self.assertTrue(result.ok)
        self.assertTrue(any("evaluations が空" in w for w in result.warnings))

    def test_empty_feedback_is_an_error(self):
        document = _valid_evaluation()
        document["evaluations"][0]["feedback"] = ""
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("feedback は必須" in e for e in result.errors))

    def test_missing_improvement_is_an_error(self):
        document = _valid_evaluation()
        del document["evaluations"][0]["improvement"]
        result = via.validate(document)
        self.assertFalse(result.ok)
        self.assertTrue(any("improvement は必須" in e for e in result.errors))


class CrossReferenceTest(unittest.TestCase):
    def test_question_ids_collects_ids(self):
        self.assertEqual(via.question_ids(_valid_questions()), {"Q001", "Q002"})

    def test_answers_referring_to_existing_questions_pass(self):
        result = via.validate(_valid_answers(), questions=_valid_questions())
        self.assertEqual(result.errors, [])

    def test_answer_referring_to_unknown_question_is_an_error(self):
        document = _valid_answers()
        document["answers"][1]["question_id"] = "Q009"
        result = via.validate(document, questions=_valid_questions())
        self.assertFalse(result.ok)
        self.assertTrue(any("存在しない" in e for e in result.errors))

    def test_evaluation_referring_to_unknown_question_is_an_error(self):
        document = _valid_evaluation()
        document["evaluations"][0]["question_id"] = "Q009"
        result = via.validate(document, questions=_valid_questions())
        self.assertFalse(result.ok)
        self.assertTrue(any("存在しない" in e for e in result.errors))

    def test_unknown_question_id_is_not_checked_without_questions(self):
        document = _valid_evaluation()
        document["evaluations"][0]["question_id"] = "Q009"
        result = via.validate(document)
        self.assertEqual(result.errors, [])

    def test_partial_answers_are_not_an_error(self):
        """未回答の質問が残っていること自体は成果物の欠陥ではない（再開の差分になる）。"""
        document = _valid_answers()
        del document["answers"][1]
        result = via.validate(document, questions=_valid_questions())
        self.assertEqual(result.errors, [])


class CliTest(unittest.TestCase):
    def _write_tmp(self, obj: dict) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def test_main_returns_0_on_valid(self):
        self.assertEqual(via.main([self._write_tmp(_valid_questions())]), 0)

    def test_main_returns_1_on_invalid(self):
        document = _valid_questions()
        del document["degraded"]
        self.assertEqual(via.main([self._write_tmp(document)]), 1)

    def test_main_returns_1_on_broken_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{ not valid json ")
        self.addCleanup(os.remove, path)
        self.assertEqual(via.main([path]), 1)

    def test_main_json_flag_valid(self):
        self.assertEqual(via.main([self._write_tmp(_valid_answers()), "--json"]), 0)

    def test_main_returns_0_on_valid_with_bom(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8-sig") as f:
            json.dump(_valid_evaluation(), f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        self.assertEqual(via.main([path]), 0)

    def test_main_with_questions_option(self):
        answers = self._write_tmp(_valid_answers())
        questions = self._write_tmp(_valid_questions())
        self.assertEqual(via.main([answers, "--questions", questions]), 0)

    def test_main_returns_1_on_broken_questions_option(self):
        answers = self._write_tmp(_valid_answers())
        self.assertEqual(via.main([answers, "--questions", answers + ".missing"]), 1)


class ResultShapeTest(unittest.TestCase):
    def test_to_dict_shape(self):
        d = via.validate(_valid_questions()).to_dict()
        self.assertEqual(d["status"], "PASS")
        self.assertEqual(d["error_count"], 0)
        self.assertIn("warnings", d)

    def test_format_report_first_line(self):
        report = via.format_report(via.validate(_valid_questions()))
        self.assertTrue(report.startswith("検証結果: PASS（ERROR 0件 / WARN 0件）"))

    def test_immutability_of_input(self):
        document = _valid_evaluation()
        snapshot = copy.deepcopy(document)
        via.validate(document, questions=_valid_questions())
        self.assertEqual(document, snapshot)


class ExampleAssetTest(unittest.TestCase):
    def _assets(self, name: str) -> str:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base, "assets", name)

    def test_bundled_examples_pass(self):
        questions = via.load_json(self._assets("interview_questions_example.json"))
        for name in ("interview_questions_example.json", "interview_answers_example.json",
                     "interview_evaluation_example.json"):
            with self.subTest(name=name):
                result = via.validate(via.load_json(self._assets(name)), questions=questions)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])


class VocabularySyncTest(unittest.TestCase):
    """検証スクリプトの語彙定数と references/interview-format.md の原本との一致を確かめる。

    片方だけを直したときに、このテストが落ちる。
    """

    def test_categories_match_interview_format(self):
        terms = _known_category_terms(_INTERVIEW_FORMAT_MD)
        self.assertEqual(len(terms), 18, terms)
        self.assertEqual(tuple(terms), via._CATEGORIES)

    def test_provenance_values_match_interview_format(self):
        terms = _field_enum_terms(_INTERVIEW_FORMAT_MD, "provenance")
        self.assertEqual(tuple(terms), via._PROVENANCE_VALUES)

    def test_stage_values_match_interview_format(self):
        terms = _field_enum_terms(_INTERVIEW_FORMAT_MD, "stage")
        self.assertEqual(tuple(terms), via._STAGE_VALUES)


if __name__ == "__main__":
    unittest.main()
