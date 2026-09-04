"""validate_self_analysis.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_self_analysis
"""
from __future__ import annotations

import copy
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


class ValidatePassTest(unittest.TestCase):
    def test_full_self_analysis_passes_without_warnings(self):
        result = vsa.validate(_valid_self_analysis())
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_full_v11_self_analysis_passes_without_warnings(self):
        result = vsa.validate(_valid_self_analysis_v11())
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_personality_null_is_treated_as_absent(self):
        d = _valid_self_analysis_v11()
        d["personality"] = None
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_markers_empty_list_passes(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"] = []
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_marker_without_options_passes(self):
        d = _valid_self_analysis_v11()
        del d["personality"]["markers"][0]["options"]
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


class ErrorCaseTest(unittest.TestCase):
    def test_root_not_object(self):
        result = vsa.validate(["not", "an", "object"])
        self.assertFalse(result.ok)

    def test_missing_schema_version(self):
        d = _valid_self_analysis()
        del d["schema_version"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("schema_version" in e for e in result.errors))

    def test_empty_schema_version(self):
        d = _valid_self_analysis()
        d["schema_version"] = "  "
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("schema_version" in e for e in result.errors))

    def test_empty_behavioral_episodes(self):
        d = _valid_self_analysis()
        d["behavioral_episodes"] = []
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("behavioral_episodes" in e for e in result.errors))

    def test_episode_not_object(self):
        d = _valid_self_analysis()
        d["behavioral_episodes"] = ["not an object"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("behavioral_episodes[0]" in e for e in result.errors))

    def test_episode_missing_situation(self):
        d = _valid_self_analysis()
        del d["behavioral_episodes"][0]["situation"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("situation" in e for e in result.errors))

    def test_episode_missing_action(self):
        d = _valid_self_analysis()
        d["behavioral_episodes"][0]["action"] = "  "
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("action" in e for e in result.errors))

    def test_episode_missing_result(self):
        d = _valid_self_analysis()
        del d["behavioral_episodes"][0]["result"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("result" in e for e in result.errors))

    def test_episode_missing_id(self):
        d = _valid_self_analysis()
        del d["behavioral_episodes"][0]["id"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("behavioral_episodes[0].id" in e for e in result.errors))

    def test_episode_empty_id(self):
        d = _valid_self_analysis()
        d["behavioral_episodes"][0]["id"] = "  "
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("behavioral_episodes[0].id" in e for e in result.errors))

    def test_episode_non_str_id(self):
        d = _valid_self_analysis()
        d["behavioral_episodes"][0]["id"] = 1
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("behavioral_episodes[0].id" in e for e in result.errors))

    def test_episode_missing_id_keeps_reference_check_working(self):
        """id が欠落しても、その id を指す参照は参照整合エラーとして検出される。"""
        d = _valid_self_analysis()
        del d["behavioral_episodes"][0]["id"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("strengths[0].episode_ids" in e and "参照整合" in e for e in result.errors)
        )
        self.assertTrue(
            any("values[0].evidence_episode_ids" in e and "参照整合" in e for e in result.errors)
        )

    def test_feedback_missing_id(self):
        d = _valid_self_analysis()
        del d["others_feedback"][0]["id"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("others_feedback[0].id" in e for e in result.errors))

    def test_feedback_missing_id_keeps_reference_check_working(self):
        d = _valid_self_analysis()
        del d["others_feedback"][0]["id"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("strengths[0].feedback_ids" in e and "参照整合" in e for e in result.errors)
        )

    def test_feedback_not_object(self):
        d = _valid_self_analysis()
        d["others_feedback"] = ["文字列"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("others_feedback[0]" in e for e in result.errors))

    def test_strengths_missing_statement(self):
        d = _valid_self_analysis()
        del d["strengths"][0]["statement"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("statement" in e for e in result.errors))

    def test_strengths_both_episode_and_feedback_ids_empty(self):
        d = _valid_self_analysis()
        d["strengths"][0]["episode_ids"] = []
        d["strengths"][0]["feedback_ids"] = []
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("strengths[0]" in e for e in result.errors))

    def test_strengths_episode_id_reference_not_found(self):
        d = _valid_self_analysis()
        d["strengths"][0]["episode_ids"] = ["ep-999"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("参照整合" in e for e in result.errors))

    def test_strengths_feedback_id_reference_not_found(self):
        d = _valid_self_analysis()
        d["strengths"][0]["feedback_ids"] = ["fb-999"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("参照整合" in e for e in result.errors))

    def test_values_evidence_episode_id_reference_not_found(self):
        d = _valid_self_analysis()
        d["values"][0]["evidence_episode_ids"] = ["ep-999"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("values[0]" in e for e in result.errors))

    def test_career_adaptability_evidence_episode_id_reference_not_found(self):
        d = _valid_self_analysis()
        d["career_adaptability"]["concern"]["evidence_episode_ids"] = ["ep-999"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("career_adaptability.concern" in e for e in result.errors)
        )

    def test_career_narrative_not_object(self):
        d = _valid_self_analysis()
        d["career_narrative"] = "文字列"
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("career_narrative" in e for e in result.errors))

    def test_career_narrative_missing_life_theme(self):
        d = _valid_self_analysis()
        del d["career_narrative"]["life_theme"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("life_theme" in e for e in result.errors))

    def test_career_narrative_missing_consistent_motivation(self):
        d = _valid_self_analysis()
        d["career_narrative"]["consistent_motivation"] = ""
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("consistent_motivation" in e for e in result.errors))

    def test_reason_for_change_not_object(self):
        d = _valid_self_analysis()
        d["reason_for_change"] = "文字列"
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("reason_for_change" in e for e in result.errors))

    def test_reason_for_change_empty_raw_reasons(self):
        d = _valid_self_analysis()
        d["reason_for_change"]["raw_reasons"] = []
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("raw_reasons" in e for e in result.errors))

    def test_reason_for_change_missing_constructive_version(self):
        d = _valid_self_analysis()
        del d["reason_for_change"]["constructive_version"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("constructive_version" in e for e in result.errors))


