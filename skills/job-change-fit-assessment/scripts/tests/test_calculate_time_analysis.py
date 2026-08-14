"""calculate_time_analysis.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests -p "test_calculate*"
"""
from __future__ import annotations

import copy
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


class FormulaValueTest(unittest.TestCase):
    """定義式の数値検証（既知入力→期待値の手計算一致）。"""

    def test_analyze_matches_hand_calculation(self):
        a = ct.analyze(**_CLEAN_ARGS)
        # 月出勤日数 = (365-125)/12 = 20
        self.assertAlmostEqual(a.month_workdays, 20.0)
        # 日次残業 = 20 / 20 = 1.0
        self.assertAlmostEqual(a.daily_overtime_h, 1.0)
        # 1日拘束 = 8 + 1(休憩) + 1(残業) + 0.75*2(通勤) = 11.5
        self.assertAlmostEqual(a.daily_binding_hours, 11.5)
        # 有給取得 = 20 * 50% = 10
        self.assertAlmostEqual(a.paid_leave_taken_days, 10.0)
        # 実出勤日 = 365 - 125 - 10 = 230
        self.assertAlmostEqual(a.annual_working_days, 230.0)
        # 年間拘束 = 230 * 11.5 = 2645
        self.assertAlmostEqual(a.annual_binding_hours, 2645.0)
        # 年間労働 = 230 * (8 + 1) = 2070
        self.assertAlmostEqual(a.annual_labor_hours, 2070.0)

    def test_paid_leave_taken_override_used_directly(self):
        a = ct.analyze(**{**_CLEAN_ARGS, "paid_leave_taken": 5.0})
        # 取得実績5日を直接用いる。付与×取得率は無視する。
        self.assertAlmostEqual(a.paid_leave_taken_days, 5.0)
        self.assertAlmostEqual(a.annual_working_days, 365 - 125 - 5)

    def test_internal_calc_not_rounded(self):
        # 割り切れない入力で内部値が丸められていないことを確認する。
        a = ct.analyze(
            scheduled_hours=7.5, break_minutes=45, monthly_overtime_h=23,
            annual_holidays=120, paid_leave_rate=60, paid_leave_granted=17,
            commute_oneway_min=38,
        )
        month = (365 - 120) / 12
        self.assertAlmostEqual(a.daily_overtime_h, 23 / month)
        self.assertNotAlmostEqual(a.daily_overtime_h, round(23 / month, 1))


class EffectiveWageTest(unittest.TestCase):
    def test_wage_computed_when_salary_present(self):
        wage = ct.effective_hourly_wage(6900000, 2645.0, 2070.0)
        self.assertEqual(wage["binding_basis"], round(6900000 / 2645.0))
        self.assertEqual(wage["labor_basis"], round(6900000 / 2070.0))

    def test_wage_none_when_salary_absent(self):
        self.assertIsNone(ct.effective_hourly_wage(None, 2645.0, 2070.0))

    def test_build_wage_null_branch_without_salary(self):
        out = ct.build_time_analysis(dict(_CLEAN_ARGS))
        self.assertIsNone(out["effective_hourly_wage"])

    def test_build_wage_present_with_salary(self):
        out = ct.build_time_analysis({**_CLEAN_ARGS, "salary": 6900000})
        self.assertEqual(out["effective_hourly_wage"]["binding_basis"], 2609)
        self.assertEqual(out["effective_hourly_wage"]["labor_basis"], 3333)


class SensitivityTest(unittest.TestCase):
    def test_sensitivity_symmetry(self):
        s = ct.sensitivity(**_CLEAN_ARGS)
        self.assertAlmostEqual(s["overtime_plus10h"], -s["overtime_minus10h"])
        self.assertAlmostEqual(s["commute_plus15min"], -s["commute_minus15min"])

    def test_sensitivity_known_deltas(self):
        s = ct.sensitivity(**_CLEAN_ARGS)
        # 残業+10h/月 → 日次+0.5h → 年間 230*0.5 = 115
        self.assertAlmostEqual(s["overtime_plus10h"], 115.0)
        # 通勤+15分片道 → 往復+0.5h → 年間 230*0.5 = 115
        self.assertAlmostEqual(s["commute_plus15min"], 115.0)

    def test_sensitivity_independent_of_base(self):
        # 拘束時間の感度は基準の残業・通勤の水準に依存しない（線形）。
        s1 = ct.sensitivity(**_CLEAN_ARGS)
        s2 = ct.sensitivity(**{**_CLEAN_ARGS, "monthly_overtime_h": 45,
                               "commute_oneway_min": 80})
        self.assertAlmostEqual(s1["overtime_plus10h"], s2["overtime_plus10h"])
        self.assertAlmostEqual(s1["commute_plus15min"], s2["commute_plus15min"])


