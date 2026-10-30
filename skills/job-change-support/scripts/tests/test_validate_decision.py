"""validate_decision.py の単体テスト。"""
import copy
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import validate_decision as vd  # noqa: E402
from field_catalog import load_catalog  # noqa: E402

A = "S_アクメクラウド-20261025-01"
B = "B_ベータシステムズ-20261028-01"

WISHES = {"conditions": [
    {"id": "c001", "level": "must"},
    {"id": "c003", "level": "want"},
]}


def raw():
    """派生項目を持たない入力だけの記録。B が 3 基準中 2 基準で上回る。"""
    return {
        "schema_version": "1.0",
        "id": "20261115-infra-2sha",
        "date": "2026-11-15",
        "subject": "インフラ職 2 社の比較",
        "candidates": [
            {"posting_id": A, "company_slug": "S_アクメクラウド", "label": "A"},
            {"posting_id": B, "company_slug": "B_ベータシステムズ", "label": "B"},
        ],
        "criteria": [
            {"id": "k01", "field_id": "salary_min", "condition_id": "c001", "direction": "higher",
             "values": {A: 6500000, B: 7000000}, "ratings": None},
            {"id": "k02", "field_id": "monthly_overtime_h", "condition_id": None, "direction": "lower",
             "values": {A: 25, B: 20}, "ratings": None},
            {"id": "k03", "field_id": "custom", "condition_id": "c003", "direction": "higher",
             "values": None, "ratings": {A: 4, B: 2}},
        ],
        "swing_order": ["k01", "k03", "k02"],
        "swing_points": {"k01": 100, "k03": 60, "k02": 40},
        "chosen": B,
        "decisive_fields": ["k01"],
        "compromised_fields": ["k03"],
        "follow_up": [
            {"at": "3m", "date": None, "satisfaction": None, "notes": {}},
            {"at": "1y", "date": None, "satisfaction": None, "notes": {}},
        ],
    }


def good():
    return vd.fill(raw(), None)


def check(d, wishes=WISHES):
    return vd.validate(d, wishes)


def has(msgs, text):
    return any(text in m for m in msgs)


class VocabularySyncTest(unittest.TestCase):
    """検証スクリプトの定数が辞書の列挙値と一致すること。"""

    def test_rank_methods_match_catalog(self):
        catalog = load_catalog()
        self.assertEqual(vd._RANK_METHODS, catalog.enum_values("weight_method"))

    def test_follow_up_at_match_catalog(self):
        catalog = load_catalog()
        self.assertEqual(tuple(vd._FOLLOW_UP_AT), catalog.enum_values("follow_up_at"))