class WarnCaseTest(unittest.TestCase):
    def test_no_others_feedback_warns_but_passes(self):
        d = _valid_self_analysis()
        d["others_feedback"] = []
        d["strengths"][0]["feedback_ids"] = []
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("others_feedback" in w for w in result.warnings))

    def test_no_metric_warns_but_passes(self):
        d = _valid_self_analysis()
        d["behavioral_episodes"][0]["metric"] = None
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("metric" in w for w in result.warnings))

    def test_missing_updated_at_warns(self):
        d = _valid_self_analysis()
        del d["updated_at"]
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("updated_at" in w for w in result.warnings))

    def test_empty_interests_warns(self):
        d = _valid_self_analysis()
        d["interests"] = {"domains": [], "concrete_topics": []}
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("interests" in w for w in result.warnings))

    def test_empty_values_warns(self):
        d = _valid_self_analysis()
        d["values"] = []
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("values" in w for w in result.warnings))

    def test_duplicate_episode_id_warns_but_passes(self):
        d = _valid_self_analysis()
        d["behavioral_episodes"].append(copy.deepcopy(d["behavioral_episodes"][0]))
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("behavioral_episodes[1].id" in w for w in result.warnings))

    def test_duplicate_feedback_id_warns_but_passes(self):
        d = _valid_self_analysis()
        d["others_feedback"].append(copy.deepcopy(d["others_feedback"][0]))
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("others_feedback[1].id" in w for w in result.warnings))

    def test_unknown_source_type_warns_but_passes(self):
        d = _valid_self_analysis()
        d["others_feedback"][0]["source_type"] = "取引先"
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("source_type" in w for w in result.warnings))

    def test_absent_source_type_does_not_warn(self):
        d = _valid_self_analysis()
        d["others_feedback"][0]["source_type"] = None
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertEqual(result.warnings, [])

    def test_constructive_version_same_as_raw_reasons_warns(self):
        d = _valid_self_analysis()
        d["reason_for_change"]["constructive_version"] = "裁量が小さい"
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(
            any("constructive_version" in w for w in result.warnings)
        )