class ComparisonTest(unittest.TestCase):
    """現職（baseline）との突き合わせ。応募先の適合を単体で測らず、現職との差分を出す。"""

    def _baseline(self) -> dict:
        return {
            "annual": {"binding_hours": 2645.0, "labor_hours": 2070.0},
            "effective_hourly_wage": {"binding_basis": 2000, "labor_basis": 2500},
        }

    def _offer(self) -> dict:
        return {
            "annual": {"binding_hours": 2400.0, "labor_hours": 1900.0},
            "effective_hourly_wage": {"binding_basis": 2500, "labor_basis": 3000},
        }

    def test_delta_is_offer_minus_baseline(self):
        c = ct.build_comparison(self._offer(), self._baseline())
        self.assertAlmostEqual(c["delta"]["annual_binding_hours"], -245.0)
        self.assertAlmostEqual(c["delta"]["annual_labor_hours"], -170.0)
        self.assertEqual(c["delta"]["hourly_wage_binding_basis"], 500)
        self.assertEqual(c["delta"]["hourly_wage_labor_basis"], 500)

    def test_current_holds_baseline_values(self):
        c = ct.build_comparison(self._offer(), self._baseline())
        self.assertAlmostEqual(c["current"]["annual_binding_hours"], 2645.0)
        self.assertEqual(c["current"]["hourly_wage_binding_basis"], 2000)

    def test_missing_value_yields_null_delta(self):
        baseline = self._baseline()
        baseline["effective_hourly_wage"] = {"binding_basis": None, "labor_basis": None}
        c = ct.build_comparison(self._offer(), baseline)
        self.assertIsNone(c["delta"]["hourly_wage_binding_basis"])
        self.assertIsNone(c["current"]["hourly_wage_binding_basis"])
        # 時間の差分は算出できるため、実質時給の欠落に巻き込まれない。
        self.assertAlmostEqual(c["delta"]["annual_binding_hours"], -245.0)

    def test_missing_offer_side_nulls_current(self):
        offer = self._offer()
        offer["effective_hourly_wage"] = {"binding_basis": None, "labor_basis": None}
        c = ct.build_comparison(offer, self._baseline())
        self.assertIsNone(c["current"]["hourly_wage_binding_basis"])
        self.assertIsNone(c["delta"]["hourly_wage_binding_basis"])

    def test_absent_key_treated_as_missing(self):
        c = ct.build_comparison(self._offer(), {})
        self.assertIsNone(c["delta"]["annual_binding_hours"])
        self.assertIsNone(c["current"]["annual_binding_hours"])

    def test_comparison_absent_without_baseline(self):
        analysis = ct.build_time_analysis({"salary": 6000000}, {})
        self.assertNotIn("comparison", analysis)


