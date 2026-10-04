"""calculate_company_score.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests -p "test_calculate_company_score*"
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import calculate_company_score as cs  # noqa: E402


def _metric(value, *, unit="円") -> dict:
    """company_metrics の1項目。value が null の項目は出典も持たない。"""
    if value is None:
        return {"value": None, "unit": unit, "source_url": None, "grade": None, "as_of": None}
    return {"value": value, "unit": unit, "source_url": "https://example.go.jp/ir", "grade": "A", "as_of": "2026-03"}


def _research(**metrics) -> dict:
    return {"schema_version": "2.0", "company_name": "架空クラウドワークス", "company_metrics": dict(metrics)}


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
        "judgment": [{"score": s, "condition": f"条件{s}"} for s in scores],
    }


def _profile(*axes) -> dict:
    return {"schema_version": "2.0", "company_score_axes": list(axes)}


def _axis_of(score: dict, axis: str) -> dict:
    return next(a for a in score["axes"] if a["axis"] == axis)


# 統計由来の既定基準を差し替え、DEFAULT_THRESHOLDS の実データに依存しない検査にする。
_SALARY_DEFAULT = {"p0": 4000000, "p100": 8000000, "unit": "円"}
_OVERTIME_DEFAULT = {"p0": 45, "p100": 5, "unit": "時間"}
_DEFAULTS = {"compensation_level": _SALARY_DEFAULT, "monthly_overtime": _OVERTIME_DEFAULT}


class ScoreFromValueTest(unittest.TestCase):
    """score = 100 × (value − zero) ÷ (full − zero) を 0〜100 でクリップし、四捨五入する。"""

    def test_mapping_rows(self):
        rows = [
            ("zero は 0 点", (4500000, 4500000, 7000000), 0),
            ("full は 100 点", (7000000, 4500000, 7000000), 100),
            ("中間は 50 点", (5750000, 4500000, 7000000), 50),
            ("下限を下回れば 0 点", (3000000, 4500000, 7000000), 0),
            ("上限を上回れば 100 点", (9000000, 4500000, 7000000), 100),
            ("50.5 は切り上げて 51", (101, 0, 200), 51),
            ("小さいほど良い軸: zero", (45, 45, 5), 0),
            ("小さいほど良い軸: full", (5, 45, 5), 100),
            ("小さいほど良い軸: 中間", (25, 45, 5), 50),
            ("小さいほど良い軸: full より小さい値", (0, 45, 5), 100),
        ]
        for label, args, expected in rows:
            with self.subTest(label):
                self.assertEqual(cs.score_from_value(*args), expected)

    def test_equal_thresholds_raise(self):
        with self.assertRaises(cs.CalcError):
            cs.score_from_value(100, 200, 200)


@mock.patch.dict(cs.DEFAULT_THRESHOLDS, _DEFAULTS, clear=True)
class QuantitativeAxisTest(unittest.TestCase):
    def _score(self, metrics: dict, *axes):
        return cs.build_company_score(_research(**metrics), _profile(*axes))

    def test_user_thresholds_take_precedence_over_the_default(self):
        score = self._score(
            {"compensation_level": _metric(6000000)},
            _quantitative("compensation_level", 100, {"zero": 4500000, "full": 7000000}),
        )
        axis = _axis_of(score, "compensation_level")
        self.assertEqual((axis["threshold_source"], axis["score"]), ("user", 60))

    def test_default_thresholds_apply_without_a_user_declaration(self):
        score = self._score({"compensation_level": _metric(6000000)}, _quantitative("compensation_level", 100))
        axis = _axis_of(score, "compensation_level")
        self.assertEqual((axis["threshold_source"], axis["score"]), ("statistic", 50))
        self.assertEqual(axis["thresholds"], {"zero": 4000000, "full": 8000000})

    def test_lower_is_better_default_direction(self):
        score = self._score({"monthly_overtime": _metric(15, unit="時間")}, _quantitative("monthly_overtime", 100))
        self.assertEqual(_axis_of(score, "monthly_overtime")["score"], 75)

    def test_user_thresholds_make_an_axis_without_default_judgeable(self):
        score = self._score(
            {"annual_holidays": _metric(125, unit="日")},
            _quantitative("annual_holidays", 100, {"zero": 105, "full": 125}),
        )
        self.assertEqual(_axis_of(score, "annual_holidays")["score"], 100)

    def test_unjudged_axes_have_no_score_and_a_reason(self):
        rows = [
            ("基準がどこにも無い", {"annual_holidays": _metric(125, unit="日")}, "annual_holidays", "基準"),
            ("実測値が null", {"compensation_level": _metric(None)}, "compensation_level", "実測値"),
            ("metrics に項目が無い", {}, "compensation_level", "実測値"),
            ("実測値が数値でない", {"compensation_level": _metric("600万円")}, "compensation_level", "実測値"),
        ]
        for label, metrics, axis, reason in rows:
            with self.subTest(label):
                score = self._score(metrics, _quantitative(axis, 100))
                self.assertIsNone(_axis_of(score, axis)["score"])
                self.assertIn(reason, _axis_of(score, axis)["reason"])
                self.assertIsNone(score["total"])
                self.assertEqual(score["coverage"], 0)

    def test_equal_user_thresholds_raise(self):
        with self.assertRaises(cs.CalcError):
            self._score(
                {"annual_holidays": _metric(125, unit="日")},
                _quantitative("annual_holidays", 100, {"zero": 120, "full": 120}),
            )


class QualitativeAxisTest(unittest.TestCase):
    def _score(self, judged, entry=None):
        return cs.build_company_score(_research(), _profile(entry or _qualitative("tech", 100)), judged)

    def test_matched_score_becomes_the_axis_score(self):
        axis = _axis_of(self._score({"tech": {"matched_score": 50, "evidence": "求人票に合致"}}), "tech")
        self.assertEqual((axis["score"], axis["evidence"]), (50, "求人票に合致"))

    def test_unjudged_cases(self):
        rows = [
            ("判定結果が渡されていない", {}, "判定結果"),
            ("matched_score が null", {"tech": {"matched_score": None, "evidence": "合致なし"}}, "合致"),
        ]
        for label, judged, reason in rows:
            with self.subTest(label):
                axis = _axis_of(self._score(judged), "tech")
                self.assertIsNone(axis["score"])
                self.assertIn(reason, axis["reason"])

    def test_contradictions_raise(self):
        no_judgment = _qualitative("tech", 100)
        del no_judgment["judgment"]
        rows = [
            ("score が判定条件に無い", {"tech": {"matched_score": 70}}, None),
            ("judgment が無い", {}, no_judgment),
        ]
        for label, judged, entry in rows:
            with self.subTest(label), self.assertRaises(cs.CalcError):
                self._score(judged, entry)


@mock.patch.dict(cs.DEFAULT_THRESHOLDS, _DEFAULTS, clear=True)
class TotalTest(unittest.TestCase):
    def test_weighted_average_and_axis_order(self):
        score = cs.build_company_score(
            _research(compensation_level=_metric(6000000), monthly_overtime=_metric(15, unit="時間")),
            _profile(_quantitative("monthly_overtime", 60), _quantitative("compensation_level", 40)),
        )
        # 75点×60 + 50点×40 = 6500、重みの合計 100 で 65点。軸は申告順に並ぶ。
        self.assertEqual((score["total"], score["coverage"], score["provisional"]), (65, 100, False))
        self.assertEqual([a["axis"] for a in score["axes"]], ["monthly_overtime", "compensation_level"])

    def test_unjudged_axis_is_excluded_from_the_average(self):
        score = cs.build_company_score(
            _research(compensation_level=_metric(6000000), annual_holidays=_metric(None)),
            _profile(_quantitative("compensation_level", 80), _quantitative("annual_holidays", 20)),
        )
        self.assertEqual((score["total"], score["coverage"]), (50, 80))

    def test_provisional_boundary(self):
        # coverage が COVERAGE_THRESHOLD 未満なら暫定、ちょうどなら確定。
        for label, weight, provisional in [
            ("未満", cs.COVERAGE_THRESHOLD - 1, True),
            ("ちょうど", cs.COVERAGE_THRESHOLD, False),
        ]:
            with self.subTest(label):
                score = cs.build_company_score(
                    _research(compensation_level=_metric(6000000)),
                    _profile(_quantitative("compensation_level", weight), _quantitative("annual_holidays", 1)),
                )
                self.assertEqual(score["coverage"], weight)
                self.assertEqual(score["provisional"], provisional)

    def test_nothing_judged_yields_null_total_and_provisional(self):
        rows = [
            ("軸の申告なし", {"schema_version": "2.0"}),
            ("全軸が判定不能", _profile(_quantitative("compensation_level", 100))),
        ]
        for label, profile in rows:
            with self.subTest(label):
                score = cs.build_company_score(_research(), profile)
                self.assertIsNone(score["total"])
                self.assertTrue(score["provisional"])
        self.assertIn("判定できた軸が1つも無い", score["rationale"])

    def test_rationale_names_axes_and_provisional(self):
        with mock.patch.dict(cs.DEFAULT_THRESHOLDS, _DEFAULTS, clear=True):
            score = cs.build_company_score(
                _research(compensation_level=_metric(6000000), annual_holidays=_metric(None)),
                _profile(
                    _quantitative("compensation_level", 40),
                    _quantitative("annual_holidays", 30),
                    _qualitative("tech_discretion", 30),
                ),
                {"tech_discretion": {"matched_score": 100, "evidence": "面接で確認"}},
            )
        for word in ("compensation_level", "tech_discretion", "annual_holidays"):
            self.assertIn(word, score["rationale"])
        # coverage 70 は閾値ちょうどなので暫定の文は含まない。
        self.assertNotIn("暫定", score["rationale"])
        self.assertEqual(score["total"], 71)  # (50×40 + 100×30) ÷ 70 = 71.4


class ContradictionTest(unittest.TestCase):
    def test_contradictions_raise(self):
        axis = lambda **kw: _profile({"axis": "a", "kind": "quantitative", "weight": 10, **kw})  # noqa: E731
        rows = [
            ("company_score_axes が配列でない", _research(), {"company_score_axes": "a"}),
            ("kind が未知", _research(), axis(kind="numeric")),
            ("weight が範囲外", _research(), axis(weight=0)),
            ("軸が重複", _research(), _profile(_quantitative("a", 50), _quantitative("a", 50))),
            ("axis がオブジェクトでない", _research(), ["a"]),
            ("職歴だけの 3.0", _research(), {"schema_version": "3.0"}),
            ("research がオブジェクトでない", [], _profile()),
        ]
        for label, research, profile in rows:
            with self.subTest(label), self.assertRaises(cs.CalcError):
                cs.build_company_score(research, profile)


class CliTest(unittest.TestCase):
    def _write(self, obj) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(obj) if isinstance(obj, str) else json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def _run(self, argv):
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            code = cs.main(argv)
        return code, out.getvalue()

    def test_exit_codes_and_json_output(self):
        research = self._write(_research(compensation_level=_metric(6000000)))
        axis = self._write(
            _profile(
                _quantitative("compensation_level", 70, {"zero": 4000000, "full": 8000000}),
                _qualitative("tech_discretion", 30),
            )
        )
        judged = self._write({"tech_discretion": {"matched_score": 100, "evidence": "確認済み"}})
        bad_judged = self._write({"tech_discretion": {"matched_score": 70}})
        rows = [
            ("valid (--axis)", ["--research", research, "--axis", axis, "--qualitative-json", judged], 0),
            ("valid (--profile alias)", ["--research", research, "--profile", axis, "--qualitative-json", judged], 0),
            ("入力の矛盾", ["--research", research, "--axis", axis, "--qualitative-json", bad_judged], 2),
            ("読めない入力", ["--research", research, "--axis", self._write("{")], 2),
            ("存在しない入力", ["--research", os.path.join(tempfile.gettempdir(), "no-such.json"), "--axis", axis], 2),
            ("職歴だけの 3.0", ["--research", research, "--axis", self._write({"schema_version": "3.0"})], 2),
        ]
        for label, argv, code in rows:
            with self.subTest(label):
                self.assertEqual(self._run(argv)[0], code)

        code, out = self._run(["--research", research, "--axis", axis, "--qualitative-json", judged, "--json"])
        data = json.loads(out)
        self.assertEqual(set(data), {"total", "coverage", "provisional", "axes", "rationale"})
        self.assertEqual((data["total"], data["coverage"]), (65, 100))  # (50×70 + 100×30) ÷ 100

    def test_out_creates_parent_directory(self):
        research = self._write(_research(compensation_level=_metric(6000000)))
        axis = self._write(_profile(_quantitative("compensation_level", 100, {"zero": 4000000, "full": 8000000})))
        with tempfile.TemporaryDirectory() as directory:
            out_path = os.path.join(directory, "nested", "company_score.json")
            self.assertEqual(self._run(["--research", research, "--axis", axis, "--out", out_path])[0], 0)
            with open(out_path, "r", encoding="utf-8-sig") as f:
                self.assertEqual(json.load(f)["total"], 50)


if __name__ == "__main__":
    unittest.main()