class PersonalityErrorCaseTest(unittest.TestCase):
    def test_personality_not_object(self):
        d = _valid_self_analysis_v11()
        d["personality"] = "文字列"
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("personality" in e for e in result.errors))

    def test_markers_not_list(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"] = "文字列"
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("personality.markers" in e for e in result.errors))

    def test_markers_key_missing(self):
        d = _valid_self_analysis_v11()
        del d["personality"]["markers"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("personality.markers" in e for e in result.errors))

    def test_marker_not_object(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"] = ["文字列"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("personality.markers[0]" in e for e in result.errors))

    def test_marker_missing_id(self):
        d = _valid_self_analysis_v11()
        del d["personality"]["markers"][0]["id"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("personality.markers[0].id" in e for e in result.errors))

    def test_marker_duplicate_id_warns_but_passes(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"][1]["id"] = d["personality"]["markers"][0]["id"]
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("personality.markers[1].id" in w for w in result.warnings))

    def test_marker_unknown_construct(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"][0]["construct"] = "unknown_construct"
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("personality.markers[0].construct" in e for e in result.errors))

    def test_marker_missing_construct(self):
        d = _valid_self_analysis_v11()
        del d["personality"]["markers"][0]["construct"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(
            any(
                "personality.markers[0].construct" in e and "必須" in e
                for e in result.errors
            )
        )

    def test_marker_empty_response(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"][0]["response"] = ""
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("personality.markers[0].response" in e for e in result.errors))

    def test_marker_options_wrong_length(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"][0]["options"] = ["1件だけ"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("personality.markers[0].options" in e for e in result.errors))

    def test_marker_options_element_empty(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"][0]["options"] = ["段取りを先に固めてから動く", "  "]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("personality.markers[0].options" in e for e in result.errors))

    def test_marker_response_not_in_options(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"][0]["response"] = "選択肢にない回答"
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("personality.markers[0].response" in e for e in result.errors))

    def test_marker_unknown_episode_ref(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"][0]["linked_episode_ids"] = ["ep-999"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("personality.markers[0].linked_episode_ids" in e and "参照整合" in e for e in result.errors)
        )

    def test_marker_unknown_feedback_ref(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"][0]["feedback_ids"] = ["fb-999"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("personality.markers[0].feedback_ids" in e and "参照整合" in e for e in result.errors)
        )

    def test_presentation_not_string(self):
        d = _valid_self_analysis_v11()
        d["personality"]["presentation"] = 123
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("personality.presentation" in e for e in result.errors))


class PersonalityWarnCaseTest(unittest.TestCase):
    def test_marker_without_evidence_warns_but_passes(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"][0]["linked_episode_ids"] = []
        d["personality"]["markers"][0]["feedback_ids"] = []
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(
            any(
                "personality.markers[0]" in w and "自己申告だけの記録" in w
                for w in result.warnings
            )
        )

    def test_presentation_with_desu_type_label_warns(self):
        d = _valid_self_analysis_v11()
        d["personality"]["presentation"] = "計測してから動く慎重型です。"
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("personality.presentation" in w for w in result.warnings))

    def test_presentation_with_dearu_type_label_warns(self):
        d = _valid_self_analysis_v11()
        d["personality"]["presentation"] = "計測してから動く慎重タイプである。"
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("personality.presentation" in w for w in result.warnings))

    def test_presentation_with_possessive_type_does_not_warn(self):
        d = _valid_self_analysis_v11()
        d["personality"]["presentation"] = (
            "判断の型である decision_style の申告と、ep-1 の計測を先に置く行動が一致している。"
        )
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertEqual(result.warnings, [])

    def test_presentation_with_non_possessive_type_still_warns(self):
        d = _valid_self_analysis_v11()
        d["personality"]["presentation"] = "本人は慎重型である。"
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("personality.presentation" in w for w in result.warnings))

    def test_presentation_with_possessive_before_taipu_still_warns(self):
        """「〜のタイプです」は「の」の直後でも分類ラベルとして WARN する（「型」だけを除外対象にする）。"""
        d = _valid_self_analysis_v11()
        d["personality"]["presentation"] = "計画重視のタイプです。"
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("personality.presentation" in w for w in result.warnings))