class FallbackTest(unittest.TestCase):
    """フォールバック適用と fallbacks_used 記録。"""

    def test_all_survey_fallbacks_applied_when_omitted(self):
        # 通勤・残業・年間休日・有給率・付与のみフォールバック（所定・休憩は法定既定）。
        out = ct.build_time_analysis({})
        fields = {f["field"] for f in out["fallbacks_used"]}
        for key in ("monthly_overtime_h", "annual_holidays", "commute_oneway_min",
                    "paid_leave_rate", "paid_leave_granted",
                    "scheduled_hours", "break_minutes"):
            self.assertIn(key, fields)

    def test_survey_fallback_carries_year_and_gov_url(self):
        out = ct.build_time_analysis({})
        by_field = {f["field"]: f for f in out["fallbacks_used"]}
        entry = by_field["annual_holidays"]
        self.assertEqual(entry["value"], 116.6)
        self.assertEqual(entry["survey_year"], 2025)
        self.assertIn("mhlw.go.jp", entry["source_url"])

    def test_provided_value_not_fallbacked(self):
        out = ct.build_time_analysis({**_CLEAN_ARGS, "annual_holidays": 125})
        fields = {f["field"] for f in out["fallbacks_used"]}
        self.assertNotIn("annual_holidays", fields)

    def test_fallback_recorded_in_assumptions(self):
        out = ct.build_time_analysis({})
        joined = "\n".join(out["assumptions"])
        self.assertIn("就労条件総合調査", joined)
        self.assertIn("毎月勤労統計調査", joined)
        self.assertIn("社会生活基本調査", joined)

    def test_input_source_fallback_when_omitted(self):
        out = ct.build_time_analysis({})
        self.assertEqual(out["inputs"]["annual_holidays"]["source"], "fallback")
        self.assertIn("mhlw.go.jp", out["inputs"]["annual_holidays"]["source_url"])

    def test_input_source_from_sources_json(self):
        sources = {"annual_holidays": {"source": "posting",
                                       "source_url": "https://example.com/x",
                                       "grade": "A"}}
        out = ct.build_time_analysis({**_CLEAN_ARGS}, sources)
        self.assertEqual(out["inputs"]["annual_holidays"]["source"], "posting")
        self.assertEqual(out["inputs"]["annual_holidays"]["grade"], "A")


class FallbackConstantsTest(unittest.TestCase):
    """完了条件: FALLBACKS 全項目に官公庁ドメインの source_url と survey_year がある。"""

    def test_all_fallbacks_have_gov_url_and_year(self):
        for key, fb in ct.FALLBACKS.items():
            self.assertIsInstance(fb["survey_year"], int, key)
            url = fb["source_url"]
            self.assertTrue(
                url.startswith("https://") and
                any(d in url for d in ("mhlw.go.jp", "stat.go.jp", "e-stat.go.jp")),
                f"{key} の source_url が官公庁ドメインでない: {url}",
            )


class LeaveTakenBranchTest(unittest.TestCase):
    def test_taken_provided_excludes_rate_and_granted_from_inputs(self):
        out = ct.build_time_analysis({**_CLEAN_ARGS, "paid_leave_taken": 8})
        self.assertIn("paid_leave_taken", out["inputs"])
        self.assertNotIn("paid_leave_rate", out["inputs"])
        self.assertNotIn("paid_leave_granted", out["inputs"])

    def test_taken_derived_includes_rate_and_granted(self):
        out = ct.build_time_analysis(dict(_CLEAN_ARGS))
        self.assertIn("paid_leave_rate", out["inputs"])
        self.assertIn("paid_leave_granted", out["inputs"])
        self.assertNotIn("paid_leave_taken", out["inputs"])


class ContradictionTest(unittest.TestCase):
    """入力矛盾時のエラー。"""

    def test_holidays_over_365_raises(self):
        with self.assertRaises(ct.CalcError):
            ct.analyze(**{**_CLEAN_ARGS, "annual_holidays": 400})

    def test_holidays_365_raises(self):
        with self.assertRaises(ct.CalcError):
            ct.analyze(**{**_CLEAN_ARGS, "annual_holidays": 365})

    def test_paid_leave_rate_out_of_range_raises(self):
        with self.assertRaises(ct.CalcError):
            ct.analyze(**{**_CLEAN_ARGS, "paid_leave_rate": 150})

    def test_working_days_nonpositive_raises(self):
        with self.assertRaises(ct.CalcError):
            ct.analyze(**{**_CLEAN_ARGS, "annual_holidays": 360,
                          "paid_leave_taken": 10})


