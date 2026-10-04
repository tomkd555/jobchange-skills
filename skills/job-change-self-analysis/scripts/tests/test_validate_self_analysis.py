"""validate_self_analysis.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_self_analysis
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

import validate_self_analysis as vsa  # noqa: E402


def _valid_self_analysis() -> dict:
    """ERROR 0件・WARN 0件になる完全な self_analysis.json を返す。"""
    return {
        "schema_version": "1.0",
        "updated_at": "2026-07-16",
        "behavioral_episodes": [
            {
                "id": "ep-1",
                "period": "2022-04〜2023-03",
                "situation": "新規プロジェクトの立ち上げ期で要員が不足していた",
                "task": "API 基盤の設計と実装を担当した",
                "action": "既存資産を調査し段階的な移行計画を提案・実行した",
                "result": "予定より1ヶ月早くリリースした",
                "metric": "応答時間を40%削減した",
                "reproducibility": "別チームでも同じ手順で再現できた",
                "emotion_note": "裁量が大きく手応えを感じていた",
            }
        ],
        "others_feedback": [
            {
                "id": "fb-1",
                "source_type": "上司",
                "content": "課題を分解して周囲を巻き込む進め方が良い",
                "context": "半期評価面談",
                "linked_episode_ids": ["ep-1"],
            }
        ],
        "interests": {
            "domains": ["現実的領域", "研究的領域"],
            "concrete_topics": ["基盤設計", "パフォーマンス改善"],
        },
        "values": [
            {"value": "裁量を持って進める", "evidence_episode_ids": ["ep-1"]}
        ],
        "career_adaptability": {
            "concern": {"self_note": "将来を見据えて動ける", "evidence_episode_ids": ["ep-1"]},
            "control": {"self_note": "自分で計画を立てられる", "evidence_episode_ids": ["ep-1"]},
            "curiosity": {"self_note": "新しい技術を試す", "evidence_episode_ids": ["ep-1"]},
            "confidence": {"self_note": "困難な課題でもやり切れる", "evidence_episode_ids": ["ep-1"]},
        },
        "strengths": [
            {"statement": "課題分解力", "episode_ids": ["ep-1"], "feedback_ids": ["fb-1"]}
        ],
        "career_narrative": {
            "life_theme": "仕組みを作って周囲を助ける",
            "turning_points": ["新規プロジェクトへの異動"],
            "consistent_motivation": "裁量を持って基盤を作ること",
            "future_direction": "より大きな裁量で基盤設計を担いたい",
        },
        "reason_for_change": {
            "raw_reasons": ["裁量が小さい", "評価制度に不満"],
            "constructive_version": "裁量を持って基盤設計に取り組める環境を求めている",
            "consistency_note": "job_change_axis.reasons の「裁量の拡大」と一致する",
        },
        "notes": "",
    }


def _valid_personality_marker(
    marker_id: str, construct: str, linked_episode_ids=None, feedback_ids=None
) -> dict:
    return {
        "id": marker_id,
        "construct": construct,
        "options": ["段取りを先に固めてから動く", "状況に合わせて組み替えながら動く"],
        "response": "段取りを先に固めてから動く",
        "linked_episode_ids": linked_episode_ids if linked_episode_ids is not None else ["ep-1"],
        "feedback_ids": feedback_ids if feedback_ids is not None else [],
        "note": None,
    }


def _valid_self_analysis_v11() -> dict:
    """ERROR 0件・WARN 0件になる、personality（1.1）付きの完全な self_analysis.json を返す。"""
    d = _valid_self_analysis()
    d["schema_version"] = "1.1"
    d["personality"] = {
        "markers": [
            _valid_personality_marker("pm-1", "planning_style", ["ep-1"], ["fb-1"]),
            _valid_personality_marker("pm-2", "decision_style", ["ep-1"], []),
        ],
        "presentation": "段取りを先に固めてから動く行動が、ep-1 で繰り返し見られる。",
    }
    d["strengths"][0]["constructs"] = ["planning_style", "decision_style"]
    return d


_DEL = object()


def _set(path: list, value=_DEL):
    """path 末端に value を代入する変異を返す（value 省略で削除）。"""

    def mutate(d: dict) -> None:
        node = d
        for key in path[:-1]:
            node = node[key]
        if value is _DEL:
            del node[path[-1]]
        else:
            node[path[-1]] = value

    return mutate


def _both(*mutations):
    def mutate(d: dict) -> None:
        for m in mutations:
            m(d)

    return mutate


def _dup_episode(d: dict) -> None:
    d["behavioral_episodes"].append(copy.deepcopy(d["behavioral_episodes"][0]))


_MARKERS = ["personality", "markers"]
_UNLINK_PM2 = _both(
    _set(_MARKERS + [1, "linked_episode_ids"], []), _set(_MARKERS + [1, "feedback_ids"], [])
)


def _presentation(text: str):
    return _set(["personality", "presentation"], text)


class ValidateTest(unittest.TestCase):
    def test_valid_documents_have_no_errors_or_warnings(self):
        """1.0 / 1.1 と personality の省略形ごとの正常形。"""
        rows = [
            ("1.0（personality なし）", _valid_self_analysis, None),
            ("1.1 完全形", _valid_self_analysis_v11, None),
            ("personality が null", _valid_self_analysis_v11, _set(["personality"], None)),
            ("markers が空配列", _valid_self_analysis_v11, _set(_MARKERS, [])),
            ("marker に options なし", _valid_self_analysis_v11, _set(_MARKERS + [0, "options"])),
        ]
        for label, build, mutate in rows:
            with self.subTest(label):
                d = build()
                if mutate:
                    mutate(d)
                snapshot = copy.deepcopy(d)
                result = vsa.validate(d)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])
                self.assertEqual(d, snapshot)

    def test_bundled_example_passes(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        document = vsa.load_self_analysis(os.path.join(base, "assets", "self_analysis_example.json"))
        result = vsa.validate(document)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_error_rules(self):
        ep = ["behavioral_episodes", 0]
        rows = [
            ("ルートがオブジェクトでない", None, "(root)"),
            ("schema_version が空白", _set(["schema_version"], "  "), "schema_version"),
            ("behavioral_episodes が空", _set(["behavioral_episodes"], []), "behavioral_episodes"),
            ("エピソードがオブジェクトでない", _set(["behavioral_episodes"], ["文字列"]), "behavioral_episodes[0]"),
            ("エピソードの action が空白", _set(ep + ["action"], "  "), "behavioral_episodes[0].action"),
            ("エピソードの id が無い", _set(ep + ["id"]), "behavioral_episodes[0].id"),
            ("エピソードの id が無くても参照整合を検出する", _set(ep + ["id"]), "strengths[0].episode_ids"),
            ("フィードバックの id が無いと参照整合を検出する", _set(["others_feedback", 0, "id"]), "strengths[0].feedback_ids"),
            ("strengths の根拠が両方空", _both(_set(["strengths", 0, "episode_ids"], []), _set(["strengths", 0, "feedback_ids"], [])), "strengths[0]"),
            ("strengths が実在しない episode を指す", _set(["strengths", 0, "episode_ids"], ["ep-999"]), "参照整合"),
            ("values が実在しない episode を指す", _set(["values", 0, "evidence_episode_ids"], ["ep-999"]), "values[0]"),
            ("career_adaptability が実在しない episode を指す", _set(["career_adaptability", "concern", "evidence_episode_ids"], ["ep-999"]), "career_adaptability.concern"),
            ("career_narrative の life_theme が無い", _set(["career_narrative", "life_theme"]), "life_theme"),
            ("reason_for_change の raw_reasons が空", _set(["reason_for_change", "raw_reasons"], []), "raw_reasons"),
            ("personality がオブジェクトでない", _set(["personality"], "文字列"), "personality"),
            ("markers が配列でない", _set(_MARKERS, "文字列"), "personality.markers"),
            ("marker の construct が語彙にない", _set(_MARKERS + [0, "construct"], "unknown_construct"), "personality.markers[0].construct"),
            ("marker の options が1件", _set(_MARKERS + [0, "options"], ["1件だけ"]), "personality.markers[0].options"),
            ("marker の response が options にない", _set(_MARKERS + [0, "response"], "選択肢にない回答"), "personality.markers[0].response"),
            ("marker が実在しない feedback を指す", _set(_MARKERS + [0, "feedback_ids"], ["fb-999"]), "personality.markers[0].feedback_ids"),
            ("presentation が文字列でない", _presentation(123), "personality.presentation"),
            ("strengths.constructs が語彙にない", _set(["strengths", 0, "constructs"], ["unknown_construct"]), "strengths[0].constructs"),
        ]
        for label, mutate, expected in rows:
            with self.subTest(label):
                d = _valid_self_analysis_v11()
                if mutate is None:
                    d = ["not", "object"]
                else:
                    mutate(d)
                result = vsa.validate(d)
                self.assertFalse(result.ok)
                self.assertTrue(any(expected in e for e in result.errors), result.errors)

    def test_warn_rules(self):
        rows = [
            ("others_feedback が0件", _both(_set(["others_feedback"], []), _set(["strengths", 0, "feedback_ids"], []), _set(_MARKERS + [0, "feedback_ids"], [])), "others_feedback"),
            ("metric が1件も無い", _set(["behavioral_episodes", 0, "metric"], None), "metric"),
            ("updated_at が無い", _set(["updated_at"]), "updated_at"),
            ("interests が空", _set(["interests"], {"domains": [], "concrete_topics": []}), "interests"),
            ("values が空", _set(["values"], []), "values"),
            ("episode の id が重複", _dup_episode, "behavioral_episodes[1].id"),
            ("source_type が値域外", _set(["others_feedback", 0, "source_type"], "取引先"), "source_type"),
            ("constructive_version が raw_reasons と同一", _set(["reason_for_change", "constructive_version"], "裁量が小さい"), "constructive_version"),
            ("未知の schema_version", _set(["schema_version"], "9.9"), "schema_version"),
            ("marker が自己申告だけ", _UNLINK_PM2, "自己申告だけの記録"),
            ("根拠のない marker の construct を強みが使う", _UNLINK_PM2, "strengths[0].constructs"),
            ("presentation が「〜型です」", _presentation("計測してから動く慎重型です。"), "personality.presentation"),
            ("presentation が「〜のタイプです」（「の」直後でも「タイプ」は対象）", _presentation("計画重視のタイプです。"), "personality.presentation"),
        ]
        for label, mutate, expected in rows:
            with self.subTest(label):
                d = _valid_self_analysis_v11()
                mutate(d)
                result = vsa.validate(d)
                self.assertTrue(result.ok, result.errors)
                self.assertTrue(any(expected in w for w in result.warnings), result.warnings)

    def test_accepted_variants_stay_clean(self):
        """ERROR にも WARN にもならない許容形。"""
        rows = [
            ("source_type が null", _set(["others_feedback", 0, "source_type"], None)),
            ("「判断の型である」は分類ラベルとみなさない", _presentation("判断の型である decision_style の申告と、ep-1 の計測を先に置く行動が一致している。")),
            ("marker の無い construct は強みに書いてよい", _set(["strengths", 0, "constructs"], ["planning_style", "collaboration_style"])),
        ]
        for label, mutate in rows:
            with self.subTest(label):
                d = _valid_self_analysis_v11()
                mutate(d)
                result = vsa.validate(d)
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
        invalid = _valid_self_analysis()
        del invalid["schema_version"]
        rows = [
            ("正常", json.dumps(_valid_self_analysis(), ensure_ascii=False), "utf-8", 0),
            ("BOM 付きの正常", json.dumps(_valid_self_analysis(), ensure_ascii=False), "utf-8-sig", 0),
            ("ERROR あり", json.dumps(invalid, ensure_ascii=False), "utf-8", 1),
            ("壊れた JSON", "{ not valid json ", "utf-8", 1),
        ]
        for label, text, encoding, code in rows:
            with self.subTest(label):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(vsa.main([self._write(text, encoding)]), code)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            vsa.main([self._write(json.dumps(_valid_self_analysis())), "--json"])
        self.assertEqual(
            set(json.loads(buf.getvalue())),
            {"status", "error_count", "warning_count", "errors", "warnings"},
        )


if __name__ == "__main__":
    unittest.main()
