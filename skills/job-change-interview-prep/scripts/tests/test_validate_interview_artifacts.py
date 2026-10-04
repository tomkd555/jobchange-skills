"""validate_interview_artifacts.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_interview_artifacts
"""
from __future__ import annotations

import copy
import io
import json
import os
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKILL_DIR = os.path.dirname(_SCRIPTS_DIR)
_INTERVIEW_FORMAT_MD = os.path.join(_SKILL_DIR, "references", "interview-format.md")

sys.path.insert(0, _SCRIPTS_DIR)

import validate_interview_artifacts as via  # noqa: E402

_CODE_RE = re.compile(r"`([^`]+)`")


def _known_category_terms(md_path: str) -> list[str]:
    """「The known question categories are …」の文からバックティック囲みの語彙を順に取り出す。"""
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
                "basis": "axis.job_change_axis.reasons[0]",
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
                "feedback": "axis.job_change_axis.reasons[0] と矛盾なく述べている。",
                "improvement": "claim C001 と結び付けて志望先での目標まで続ける。",
            }
        ],
    }


def _degrade(d, reason="company_research.json が無い"):
    d["degraded"] = True
    d["degraded_reason"] = reason


def _degraded_with_graded_fit(d):
    _degrade(d)


def _degraded_excluded_fit(d):
    _degrade(d)
    d["evaluations"][0]["scores"]["company_fit"] = "対象外"


class ValidateTest(unittest.TestCase):
    def test_valid_fixtures_pass(self):
        rows = [
            ("questions", _valid_questions(), None),
            ("answers", _valid_answers(), None),
            ("evaluation", _valid_evaluation(), None),
            ("answers + questions 相互参照", _valid_answers(), _valid_questions()),
        ]
        for label, document, questions in rows:
            with self.subTest(label):
                result = via.validate(document, questions=questions)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_detect_kind(self):
        self.assertEqual(via.detect_kind(_valid_questions()), "questions")
        self.assertEqual(via.detect_kind(_valid_answers()), "answers")
        self.assertEqual(via.detect_kind(_valid_evaluation()), "evaluation")

    def test_bundled_examples_pass(self):
        def asset(name):
            return os.path.join(_SKILL_DIR, "assets", name)

        questions = via.load_json(asset("interview_questions_example.json"))
        for name in ("interview_questions_example.json", "interview_answers_example.json",
                     "interview_evaluation_example.json"):
            with self.subTest(name):
                result = via.validate(via.load_json(asset(name)), questions=questions)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_error_rules(self):
        q, a, e = _valid_questions, _valid_answers, _valid_evaluation
        rows = [
            ("ルートが配列", lambda: ["questions"], None, None, "ルート要素"),
            ("種別キーが無い", lambda: {"degraded": False, "degraded_reason": None}, None, None, "判別できない"),
            ("種別キーが2つ", q, lambda d: d.__setitem__("answers", []), None, "判別できない"),
            ("degraded が真偽値でない", q, lambda d: d.__setitem__("degraded", "false"), None, "degraded は真偽値"),
            ("degraded_reason 欠落", q, lambda d: d.pop("degraded_reason"), None, "degraded_reason は必須"),
            ("degraded=true で理由が空", q, lambda d: d.update(degraded=True), None, "理由の文字列"),
            ("degraded=false で理由あり", q, lambda d: d.update(degraded_reason="書かない"), None, "null でなければならない"),
            ("entries が配列でない", q, lambda d: d.__setitem__("questions", {}), None, "配列でなければならない"),
            ("要素がオブジェクトでない", q, lambda d: d["questions"].__setitem__(0, "Q001"), None, "オブジェクトでなければならない"),
            ("id 形式（Q + 3桁以上）", q, lambda d: d["questions"][0].__setitem__("id", "1"), None, "Q001 形式"),
            ("id 重複", q, lambda d: d["questions"][1].__setitem__("id", "Q001"), None, "重複"),
            ("category が空（必須文字列）", q, lambda d: d["questions"][0].__setitem__("category", ""), None, "category は必須"),
            ("notes が配列でない", q, lambda d: d.__setitem__("notes", "配慮事項"), None, "notes は配列"),
            ("notes に空要素", q, lambda d: d.__setitem__("notes", ["面接は二段階である。", ""]), None, "notes[1]"),
            ("answered_at 形式", a, lambda d: d["answers"][0].__setitem__("answered_at", "2026/08/14"), None, "YYYY-MM-DD"),
            ("scores がオブジェクトでない", e, lambda d: d["evaluations"][0].__setitem__("scores", "充足"), None, "scores はオブジェクト"),
            ("core score が語彙外", e, lambda d: d["evaluations"][0]["scores"].__setitem__("star", "良い"), None, "scores.star"),
            ("degraded=true で company_fit に評価値", e, _degraded_with_graded_fit, None, "対象外」または欠落"),
            ("degraded=true で理由が空白", e, lambda d: (_degrade(d, "   "), d["evaluations"][0]["scores"].__setitem__("company_fit", "対象外")), None, "理由の文字列"),
            ("degraded=false で company_fit が対象外", e, lambda d: d["evaluations"][0]["scores"].__setitem__("company_fit", "対象外"), None, "対象外」にできない"),
            ("degraded=false で company_fit 欠落", e, lambda d: d["evaluations"][0]["scores"].pop("company_fit"), None, "scores.company_fit"),
            ("answers の質問 id が質問側に無い", a, lambda d: d["answers"][1].__setitem__("question_id", "Q009"), q, "存在しない"),
            ("evaluations の質問 id が質問側に無い", e, lambda d: d["evaluations"][0].__setitem__("question_id", "Q009"), q, "存在しない"),
        ]
        for label, build, mutate, questions, expected in rows:
            with self.subTest(label):
                document = build()
                if mutate is not None:
                    mutate(document)
                result = via.validate(document, questions=questions() if questions else None)
                self.assertFalse(result.ok)
                self.assertTrue(any(expected in err for err in result.errors), result.errors)

    def test_accepted_variants_have_no_error(self):
        q, a, e = _valid_questions, _valid_answers, _valid_evaluation
        rows = [
            ("4桁の id", q, lambda d: d["questions"][0].__setitem__("id", "Q1000"), None),
            ("degraded=true と理由と対象外", e, _degraded_excluded_fit, None),
            ("degraded=true で company_fit 欠落", e, lambda d: (_degrade(d), d["evaluations"][0]["scores"].pop("company_fit")), None),
            ("questions 未指定なら id を照合しない", e, lambda d: d["evaluations"][0].__setitem__("question_id", "Q009"), None),
            ("未回答の質問が残る", a, lambda d: d["answers"].pop(1), q),
            ("answers 種別の notes は検査しない", a, lambda d: d.__setitem__("notes", "不正"), None),
        ]
        for label, build, mutate, questions in rows:
            with self.subTest(label):
                document = build()
                mutate(document)
                result = via.validate(document, questions=questions() if questions else None)
                self.assertEqual(result.errors, [])

    def test_warn_rules(self):
        q = _valid_questions
        rows = [
            ("questions が空", lambda d: d.__setitem__("questions", []), "questions が空"),
            ("カタログ外の category", lambda d: d["questions"][0].__setitem__("category", "雑談"), "既知の質問類型"),
            ("語彙外の provenance（非文字列）", lambda d: d["questions"][0].__setitem__("provenance", 1), "既知の出所"),
            ("provenance 欠落", lambda d: d["questions"][0].pop("provenance"), "provenance"),
            ("語彙外の stage", lambda d: d["questions"][0].__setitem__("stage", "三次面接"), "既知の選考段階"),
        ]
        for label, mutate, expected in rows:
            with self.subTest(label):
                document = q()
                mutate(document)
                result = via.validate(document)
                self.assertEqual(result.errors, [])
                self.assertTrue(any(expected in w for w in result.warnings), result.warnings)

    def test_input_is_not_mutated(self):
        document = _valid_evaluation()
        snapshot = copy.deepcopy(document)
        via.validate(document, questions=_valid_questions())
        self.assertEqual(document, snapshot)


