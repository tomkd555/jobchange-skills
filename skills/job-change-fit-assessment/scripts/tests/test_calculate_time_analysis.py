"""calculate_time_analysis.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests -p "test_calculate*"
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import calculate_time_analysis as ct  # noqa: E402


# 手計算が整数で閉じる既知入力（年間休日125→月20日、残業20h→日次1.0h）。
_CLEAN_ARGS = dict(
    scheduled_hours=8.0,
    break_minutes=60.0,
    monthly_overtime_h=20.0,
    annual_holidays=125.0,
    paid_leave_rate=50.0,
    paid_leave_granted=20.0,
    commute_oneway_min=45.0,
)


class AnalyzeTest(unittest.TestCase):
    def test_analyze_matches_hand_calculation(self):
        a = ct.analyze(**_CLEAN_ARGS)
        expected = {
            "month_workdays": 20.0,  # (365-125)/12
            "daily_overtime_h": 1.0,  # 20 / 20
            "daily_binding_hours": 11.5,  # 8 + 1(休憩) + 1(残業) + 0.75*2(通勤)
            "paid_leave_taken_days": 10.0,  # 20 * 50%
            "annual_working_days": 230.0,  # 365 - 125 - 10
            "annual_binding_hours": 2645.0,  # 230 * 11.5
            "annual_labor_hours": 2070.0,  # 230 * (8 + 1)
        }
        for name, value in expected.items():
            with self.subTest(name):
                self.assertAlmostEqual(getattr(a, name), value)

    def test_paid_leave_taken_overrides_rate_times_granted(self):
        a = ct.analyze(**{**_CLEAN_ARGS, "paid_leave_taken": 5.0})
        self.assertAlmostEqual(a.paid_leave_taken_days, 5.0)
        self.assertAlmostEqual(a.annual_working_days, 365 - 125 - 5)

    def test_contradictions_raise(self):
        rows = [
            ("年間休日が 365 超", {"annual_holidays": 400}),
            ("年間休日がちょうど 365", {"annual_holidays": 365}),
            ("有給取得率が 100 超", {"paid_leave_rate": 150}),
            ("実出勤日が 0 以下", {"annual_holidays": 360, "paid_leave_taken": 10}),
        ]
        for label, over in rows:
            with self.subTest(label), self.assertRaises(ct.CalcError):
                ct.analyze(**{**_CLEAN_ARGS, **over})


class WageAndSensitivityTest(unittest.TestCase):
    def test_effective_hourly_wage(self):
        self.assertEqual(ct.effective_hourly_wage(6900000, 2645.0, 2070.0), {"binding_basis": 2609, "labor_basis": 3333})
        self.assertIsNone(ct.effective_hourly_wage(None, 2645.0, 2070.0))

    def test_sensitivity_known_deltas_independent_of_base(self):
        # 残業+10h/月 → 日次+0.5h、通勤+15分片道 → 往復+0.5h。どちらも年間 230*0.5 = 115。
        for label, over in [("基準", {}), ("残業・通勤が大きい基準", {"monthly_overtime_h": 45, "commute_oneway_min": 80})]:
            with self.subTest(label):
                s = ct.sensitivity(**{**_CLEAN_ARGS, **over})
                if not over:
                    self.assertAlmostEqual(s["overtime_plus10h"], 115.0)
                    self.assertAlmostEqual(s["commute_plus15min"], 115.0)
                self.assertAlmostEqual(s["overtime_plus10h"], -s["overtime_minus10h"])
                self.assertAlmostEqual(s["commute_plus15min"], -s["commute_minus15min"])


class BuildTimeAnalysisTest(unittest.TestCase):
    def test_build_with_salary(self):
        out = ct.build_time_analysis({**_CLEAN_ARGS, "salary": 6900000})
        self.assertEqual(out["effective_hourly_wage"], {"binding_basis": 2609, "labor_basis": 3333})
        self.assertEqual(out["annual"]["binding_hours"], 2645.0)
        self.assertEqual(out["annual"]["working_days"], 230)
        self.assertIn("salary", out["inputs"])

    def test_build_without_salary_has_null_wage(self):
        out = ct.build_time_analysis(dict(_CLEAN_ARGS))
        self.assertIsNone(out["effective_hourly_wage"])
        self.assertNotIn("salary", out["inputs"])

    def test_omitted_inputs_use_fallbacks_and_record_them(self):
        out = ct.build_time_analysis({})
        by_field = {f["field"]: f for f in out["fallbacks_used"]}
        self.assertEqual(
            set(by_field),
            {"scheduled_hours", "break_minutes", "monthly_overtime_h", "annual_holidays",
             "commute_oneway_min", "paid_leave_rate", "paid_leave_granted"},
        )
        self.assertEqual(by_field["annual_holidays"]["value"], 116.6)
        self.assertEqual(by_field["scheduled_hours"]["value"], 8.0)  # 法定既定
        self.assertEqual(out["inputs"]["annual_holidays"]["source"], "fallback")
        self.assertIn("就労条件総合調査", "\n".join(out["assumptions"]))

    def test_provided_values_are_not_fallbacked_and_take_source_meta(self):
        sources = {"annual_holidays": {"source": "posting", "source_url": "https://example.com/x", "grade": "A"}}
        out = ct.build_time_analysis(dict(_CLEAN_ARGS), sources)
        self.assertEqual(out["fallbacks_used"], [])
        entry = out["inputs"]["annual_holidays"]
        self.assertEqual((entry["source"], entry["grade"]), ("posting", "A"))
        self.assertEqual(out["inputs"]["break_minutes"]["source"], "user")

    def test_leave_taken_branch_selects_inputs(self):
        taken = ct.build_time_analysis({**_CLEAN_ARGS, "paid_leave_taken": 8})["inputs"]
        derived = ct.build_time_analysis(dict(_CLEAN_ARGS))["inputs"]
        self.assertIn("paid_leave_taken", taken)
        self.assertNotIn("paid_leave_rate", taken)
        self.assertNotIn("paid_leave_granted", taken)
        self.assertNotIn("paid_leave_taken", derived)
        self.assertIn("paid_leave_rate", derived)

    def test_output_rounding_types(self):
        out = ct.build_time_analysis({**_CLEAN_ARGS, "salary": 6900000})
        self.assertIsInstance(out["annual"]["working_days"], int)
        self.assertIsInstance(out["effective_hourly_wage"]["binding_basis"], int)


class ComparisonTest(unittest.TestCase):
    """現職（baseline）との突き合わせ。delta は 応募先 − 現職。"""

    BASELINE = {
        "annual": {"binding_hours": 2645.0, "labor_hours": 2070.0},
        "effective_hourly_wage": {"binding_basis": 2000, "labor_basis": 2500},
    }
    OFFER = {
        "annual": {"binding_hours": 2400.0, "labor_hours": 1900.0},
        "effective_hourly_wage": {"binding_basis": 2500, "labor_basis": 3000},
    }

    def test_delta_and_current(self):
        c = ct.build_comparison(self.OFFER, self.BASELINE)
        self.assertEqual(c["delta"], {
            "annual_binding_hours": -245.0, "annual_labor_hours": -170.0,
            "hourly_wage_binding_basis": 500, "hourly_wage_labor_basis": 500,
        })
        self.assertEqual(c["current"]["annual_binding_hours"], 2645.0)
        self.assertEqual(c["current"]["hourly_wage_binding_basis"], 2000)

    def test_missing_side_nulls_only_that_item(self):
        null_wage = {"effective_hourly_wage": {"binding_basis": None, "labor_basis": None}}
        rows = [
            ("現職側の時給が null", self.OFFER, {**self.BASELINE, **null_wage}),
            ("応募先側の時給が null", {**self.OFFER, **null_wage}, self.BASELINE),
        ]
        for label, offer, baseline in rows:
            with self.subTest(label):
                c = ct.build_comparison(offer, baseline)
                self.assertIsNone(c["delta"]["hourly_wage_binding_basis"])
                self.assertIsNone(c["current"]["hourly_wage_binding_basis"])
                self.assertEqual(c["delta"]["annual_binding_hours"], -245.0)

    def test_empty_baseline_yields_all_null(self):
        c = ct.build_comparison(self.OFFER, {})
        self.assertTrue(all(v is None for v in c["delta"].values()))


class CliTest(unittest.TestCase):
    def _args(self, **over) -> list[str]:
        base = {
            "--scheduled-hours": "8", "--break-minutes": "60", "--overtime-h-month": "20",
            "--annual-holidays": "125", "--paid-leave-rate": "50", "--paid-leave-granted": "20",
            "--commute-oneway-min": "45",
        }
        base.update(over)
        return [x for kv in base.items() for x in kv]

    def _write(self, obj) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8-sig") as f:
            f.write(obj) if isinstance(obj, str) else json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def _run(self, argv):
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            code = ct.main(argv)
        return code, out.getvalue()

    def test_exit_codes(self):
        sources = self._write({"annual_holidays": {"source": "posting", "source_url": "https://ex.com", "grade": "A"}})
        rows = [
            ("valid", self._args(), 0),
            ("引数なし（全てフォールバック）", [], 0),
            ("入力の矛盾", self._args(**{"--annual-holidays": "400"}), 2),
            ("sources-json（BOM 付き）", self._args() + ["--sources-json", sources], 0),
            ("sources-json が壊れている", self._args() + ["--sources-json", self._write("{")], 2),
            ("baseline-json が壊れている", self._args() + ["--baseline-json", self._write("{")], 2),
            ("baseline-json が存在しない", self._args() + ["--baseline-json", os.path.join(tempfile.gettempdir(), "no-such.json")], 2),
        ]
        for label, argv, code in rows:
            with self.subTest(label):
                self.assertEqual(self._run(argv)[0], code)

    def test_json_output_keys_and_baseline_comparison(self):
        baseline = self._write({"annual": {"binding_hours": 2745.0, "labor_hours": 2070.0}})
        code, out = self._run(self._args(**{"--salary": "6900000"}) + ["--baseline-json", baseline, "--json"])
        data = json.loads(out)
        self.assertEqual(
            set(data),
            {"inputs", "daily", "annual", "effective_hourly_wage", "sensitivity",
             "assumptions", "fallbacks_used", "comparison"},
        )
        self.assertEqual(data["comparison"]["delta"]["annual_binding_hours"], -100.0)  # 2645 - 2745

    def test_out_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as d:
            out_path = os.path.join(d, "nested", "time_analysis.json")
            self.assertEqual(self._run(self._args() + ["--out", out_path])[0], 0)
            with open(out_path, "r", encoding="utf-8-sig") as f:
                self.assertEqual(json.load(f)["annual"]["binding_hours"], 2645.0)


class ExampleAssetTest(unittest.TestCase):
    """記入例 time_analysis_example.json が、現在の算定と一致する。

    time_analysis.json には検証スクリプトが無いため、記入例の入力から組み立て直して突き合わせる。
    comparison は main が現職の time_analysis.json から付ける項目なので、比較の対象外である。
    """

    def test_bundled_example_matches_recalculation(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(base, "assets", "time_analysis_example.json"), encoding="utf-8") as f:
            example = json.load(f)

        # source が fallback の入力は、記入例を作ったときに未指定だったものである。同じ条件で作り直す。
        given = {k: m for k, m in example["inputs"].items() if m["source"] != "fallback"}
        provided = {k: m["value"] for k, m in given.items()}
        sources = {k: {f: m[f] for f in ("source", "source_url", "grade")} for k, m in given.items()}

        rebuilt = ct.build_time_analysis(provided, sources)
        for key in rebuilt:
            with self.subTest(key=key):
                self.assertEqual(rebuilt[key], example[key])


if __name__ == "__main__":
    unittest.main()