class StrengthsConstructsTest(unittest.TestCase):
    def test_constructs_not_list(self):
        d = _valid_self_analysis_v11()
        d["strengths"][0]["constructs"] = "planning_style"
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("strengths[0].constructs" in e for e in result.errors))

    def test_unknown_construct_in_strengths(self):
        d = _valid_self_analysis_v11()
        d["strengths"][0]["constructs"] = ["unknown_construct"]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("strengths[0].constructs" in e for e in result.errors))

    def test_constructs_with_non_string_element_errors(self):
        d = _valid_self_analysis_v11()
        d["strengths"][0]["constructs"] = ["planning_style", 123]
        result = vsa.validate(d)
        self.assertFalse(result.ok)
        self.assertTrue(any("strengths[0].constructs" in e for e in result.errors))

    def test_construct_with_unlinked_marker_warns(self):
        d = _valid_self_analysis_v11()
        d["personality"]["markers"][1]["linked_episode_ids"] = []
        d["personality"]["markers"][1]["feedback_ids"] = []
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(
            any("strengths[0].constructs" in w and "decision_style" in w for w in result.warnings)
        )

    def test_construct_with_no_marker_does_not_warn(self):
        d = _valid_self_analysis_v11()
        d["strengths"][0]["constructs"] = ["planning_style", "collaboration_style"]
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertEqual(result.warnings, [])


class SchemaVersionCompatibilityTest(unittest.TestCase):
    def test_v10_document_without_personality_still_passes_without_new_warnings(self):
        result = vsa.validate(_valid_self_analysis())
        self.assertTrue(result.ok)
        self.assertEqual(result.warnings, [])

    def test_unknown_schema_version_warns_but_passes(self):
        d = _valid_self_analysis()
        d["schema_version"] = "9.9"
        result = vsa.validate(d)
        self.assertTrue(result.ok)
        self.assertTrue(any("schema_version" in w for w in result.warnings))


class CliTest(unittest.TestCase):
    def _write_tmp(self, obj) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def test_main_returns_0_on_valid(self):
        path = self._write_tmp(_valid_self_analysis())
        self.assertEqual(vsa.main([path]), 0)

    def test_main_returns_1_on_invalid(self):
        d = _valid_self_analysis()
        del d["schema_version"]
        path = self._write_tmp(d)
        self.assertEqual(vsa.main([path]), 1)

    def test_main_returns_1_on_broken_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{ not valid json ")
        self.addCleanup(os.remove, path)
        self.assertEqual(vsa.main([path]), 1)

    def test_main_json_flag_valid(self):
        path = self._write_tmp(_valid_self_analysis())
        self.assertEqual(vsa.main([path, "--json"]), 0)

    def test_main_returns_0_on_valid_with_bom(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8-sig") as f:
            json.dump(_valid_self_analysis(), f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        self.assertEqual(vsa.main([path]), 0)


class ResultShapeTest(unittest.TestCase):
    def test_to_dict_shape(self):
        result = vsa.validate(_valid_self_analysis())
        d = result.to_dict()
        self.assertEqual(d["status"], "PASS")
        self.assertEqual(d["error_count"], 0)
        self.assertIn("warnings", d)

    def test_immutability_of_input(self):
        for label, factory in (("1.0", _valid_self_analysis), ("1.1", _valid_self_analysis_v11)):
            with self.subTest(schema_version=label):
                d = factory()
                snapshot = copy.deepcopy(d)
                vsa.validate(d)
                self.assertEqual(d, snapshot)


class ExampleAssetTest(unittest.TestCase):
    def test_bundled_example_passes(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        document = vsa.load_self_analysis(
            os.path.join(base, "assets", "self_analysis_example.json")
        )
        result = vsa.validate(document)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


if __name__ == "__main__":
    unittest.main()