class CliTest(unittest.TestCase):
    def _run(self, *args: str) -> tuple[int, str]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = via.main(list(args))
        return code, buffer.getvalue()

    def _write(self, obj) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if isinstance(obj, str):
                f.write(obj)
            else:
                json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def test_exit_codes(self):
        invalid = _valid_questions()
        del invalid["degraded"]
        answers = self._write(_valid_answers())
        rows = [
            ("valid", [self._write(_valid_questions())], 0),
            ("invalid", [self._write(invalid)], 1),
            ("broken json", [self._write("{ not valid json ")], 1),
            ("--questions で相互参照", [answers, "--questions", self._write(_valid_questions())], 0),
            ("--questions が読めない", [answers, "--questions", answers + ".missing"], 1),
        ]
        for label, argv, expected in rows:
            with self.subTest(label):
                self.assertEqual(self._run(*argv)[0], expected)

    def test_json_output_keys(self):
        _, output = self._run(self._write(_valid_answers()), "--json")
        self.assertEqual(
            set(json.loads(output)),
            {"status", "error_count", "warning_count", "errors", "warnings"},
        )


class VocabularySyncTest(unittest.TestCase):
    """検証スクリプトの語彙定数と references/interview-format.md の原本との一致を確かめる。"""

    def test_categories_match_interview_format(self):
        terms = _known_category_terms(_INTERVIEW_FORMAT_MD)
        self.assertEqual(tuple(terms), via._CATEGORIES)

    def test_provenance_values_match_interview_format(self):
        terms = _field_enum_terms(_INTERVIEW_FORMAT_MD, "provenance")
        self.assertEqual(tuple(terms), via._PROVENANCE_VALUES)

    def test_stage_values_match_interview_format(self):
        terms = _field_enum_terms(_INTERVIEW_FORMAT_MD, "stage")
        self.assertEqual(tuple(terms), via._STAGE_VALUES)


if __name__ == "__main__":
    unittest.main()
