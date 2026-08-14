"""calculate_company_score.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests -p "test_calculate_company_score*"
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import calculate_company_score as cs  # noqa: E402


def _metric(value, *, unit="円", grade="A", source_url="https://example.go.jp/ir") -> dict:
    """company_metrics の1項目を組み立てる。value が null の項目は出典も持たない。"""
    if value is None:
        return {"value": None, "unit": unit, "source_url": None, "grade": None, "as_of": None}
    return {
        "value": value,
        "unit": unit,
        "source_url": source_url,
        "grade": grade,
        "as_of": "2026-03",
    }


def _research(**metrics) -> dict:
    """company_research.json のうち、採点に使う company_metrics だけを持つ最小の文書を返す。"""
    return {
        "schema_version": "2.0",
        "company_name": "架空クラウドワークス",
        "company_metrics": dict(metrics),
    }


def _quantitative(axis: str, weight: int, thresholds: dict | None = None) -> dict:
    entry = {"axis": axis, "kind": "quantitative", "weight": weight}
    if thresholds is not None:
        entry["thresholds"] = thresholds
    return entry


def _qualitative(axis: str, weight: int, scores=(100, 50, 0)) -> dict:
    return {
        "axis": axis,
        "kind": "qualitative",
        "weight": weight,
        "label": "裁量の大きさ",
        "definition": "設計方針を自分で決められること",
        "judgment": [{"score": s, "condition": f"条件{s}"} for s in scores],
    }


def _profile(*axes) -> dict:
    return {"schema_version": "2.0", "company_score_axes": list(axes)}


def _axis_of(score: dict, axis: str) -> dict:
    return next(a for a in score["axes"] if a["axis"] == axis)


# 統計由来の既定基準を差し替える。DEFAULT_THRESHOLDS の実データに依存しない検査にする。
_SALARY_DEFAULT = {
    "p0": 4000000,
    "p100": 8000000,
    "unit": "円",
    "direction": "higher_is_better",
    "survey": "架空統計",
    "survey_year": 2025,
    "source_url": "https://example.go.jp/stat",
    "coverage": 90,
}
_OVERTIME_DEFAULT = {
    "p0": 45,
    "p100": 5,
    "unit": "時間",
    "direction": "lower_is_better",
    "survey": "架空統計",
    "survey_year": 2025,
    "source_url": "https://example.go.jp/stat",
    "coverage": 80,
}


class LinearMappingTest(unittest.TestCase):
    """実測値を 0〜100 点へ換算する線形式。原本は company-score-rubric.md。"""

    def test_value_at_zero_threshold_is_0(self):
        self.assertEqual(cs.score_from_value(4500000, 4500000, 7000000), 0)

    def test_value_at_full_threshold_is_100(self):
        self.assertEqual(cs.score_from_value(7000000, 4500000, 7000000), 100)

    def test_midpoint_is_50(self):
        self.assertEqual(cs.score_from_value(5750000, 4500000, 7000000), 50)

    def test_value_below_range_is_clipped_to_0(self):
        self.assertEqual(cs.score_from_value(3000000, 4500000, 7000000), 0)

    def test_value_above_range_is_clipped_to_100(self):
        self.assertEqual(cs.score_from_value(9000000, 4500000, 7000000), 100)

    def test_result_is_rounded_half_up(self):
        # 100 × (101 − 0) ÷ (200 − 0) = 50.5。四捨五入して 51 とする。
        self.assertEqual(cs.score_from_value(101, 0, 200), 51)

    def test_equal_thresholds_raise(self):
        with self.assertRaises(cs.CalcError):
            cs.score_from_value(100, 200, 200)


class LowerIsBetterTest(unittest.TestCase):
    """p0 > p100 の軸（残業時間など）は、値が小さいほど点数が高い。"""

    def test_small_value_scores_higher_than_large_value(self):
        low = cs.score_from_value(10, 45, 5)
        high = cs.score_from_value(40, 45, 5)
        self.assertGreater(low, high)

    def test_ends_and_midpoint(self):
        self.assertEqual(cs.score_from_value(45, 45, 5), 0)
        self.assertEqual(cs.score_from_value(5, 45, 5), 100)
        self.assertEqual(cs.score_from_value(25, 45, 5), 50)

    def test_value_below_full_threshold_is_clipped_to_100(self):
        self.assertEqual(cs.score_from_value(0, 45, 5), 100)

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"monthly_overtime": _OVERTIME_DEFAULT}, clear=True)
    def test_overtime_axis_uses_the_default_direction(self):
        score = cs.build_company_score(
            _research(monthly_overtime=_metric(15, unit="時間")),
            _profile(_quantitative("monthly_overtime", 100)),
        )
        self.assertEqual(_axis_of(score, "monthly_overtime")["score"], 75)


class ThresholdSourceTest(unittest.TestCase):
    """基準は利用者の申告を既定より優先し、どちらも無ければ判定できない。"""

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True)
    def test_user_thresholds_take_precedence_over_the_default(self):
        score = cs.build_company_score(
            _research(compensation_level=_metric(6000000)),
            _profile(
                _quantitative("compensation_level", 100, {"zero": 4500000, "full": 7000000})
            ),
        )
        axis = _axis_of(score, "compensation_level")
        self.assertEqual(axis["threshold_source"], "user")
        self.assertEqual(axis["thresholds"], {"zero": 4500000, "full": 7000000})
        self.assertEqual(axis["score"], 60)

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True)
    def test_default_thresholds_apply_without_a_user_declaration(self):
        score = cs.build_company_score(
            _research(compensation_level=_metric(6000000)),
            _profile(_quantitative("compensation_level", 100)),
        )
        axis = _axis_of(score, "compensation_level")
        self.assertEqual(axis["threshold_source"], "statistic")
        self.assertEqual(axis["thresholds"], {"zero": 4000000, "full": 8000000})
        self.assertEqual(axis["score"], 50)

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {}, clear=True)
    def test_axis_without_any_threshold_is_not_judged(self):
        score = cs.build_company_score(
            _research(annual_holidays=_metric(125, unit="日")),
            _profile(_quantitative("annual_holidays", 100)),
        )
        axis = _axis_of(score, "annual_holidays")
        self.assertIsNone(axis["score"])
        self.assertIsNone(axis["threshold_source"])
        self.assertIsNone(axis["thresholds"])
        self.assertIn("基準", axis["reason"])
        self.assertIsNone(score["total"])

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {}, clear=True)
    def test_user_thresholds_alone_make_an_axis_judgeable(self):
        score = cs.build_company_score(
            _research(annual_holidays=_metric(125, unit="日")),
            _profile(_quantitative("annual_holidays", 100, {"zero": 105, "full": 125})),
        )
        self.assertEqual(_axis_of(score, "annual_holidays")["score"], 100)

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {}, clear=True)
    def test_equal_user_thresholds_raise(self):
        with self.assertRaises(cs.CalcError):
            cs.build_company_score(
                _research(annual_holidays=_metric(125, unit="日")),
                _profile(_quantitative("annual_holidays", 100, {"zero": 120, "full": 120})),
            )


class MissingValueTest(unittest.TestCase):
    """実測値が無い軸は 0 点にせず、判定できない扱いにする。"""

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True)
    def test_null_value_is_not_scored_as_zero(self):
        score = cs.build_company_score(
            _research(compensation_level=_metric(None)),
            _profile(_quantitative("compensation_level", 100)),
        )
        axis = _axis_of(score, "compensation_level")
        self.assertIsNone(axis["score"])
        self.assertIn("実測値", axis["reason"])

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True)
    def test_missing_metric_entry_is_not_judged(self):
        score = cs.build_company_score(
            _research(), _profile(_quantitative("compensation_level", 100))
        )
        self.assertIsNone(_axis_of(score, "compensation_level")["score"])
        self.assertEqual(score["coverage"], 0)

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True)
    def test_non_numeric_value_is_not_judged(self):
        research = _research(compensation_level=_metric("600万円"))
        score = cs.build_company_score(
            research, _profile(_quantitative("compensation_level", 100))
        )
        self.assertIsNone(_axis_of(score, "compensation_level")["score"])


class QualitativeTest(unittest.TestCase):
    """定性軸は、fit-assessor が判定した matched_score をそのまま点数にする。"""

    def test_matched_score_becomes_the_axis_score(self):
        score = cs.build_company_score(
            _research(),
            _profile(_qualitative("tech_discretion", 100)),
            {"tech_discretion": {"matched_score": 50, "evidence": "求人票の記載に合致"}},
        )
        axis = _axis_of(score, "tech_discretion")
        self.assertEqual(axis["score"], 50)
        self.assertEqual(axis["evidence"], "求人票の記載に合致")
        self.assertIsNone(axis["value"])
        self.assertIsNone(axis["thresholds"])
        self.assertIsNone(axis["threshold_source"])

    def test_axis_without_a_judgement_is_not_judged(self):
        score = cs.build_company_score(
            _research(), _profile(_qualitative("tech_discretion", 100)), {}
        )
        axis = _axis_of(score, "tech_discretion")
        self.assertIsNone(axis["score"])
        self.assertIn("判定結果", axis["reason"])

    def test_null_matched_score_is_not_judged(self):
        score = cs.build_company_score(
            _research(),
            _profile(_qualitative("tech_discretion", 100)),
            {"tech_discretion": {"matched_score": None, "evidence": "どの条件にも合致しない"}},
        )
        axis = _axis_of(score, "tech_discretion")
        self.assertIsNone(axis["score"])
        self.assertIn("合致", axis["reason"])

    def test_score_outside_the_judgement_raises(self):
        with self.assertRaises(cs.CalcError):
            cs.build_company_score(
                _research(),
                _profile(_qualitative("tech_discretion", 100)),
                {"tech_discretion": {"matched_score": 70, "evidence": "中間の点数"}},
            )

    def test_axis_without_judgment_conditions_raises(self):
        entry = _qualitative("tech_discretion", 100)
        del entry["judgment"]
        with self.assertRaises(cs.CalcError):
            cs.build_company_score(_research(), _profile(entry), {})


class TotalTest(unittest.TestCase):
    """総合点は判定できた軸だけの加重平均、coverage はその重みの合計である。"""

    @mock.patch.dict(
        cs.DEFAULT_THRESHOLDS,
        {"compensation_level": _SALARY_DEFAULT, "monthly_overtime": _OVERTIME_DEFAULT},
        clear=True,
    )
    def test_weighted_average_of_judged_axes(self):
        score = cs.build_company_score(
            _research(
                compensation_level=_metric(6000000),
                monthly_overtime=_metric(15, unit="時間"),
            ),
            _profile(
                _quantitative("compensation_level", 40),
                _quantitative("monthly_overtime", 60),
            ),
        )
        # 50点×40 + 75点×60 = 6500、重みの合計 100 で 65点。
        self.assertEqual(score["total"], 65)
        self.assertEqual(score["coverage"], 100)

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True)
    def test_unjudged_axis_is_excluded_from_the_average(self):
        score = cs.build_company_score(
            _research(compensation_level=_metric(6000000), annual_holidays=_metric(None)),
            _profile(
                _quantitative("compensation_level", 80),
                _quantitative("annual_holidays", 20),
            ),
        )
        self.assertEqual(score["total"], 50)
        self.assertEqual(score["coverage"], 80)

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {}, clear=True)
    def test_no_judged_axis_yields_null_total(self):
        score = cs.build_company_score(
            _research(), _profile(_quantitative("compensation_level", 100))
        )
        self.assertIsNone(score["total"])
        self.assertEqual(score["coverage"], 0)

    def test_no_declared_axis_yields_null_total(self):
        score = cs.build_company_score(_research(), {"schema_version": "2.0"})
        self.assertIsNone(score["total"])
        self.assertEqual(score["axes"], [])
        self.assertEqual(score["coverage"], 0)


class ProvisionalTest(unittest.TestCase):
    """coverage が COVERAGE_THRESHOLD を下回るとき暫定とする。"""

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True)
    def test_coverage_below_threshold_is_provisional(self):
        score = cs.build_company_score(
            _research(compensation_level=_metric(6000000)),
            _profile(
                _quantitative("compensation_level", 60),
                _quantitative("annual_holidays", 40),
            ),
        )
        self.assertEqual(score["coverage"], 60)
        self.assertTrue(score["provisional"])

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True)
    def test_coverage_at_threshold_is_not_provisional(self):
        score = cs.build_company_score(
            _research(compensation_level=_metric(6000000)),
            _profile(
                _quantitative("compensation_level", cs.COVERAGE_THRESHOLD),
                _quantitative("annual_holidays", 100 - cs.COVERAGE_THRESHOLD),
            ),
        )
        self.assertEqual(score["coverage"], cs.COVERAGE_THRESHOLD)
        self.assertFalse(score["provisional"])

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {}, clear=True)
    def test_null_total_is_provisional(self):
        score = cs.build_company_score(
            _research(), _profile(_quantitative("compensation_level", 100))
        )
        self.assertIsNone(score["total"])
        self.assertTrue(score["provisional"])


class RationaleTest(unittest.TestCase):
    """rationale は同じ入力から同じ文字列になる。"""

    def _score(self) -> dict:
        with mock.patch.dict(
            cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True
        ):
            return cs.build_company_score(
                _research(compensation_level=_metric(6000000), annual_holidays=_metric(None)),
                _profile(
                    _quantitative("compensation_level", 50),
                    _quantitative("annual_holidays", 20),
                    _qualitative("tech_discretion", 30),
                ),
                {"tech_discretion": {"matched_score": 100, "evidence": "面接で確認できた"}},
            )

    def test_same_input_yields_same_rationale(self):
        self.assertEqual(self._score()["rationale"], self._score()["rationale"])

    def test_rationale_names_the_judged_axes(self):
        rationale = self._score()["rationale"]
        self.assertIn("compensation_level", rationale)
        self.assertIn("tech_discretion", rationale)

    def test_rationale_names_the_unjudged_axis(self):
        self.assertIn("annual_holidays", self._score()["rationale"])

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True)
    def test_rationale_states_the_provisional_condition(self):
        score = cs.build_company_score(
            _research(compensation_level=_metric(6000000)),
            _profile(
                _quantitative("compensation_level", 40),
                _quantitative("annual_holidays", 60),
            ),
        )
        self.assertTrue(score["provisional"])
        self.assertIn("暫定", score["rationale"])

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {}, clear=True)
    def test_rationale_states_that_no_axis_was_judged(self):
        score = cs.build_company_score(
            _research(), _profile(_quantitative("compensation_level", 100))
        )
        self.assertIn("判定できた軸が1つも無い", score["rationale"])


class ShapeTest(unittest.TestCase):
    """出力の構造。軸は profile の申告順に並べる。"""

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True)
    def test_axes_keep_declared_order(self):
        score = cs.build_company_score(
            _research(compensation_level=_metric(6000000)),
            _profile(
                _qualitative("tech_discretion", 30),
                _quantitative("compensation_level", 70),
            ),
            {"tech_discretion": {"matched_score": 0, "evidence": "承認が要ると明記"}},
        )
        self.assertEqual(
            [a["axis"] for a in score["axes"]], ["tech_discretion", "compensation_level"]
        )

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True)
    def test_quantitative_axis_carries_the_source_of_the_measured_value(self):
        score = cs.build_company_score(
            _research(compensation_level=_metric(6000000)),
            _profile(_quantitative("compensation_level", 100)),
        )
        axis = _axis_of(score, "compensation_level")
        self.assertEqual(axis["value"], 6000000)
        self.assertEqual(axis["unit"], "円")
        self.assertEqual(axis["grade"], "A")
        self.assertEqual(axis["source_url"], "https://example.go.jp/ir")

    @mock.patch.dict(cs.DEFAULT_THRESHOLDS, {"compensation_level": _SALARY_DEFAULT}, clear=True)
    def test_output_keys(self):
        score = cs.build_company_score(
            _research(compensation_level=_metric(6000000)),
            _profile(_quantitative("compensation_level", 100)),
        )
        for key in ("total", "coverage", "provisional", "axes", "rationale"):
            self.assertIn(key, score)

    def test_output_is_json_serializable(self):
        score = cs.build_company_score(
            _research(), _profile(_qualitative("tech_discretion", 100)),
            {"tech_discretion": {"matched_score": 50, "evidence": "求人票の記載に合致"}},
        )
        json.dumps(score, ensure_ascii=False)


class ContradictionTest(unittest.TestCase):
    """入力の矛盾は CalcError を送出する。"""

    def test_company_score_axes_not_list_raises(self):
        with self.assertRaises(cs.CalcError):
            cs.build_company_score(_research(), {"company_score_axes": "compensation_level"})

    def test_unknown_kind_raises(self):
        with self.assertRaises(cs.CalcError):
            cs.build_company_score(
                _research(),
                _profile({"axis": "compensation_level", "kind": "numeric", "weight": 100}),
            )

    def test_weight_out_of_range_raises(self):
        with self.assertRaises(cs.CalcError):
            cs.build_company_score(
                _research(), _profile(_quantitative("compensation_level", 0))
            )

    def test_duplicated_axis_raises(self):
        with self.assertRaises(cs.CalcError):
            cs.build_company_score(
                _research(),
                _profile(
                    _quantitative("compensation_level", 50),
                    _quantitative("compensation_level", 50),
                ),
            )

    def test_profile_not_object_raises(self):
        with self.assertRaises(cs.CalcError):
            cs.build_company_score(_research(), ["compensation_level"])

    def test_research_not_object_raises(self):
        with self.assertRaises(cs.CalcError):
            cs.build_company_score([], _profile())


class CliTest(unittest.TestCase):
    def _write(self, obj: dict) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def _args(self) -> list:
        research = self._write(_research(compensation_level=_metric(6000000)))
        profile = self._write(
            _profile(
                _quantitative("compensation_level", 70, {"zero": 4000000, "full": 8000000}),
                _qualitative("tech_discretion", 30),
            )
        )
        qualitative = self._write(
            {"tech_discretion": {"matched_score": 100, "evidence": "面接で確認できた"}}
        )
        return [
            "--research", research,
            "--profile", profile,
            "--qualitative-json", qualitative,
        ]

    def test_main_returns_0(self):
        self.assertEqual(cs.main(self._args() + ["--json"]), 0)

    def test_main_out_writes_file_and_creates_parent(self):
        directory = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(directory, ignore_errors=True))
        out_path = os.path.join(directory, "nested", "company_score.json")
        self.assertEqual(cs.main(self._args() + ["--out", out_path]), 0)
        with open(out_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        self.assertEqual(data["total"], 65)
        self.assertEqual(data["coverage"], 100)
        self.assertFalse(data["provisional"])

    def test_main_runs_without_qualitative_json(self):
        research = self._write(_research(compensation_level=_metric(6000000)))
        profile = self._write(
            _profile(_quantitative("compensation_level", 100, {"zero": 4000000, "full": 8000000}))
        )
        self.assertEqual(cs.main(["--research", research, "--profile", profile, "--json"]), 0)

    def test_main_contradiction_exit_2(self):
        research = self._write(_research())
        profile = self._write(_profile(_qualitative("tech_discretion", 100)))
        qualitative = self._write({"tech_discretion": {"matched_score": 70, "evidence": "中間"}})
        self.assertEqual(
            cs.main([
                "--research", research, "--profile", profile,
                "--qualitative-json", qualitative,
            ]),
            2,
        )

    def test_main_unreadable_input_exit_2(self):
        research = self._write(_research())
        self.assertEqual(
            cs.main(["--research", research, "--profile", os.path.join(research, "no-such.json")]),
            2,
        )


if __name__ == "__main__":
    unittest.main()