class PureFunctionTest(unittest.TestCase):
    def test_scale_values_direction_higher_lower(self):
        self.assertEqual(vd.scale_values({"a": 10, "b": 20, "c": 15}, "higher"), {"a": 0.0, "b": 1.0, "c": 0.5})
        self.assertEqual(vd.scale_values({"a": 10, "b": 20}, "lower"), {"a": 1.0, "b": 0.0})

    def test_scale_values_null_value_returns_none(self):
        self.assertEqual(vd.scale_values({"a": 10, "b": None}, "higher"), {"a": 1.0, "b": None})

    def test_scale_values_all_equal_returns_one(self):
        self.assertEqual(vd.scale_values({"a": 5, "b": 5}, "lower"), {"a": 1.0, "b": 1.0})

    def test_scale_values_all_null_returns_none(self):
        self.assertEqual(vd.scale_values({"a": None}, "higher"), {"a": None})

    def test_scale_ratings_one_three_five_returns_unit_scale(self):
        self.assertEqual(vd.scale_ratings({"a": 1, "b": 3, "c": 5}), {"a": 0.0, "b": 0.5, "c": 1.0})

    def test_swing_weights_points_normalise_by_total(self):
        w = vd.swing_weights({"k01": 100, "k03": 60, "k02": 40})
        self.assertAlmostEqual(w["k01"], 0.5)
        self.assertAlmostEqual(w["k03"], 0.3)
        self.assertAlmostEqual(w["k02"], 0.2)

    def test_roc_weights_three_criteria_returns_fixed_values(self):
        w = vd.roc_weights(["k01", "k03", "k02"])
        self.assertEqual({k: round(v, 4) for k, v in w.items()}, {"k01": 0.6111, "k03": 0.2778, "k02": 0.1111})
        self.assertAlmostEqual(sum(w.values()), 1.0)

    def test_equal_weights_four_criteria_returns_quarter(self):
        self.assertEqual(vd.equal_weights(["a", "b", "c", "d"]), {"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25})

    def test_weighted_scores_full_data_returns_weighted_sum(self):
        crits = [{"id": "k01", "scaled": {A: 0.0, B: 1.0}}, {"id": "k02", "scaled": {A: 1.0, B: 0.5}}]
        s = vd.weighted_scores(crits, {"k01": 0.75, "k02": 0.25}, [A, B])
        self.assertAlmostEqual(s[A], 0.25)
        self.assertAlmostEqual(s[B], 0.875)

    def test_weighted_scores_null_renormalises(self):
        crits = [{"id": "k01", "scaled": {A: 1.0, B: 0.0}}, {"id": "k02", "scaled": {A: None, B: 1.0}}]
        s = vd.weighted_scores(crits, {"k01": 0.5, "k02": 0.5}, [A, B])
        self.assertAlmostEqual(s[A], 1.0)  # k01 だけが残り、重み 0.5 が 1 に戻る
        self.assertAlmostEqual(s[B], 0.5)

    def test_weighted_scores_all_null_returns_none(self):
        crits = [{"id": "k01", "scaled": {A: None, B: 1.0}}]
        self.assertIsNone(vd.weighted_scores(crits, {"k01": 1.0}, [A, B])[A])

    def test_rank_null_sorts_last(self):
        self.assertEqual(vd.rank({A: None, B: 0.3}, [A, B]), [B, A])

    def test_rank_ties_return_input_order(self):
        self.assertEqual(vd.rank({A: 0.5, B: 0.5}, [A, B]), [A, B])
        self.assertEqual(vd.rank({A: 0.5, B: 0.5}, [B, A]), [B, A])

    def test_want_counts_without_wishes_returns_none(self):
        crits = [{"id": "k01", "scaled": {A: 0.0, B: 1.0}}, {"id": "k02", "scaled": {A: 1.0, B: 1.0}}]
        self.assertIsNone(vd.want_counts(crits, [A, B], None))

    def test_want_counts_with_wishes_counts_want_only(self):
        crits = [
            {"id": "k01", "condition_id": "c001", "scaled": {A: 0.0, B: 1.0}},
            {"id": "k03", "condition_id": "c003", "scaled": {A: 1.0, B: 0.0}},
            {"id": "k02", "condition_id": None, "scaled": {A: 1.0, B: 0.0}},
        ]
        self.assertEqual(vd.want_counts(crits, [A, B], WISHES), {A: 1, B: 0})

    def test_fill_scaled_values_per_criterion(self):
        d = good()
        self.assertEqual(d["criteria"][0]["scaled"], {A: 0.0, B: 1.0})
        self.assertEqual(d["criteria"][1]["scaled"], {A: 0.0, B: 1.0})
        self.assertEqual(d["criteria"][2]["scaled"], {A: 0.75, B: 0.25})

    def test_fill_roc_weights(self):
        self.assertEqual(good()["weights"]["roc"], {"k01": 0.6111, "k03": 0.2778, "k02": 0.1111})

    def test_fill_swing_scores(self):
        self.assertEqual(good()["scores"]["swing"], {A: 0.225, B: 0.775})

    def test_fill_swing_ranking(self):
        self.assertEqual(good()["rankings"]["swing"], [B, A])

    def test_fill_without_wishes_want_count_zero(self):
        self.assertEqual(good()["scores"]["want_count"], {A: 0, B: 0})

    def test_fill_with_wishes_want_count_zero_below_best(self):
        self.assertEqual(vd.fill(raw(), WISHES)["scores"]["want_count"], {A: 0, B: 0})  # k01 は must、k03 の A は 0.75

    def test_fill_with_want_conditions_counts_best_values(self):
        wants = {"conditions": [{"id": "c001", "level": "want"}, {"id": "c003", "level": "want"}]}
        self.assertEqual(vd.fill(raw(), wants)["scores"]["want_count"], {A: 0, B: 1})

    def test_sensitivity_top_unchanged(self):
        s = good()["sensitivity"]
        self.assertFalse(s["top_changes"])

    def test_sensitivity_details_two_changes_per_criterion(self):
        s = good()["sensitivity"]
        self.assertEqual(s["delta"], 0.2)
        self.assertEqual([(x["criterion_id"], x["change"]) for x in s["details"]][:2], [("k01", "-20%"), ("k01", "+20%")])
        self.assertEqual(len(s["details"]), 6)


def close_race():
    """重みを 20% 動かすと首位が入れ替わる記録。"""
    d = raw()
    d["criteria"][1]["values"] = {A: 20, B: 25}
    d["criteria"][2]["ratings"] = {A: 5, B: 1}
    d["swing_points"] = {"k01": 100, "k03": 60, "k02": 30}
    return vd.fill(d, WISHES)


class ValidateTest(unittest.TestCase):
    def test_valid_fixture_no_findings(self):
        r = check(good())
        self.assertEqual((r.errors, r.warnings), ([], []))
        self.assertEqual(check(vd.fill(raw(), WISHES), WISHES).errors, [])

    def mutate(self, fn, wishes=None):
        d = good()
        fn(d)
        return check(d, wishes)

    def assertError(self, fn, text, wishes=None):
        r = self.mutate(fn, wishes)
        self.assertTrue(has(r.errors, text), r.errors)

    def test_root_not_object_fails(self):
        self.assertFalse(check([]).ok)

    def test_error_header_id_date_subject(self):
        self.assertError(lambda d: d.update(id="2026-infra"), "id は")
        self.assertError(lambda d: d.update(id="20261116-infra"), "日付部分")
        self.assertError(lambda d: d.update(date="2026-13-01"), "date は")
        self.assertError(lambda d: d.update(subject=" "), "subject は")

    def test_error_missing_required_field(self):
        d = good()
        del d["swing_order"]
        self.assertTrue(has(check(d).errors, "swing_order"))
        d = good()
        del d["follow_up"]
        self.assertTrue(has(check(d).errors, "follow_up"))

    def test_error_candidates(self):
        self.assertError(lambda d: d.update(candidates=d["candidates"][:1]), "2〜5 件")
        self.assertError(lambda d: d["candidates"][1].update(posting_id=A), "重複")
        self.assertError(lambda d: d["candidates"][1].update(posting_id="B_ベータ-2026"), "posting_id は")
        self.assertError(lambda d: d["candidates"][1].update(company_slug="X"), "company_slug")
        self.assertError(lambda d: d["candidates"][1].update(label="ABC"), "label")

    def test_error_criterion_id_field_and_direction(self):
        self.assertError(lambda d: d["criteria"][0].update(id="k1"), "k と 2 桁")
        self.assertError(lambda d: d["criteria"][1].update(id="k01"), "重複")
        self.assertError(lambda d: d["criteria"][0].update(field_id="nothing"), "辞書にない")
        self.assertError(lambda d: d["criteria"][0].update(direction="lower"), "辞書の向き")
        self.assertError(lambda d: d["criteria"][0].update(direction="up"), "higher か lower")

    def test_error_custom_without_condition(self):
        self.assertError(lambda d: d["criteria"][2].update(condition_id=None), "condition_id が必須")

    def test_error_values_and_ratings(self):
        self.assertError(lambda d: d["criteria"][0].update(values=None), "values は")
        self.assertError(lambda d: d["criteria"][0].update(ratings={A: 3, B: 3}), "ratings は null")
        self.assertError(lambda d: d["criteria"][0]["values"].pop(A), "キーが候補")
        self.assertError(lambda d: d["criteria"][0]["values"].update({A: "高い"}), "整数")
        self.assertError(lambda d: d["criteria"][2]["ratings"].update({A: 6}), "1〜5")
        self.assertError(lambda d: d["criteria"][2].update(values={A: 1, B: 2}), "values は null")

    def test_error_swing(self):
        self.assertError(lambda d: d.update(swing_order=["k01", "k02"]), "並べ替え")
        self.assertError(lambda d: d["swing_points"].pop("k02"), "キーが基準")
        self.assertError(lambda d: d["swing_points"].update(k02=120), "0〜100")
        self.assertError(lambda d: d["swing_points"].update(k01=90), "100")

    def test_error_weights(self):
        self.assertError(lambda d: d["weights"].pop("roc"), "weights")
        self.assertError(lambda d: d["weights"]["swing"].update(k01=0.9), "weights.swing")
        self.assertError(lambda d: d["weights"]["equal"].update(k01=0.5), "合計が 1")

    def test_error_rankings(self):
        self.assertError(lambda d: d["rankings"].pop("equal"), "rankings")
        self.assertError(lambda d: d["rankings"].update(swing=[A, A]), "rankings.swing")

    def test_error_derived_differs(self):
        self.assertError(lambda d: d["criteria"][0]["scaled"].update({A: 0.5}), "scaled")
        self.assertError(lambda d: d["scores"]["swing"].update({A: 0.5}), "scores.swing")
        self.assertError(lambda d: d["sensitivity"].update(top_changes=True), "sensitivity")

    def test_derived_within_tolerance_no_error(self):
        d = good()
        d["scores"]["swing"][A] += 0.0004  # 許容差内
        self.assertTrue(check(d).ok)

    def test_error_chosen_and_fields(self):
        self.assertError(lambda d: d.update(chosen="X-20261001-01"), "chosen")
        self.assertError(lambda d: d.update(decisive_fields=["k09"]), "decisive_fields")
        self.assertError(lambda d: d.update(compromised_fields=["x"]), "compromised_fields")

    def test_error_follow_up(self):
        self.assertError(lambda d: d["follow_up"].pop(), "follow_up は")
        self.assertError(lambda d: d["follow_up"][0].update(at="6m"), "follow_up は")
        self.assertError(lambda d: d["follow_up"][0].update(satisfaction=6), "satisfaction")
        self.assertError(lambda d: d["follow_up"][1].update(date="2027-02-30"), "date")

    def test_error_condition_missing_in_wishes(self):
        self.assertError(lambda d: None, "wishes.json にない", wishes={"conditions": [{"id": "c001", "level": "must"}]})

    def test_warn_unknown_schema_version(self):
        r = self.mutate(lambda d: d.update(schema_version="9.9"))
        self.assertTrue(has(r.warnings, "schema_version"))
        self.assertTrue(r.ok)

    def test_warn_null_scaled(self):
        d = raw()
        d["criteria"][1]["values"][B] = None
        r = check(vd.fill(d, None))
        self.assertTrue(has(r.warnings, "換算値が null"))
        self.assertTrue(r.ok)

    def test_fill_null_value_renormalises(self):
        d = raw()
        d["criteria"][1]["values"][B] = None
        f = vd.fill(d, None)
        self.assertIsNone(f["criteria"][1]["scaled"][B])
        self.assertEqual(f["scores"]["swing"][B], round((0.5 * 1.0 + 0.3 * 0.25) / 0.8, 4))

    def test_warn_chosen_without_decisive(self):
        r = self.mutate(lambda d: d.update(decisive_fields=[]))
        self.assertTrue(has(r.warnings, "decisive_fields"))

    def test_no_chosen_without_decisive_no_warnings(self):
        self.assertTrue(check(vd.fill(dict(raw(), chosen=None, decisive_fields=[]), None)).warnings == [])

    def test_warn_top_changes(self):
        d = close_race()
        self.assertTrue(d["sensitivity"]["top_changes"])
        r = check(d)
        self.assertTrue(has(r.warnings, "top_changes"))
        self.assertTrue(r.ok)


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = vd.main(list(args))
        return code, buf.getvalue()

    def write(self, d):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        self.addCleanup(os.remove, path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        return path

    def test_fill_writes_derived_fields(self):
        path = self.write(raw())
        self.assertEqual(self.run_cli(path)[0], 1)
        code, out = self.run_cli(path, "--fill")
        self.assertEqual(code, 0, out)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.assertTrue(text.endswith("}\n"))
        self.assertIn("アクメクラウド", text)
        self.assertEqual(json.loads(text)["rankings"]["swing"], [B, A])

    def test_fill_output_passes_validate(self):
        path = self.write(raw())
        self.run_cli(path, "--fill")
        self.assertEqual(self.run_cli(path)[0], 0)

    def test_fill_twice_unchanged(self):
        path = self.write(raw())
        self.run_cli(path, "--fill")
        with open(path, encoding="utf-8") as f:
            first = f.read()
        self.run_cli(path, "--fill")
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), first)

    def test_fill_refuses_invalid_input(self):
        d = raw()
        d["swing_points"]["k01"] = 90
        path = self.write(d)
        code, _ = self.run_cli(path, "--fill")
        self.assertEqual(code, 1)
        with open(path, encoding="utf-8") as f:
            self.assertNotIn("weights", json.load(f))

    def test_json_output_with_wishes_status_pass(self):
        path = self.write(vd.fill(raw(), WISHES))
        wishes = self.write(WISHES)
        code, out = self.run_cli(path, "--wishes", wishes, "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["status"], "PASS")

    def test_unreadable_file_fails(self):
        code, out = self.run_cli(os.path.join(tempfile.gettempdir(), "no-such-decision.json"), "--json")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