class CliTest(unittest.TestCase):
    def _args(self, **over) -> list[str]:
        base = {
            "--scheduled-hours": "8", "--break-minutes": "60",
            "--overtime-h-month": "20", "--annual-holidays": "125",
            "--paid-leave-rate": "50", "--paid-leave-granted": "20",
            "--commute-oneway-min": "45",
        }
        base.update(over)
        out = []
        for k, v in base.items():
            out.append(k)
            out.append(v)
        return out

    def test_main_returns_0(self):
        self.assertEqual(ct.main(self._args() + ["--json"]), 0)

    def test_main_contradiction_exit_2(self):
        self.assertEqual(ct.main(self._args(**{"--annual-holidays": "400"})), 2)

    def test_main_out_writes_file_and_creates_parent(self):
        d = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        out_path = os.path.join(d, "nested", "time_analysis.json")
        rc = ct.main(self._args() + ["--out", out_path])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        self.assertEqual(data["annual"]["binding_hours"], 2645.0)

    def test_main_no_args_uses_fallbacks_exit_0(self):
        self.assertEqual(ct.main(["--json"]), 0)

    def test_sources_json_bom_read(self):
        d = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        src_path = os.path.join(d, "sources.json")
        with open(src_path, "w", encoding="utf-8-sig") as f:
            json.dump({"annual_holidays": {"source": "posting",
                                           "source_url": "https://ex.com",
                                           "grade": "A"}}, f, ensure_ascii=False)
        rc = ct.main(self._args() + ["--sources-json", src_path, "--json"])
        self.assertEqual(rc, 0)


class ResultShapeTest(unittest.TestCase):
    def test_output_keys(self):
        out = ct.build_time_analysis({**_CLEAN_ARGS, "salary": 6900000})
        for key in ("inputs", "daily", "annual", "effective_hourly_wage",
                    "sensitivity", "assumptions", "fallbacks_used"):
            self.assertIn(key, out)
        for key in ("scheduled_hours", "break_h", "daily_overtime_h",
                    "commute_oneway_h", "binding_hours"):
            self.assertIn(key, out["daily"])
        for key in ("working_days", "paid_leave_taken_days", "binding_hours",
                    "labor_hours"):
            self.assertIn(key, out["annual"])
        for key in ("overtime_plus10h", "overtime_minus10h",
                    "commute_plus15min", "commute_minus15min"):
            self.assertIn(key, out["sensitivity"])

    def test_input_immutability(self):
        provided = {**_CLEAN_ARGS, "salary": 6900000}
        snapshot = copy.deepcopy(provided)
        ct.build_time_analysis(provided)
        self.assertEqual(provided, snapshot)

    def test_output_is_json_serializable(self):
        out = ct.build_time_analysis(dict(_CLEAN_ARGS))
        json.dumps(out, ensure_ascii=False)

    def test_days_and_yen_are_integers(self):
        out = ct.build_time_analysis({**_CLEAN_ARGS, "salary": 6900000})
        self.assertIsInstance(out["annual"]["working_days"], int)
        self.assertIsInstance(out["annual"]["paid_leave_taken_days"], int)
        self.assertIsInstance(out["effective_hourly_wage"]["binding_basis"], int)


class ExampleAssetTest(unittest.TestCase):
    """記入例 time_analysis_example.json が、現在の算定と一致することを確かめる。

    time_analysis.json には検証スクリプトが無いため、記入例の入力から組み立て直して突き合わせる。
    comparison は現職の time_analysis.json を材料に main が付ける項目なので、比較の対象外である。
    """

    def test_bundled_example_matches_recalculation(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base, "assets", "time_analysis_example.json")
        with open(path, encoding="utf-8") as f:
            example = json.load(f)

        # source が fallback の入力は、記入例を作ったときに未指定だったものである。同じ条件で作り直す。
        given = {
            key: meta for key, meta in example["inputs"].items() if meta["source"] != "fallback"
        }
        provided = {key: meta["value"] for key, meta in given.items()}
        sources = {
            key: {
                "source": meta["source"],
                "source_url": meta["source_url"],
                "grade": meta["grade"],
            }
            for key, meta in given.items()
        }

        rebuilt = ct.build_time_analysis(provided, sources)
        for key in rebuilt:
            with self.subTest(key=key):
                self.assertEqual(rebuilt[key], example[key])


if __name__ == "__main__":
    unittest.main()
