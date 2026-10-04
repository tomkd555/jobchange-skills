"""validate_interview_intel.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_interview_intel
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


def _rq(d):
    return d["reported_questions"][0]


def _log(d):
    return d["search_log"][0]


def _all_empty(d, **extra):
    d["reported_questions"] = []
    d["format_facts"] = []
    d["themes"] = []
    d.update(extra)


class ValidateTest(unittest.TestCase):
    def test_valid_document_has_no_error_and_no_warning(self):
        result = vii.validate(_valid_document())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_bundled_example_passes(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        document = vii.load_json(os.path.join(base, "assets", "interview_intel_example.json"))
        result = vii.validate(document)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_error_rules(self):
        rows = [
            ("ルートが配列", None, "ルート要素"),
            ("schema_version 欠落（必須文字列）", lambda d: d.pop("schema_version"), "schema_version は必須"),
            ("researched_at 形式", lambda d: d.__setitem__("researched_at", "2026/09/04"), "YYYY-MM-DD"),
            ("researched_at が実在しない日付", lambda d: d.__setitem__("researched_at", "2026-02-30"), "researched_at"),
            ("role_title が文字列でも null でもない", lambda d: d.__setitem__("role_title", 1), "role_title"),
            ("配列でない（reported_questions）", lambda d: d.__setitem__("reported_questions", {}), "reported_questions は配列"),
            ("要素がオブジェクトでない", lambda d: d["format_facts"].__setitem__(0, "FF001"), "オブジェクトでなければならない"),
            ("id 形式（RQ + 3桁以上）", lambda d: _rq(d).__setitem__("id", "Q001"), "RQ001 形式"),
            ("id 重複", lambda d: d["reported_questions"][1].__setitem__("id", "RQ001"), "重複"),
            ("FF の id 形式", lambda d: d["format_facts"][0].__setitem__("id", "RQ001"), "FF001 形式"),
            ("TH の id 形式", lambda d: d["themes"][0].__setitem__("id", "FF001"), "TH001 形式"),
            ("kind が語彙外", lambda d: _rq(d).__setitem__("kind", "guessed"), "kind は"),
            ("source_url が http でない", lambda d: _rq(d).__setitem__("source_url", "転職会議"), "source_url"),
            ("grade が語彙外", lambda d: _rq(d).__setitem__("grade", "S"), "grade は"),
            ("quote が空（必須文字列）", lambda d: _rq(d).__setitem__("quote", ""), "quote は必須"),
            ("accessed が実在しない日付", lambda d: _rq(d).__setitem__("accessed", "2026-13-01"), "accessed"),
            ("statement が空", lambda d: d["format_facts"][0].__setitem__("statement", ""), "statement は必須"),
            ("likely_probe が空", lambda d: d["themes"][0].__setitem__("likely_probe", ""), "likely_probe は必須"),
            ("search_log 欠落", lambda d: d.pop("search_log"), "search_log は必須"),
            ("search_log が空", lambda d: d.__setitem__("search_log", []), "search_log が空"),
            ("search_log のキー欠落（null 明記が必要）", lambda d: _log(d).pop("hit_count"), "hit_count は必須"),
            ("search_log.url が http でも null でもない", lambda d: _log(d).__setitem__("url", "転職会議"), "search_log[0].url"),
            ("fetched_at 形式", lambda d: _log(d).__setitem__("fetched_at", "2026/09/04"), "fetched_at"),
            ("hit_count が負数", lambda d: _log(d).__setitem__("hit_count", -1), "hit_count"),
            ("hit_count が真偽値", lambda d: _log(d).__setitem__("hit_count", True), "hit_count"),
            ("open_questions の空要素", lambda d: d.__setitem__("open_questions", [""]), "open_questions[0]"),
            ("3配列が空で open_questions も空", lambda d: _all_empty(d, open_questions=[]), "何も語っていない"),
            ("3配列が空で open_questions 欠落", lambda d: (_all_empty(d), d.pop("open_questions")), "何も語っていない"),
        ]
        for label, mutate, expected in rows:
            with self.subTest(label):
                document = _valid_document()
                if mutate is None:
                    result = vii.validate([])
                else:
                    mutate(document)
                    result = vii.validate(document)
                self.assertFalse(result.ok)
                self.assertTrue(any(expected in e for e in result.errors), result.errors)

    def test_accepted_variants_have_no_error(self):
        rows = [
            ("role_title が null", lambda d: d.__setitem__("role_title", None)),
            ("fetched_at が ISO 8601 時刻付き", lambda d: _log(d).__setitem__("fetched_at", "2026-09-04T10:30:00+09:00")),
            ("search_log の null 値", lambda d: _log(d).update(url=None, fetched_at=None, hit_count=None, adopted_count=None)),
            ("3配列が空でも open_questions がある", lambda d: _all_empty(d)),
        ]
        for label, mutate in rows:
            with self.subTest(label):
                document = _valid_document()
                mutate(document)
                self.assertEqual(vii.validate(document).errors, [])

    def test_shape_error_is_not_reported_twice(self):
        # 配列でない場合は形状エラー1件だけで、「何も語っていない」を重ねない。
        document = _valid_document()
        _all_empty(document, open_questions=[])
        document["reported_questions"] = {}
        result = vii.validate(document)
        self.assertEqual(len(result.errors), 1)

    def test_warn_rules(self):
        rows = [
            ("schema_version が未知", lambda d: d.__setitem__("schema_version", "0.9"), "既知のバージョン"),
            ("配列が空（共通ヘルパー）", lambda d: d.__setitem__("themes", []), "themes が空"),
            ("grade が D", lambda d: _rq(d).__setitem__("grade", "D"), "grade が D"),
            ("accessed 未記載", lambda d: _rq(d).pop("accessed"), "accessed が未記載"),
            ("reported の質問と引用が重ならない", lambda d: _rq(d).__setitem__("quote", "全く別の内容の引用"), "逐語"),
            ("coverage_notes 未記載", lambda d: d.pop("coverage_notes"), "coverage_notes"),
        ]
        for label, mutate, expected in rows:
            with self.subTest(label):
                document = _valid_document()
                mutate(document)
                result = vii.validate(document)
                self.assertEqual(result.errors, [])
                self.assertTrue(any(expected in w for w in result.warnings), result.warnings)


class CliTest(unittest.TestCase):
    def _run(self, content: str, *extra: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "interview_intel.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = vii.main([path, *extra])
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
