"""calculate_company_tier.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests -p "test_calculate_company_tier*"
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import calculate_company_tier as cc  # noqa: E402


def _research(ratings: dict | None = None, *, with_tier: bool = True) -> dict:
    """company_research.json のうち、格付けに使う tier だけを持つ最小の文書を返す。"""
    document: dict = {"schema_version": "2.0", "company_name": "架空クラウドワークス"}
    if with_tier:
        document["tier"] = {
            "rubric_version": 2,
            "assessed_date": "2026-07-29",
            "axes": {
                axis: {"rating": rating, "basis": "根拠", "claim_ids": ["C001"]}
                for axis, rating in (ratings or {}).items()
            },
        }
    return document


def _profile(*declared) -> dict:
    """(軸キー, 重視段階) の並びから profile.json の company_quality_axes を組み立てる。"""
    return {
        "schema_version": "2.0",
        "company_quality_axes": [
            {"axis": axis, "emphasis": emphasis} for axis, emphasis in declared
        ],
    }


class LevelRuleTest(unittest.TestCase):
    """総合の格付けを C・S・A・B の順に当てはめる規則。原本は tier-rubric.md。"""

    def test_low_on_top_axis_is_c(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "low", "retention": "high"}),
            _profile(("compensation_level", "top"), ("retention", "high")),
        )
        self.assertEqual(tier["level"], "C")

    def test_two_lows_among_target_axes_is_c(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "high", "retention": "low", "work_style": "low"}),
            _profile(("compensation_level", "top"), ("retention", "high"), ("work_style", "high")),
        )
        self.assertEqual(tier["level"], "C")

    def test_all_top_high_without_low_is_s(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "high", "retention": "medium"}),
            _profile(("compensation_level", "top"), ("retention", "high")),
        )
        self.assertEqual(tier["level"], "S")

    def test_two_highs_without_low_is_a(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "medium", "retention": "high", "work_style": "high"}),
            _profile(("compensation_level", "top"), ("retention", "high"), ("work_style", "high")),
        )
        self.assertEqual(tier["level"], "A")

    def test_single_low_without_top_low_is_b(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "high", "retention": "low"}),
            _profile(("compensation_level", "high"), ("retention", "high")),
        )
        self.assertEqual(tier["level"], "B")

    def test_medium_only_is_b(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "medium", "retention": "medium"}),
            _profile(("compensation_level", "top"), ("retention", "high")),
        )
        self.assertEqual(tier["level"], "B")

    def test_s_requires_a_top_axis(self):
        # top の軸が1つも無ければ最重視の条件を満たしようがない。high 2軸なら A になる。
        tier = cc.build_company_tier(
            _research({"compensation_level": "high", "retention": "high"}),
            _profile(("compensation_level", "high"), ("retention", "high")),
        )
        self.assertEqual(tier["level"], "A")

    def test_unknown_top_axis_is_not_s(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "unknown", "retention": "high"}),
            _profile(("compensation_level", "top"), ("retention", "high")),
        )
        self.assertEqual(tier["level"], "B")


class ProvisionalTest(unittest.TestCase):
    """暫定（provisional）の条件。"""

    def test_unknown_on_top_axis_is_provisional(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "unknown", "retention": "high"}),
            _profile(("compensation_level", "top"), ("retention", "high")),
        )
        self.assertTrue(tier["provisional"])

    def test_two_unknown_target_axes_is_provisional(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "high", "retention": "unknown"}),
            _profile(
                ("compensation_level", "top"), ("retention", "high"), ("work_style", "high")
            ),
        )
        self.assertTrue(tier["provisional"])

    def test_single_unknown_on_non_top_axis_is_not_provisional(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "high", "retention": "unknown"}),
            _profile(("compensation_level", "top"), ("retention", "high")),
        )
        self.assertFalse(tier["provisional"])

    def test_unknown_reference_axis_is_not_provisional(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "high"}),
            _profile(("compensation_level", "top"), ("growth", "reference")),
        )
        self.assertFalse(tier["provisional"])


class NoEmphasisTest(unittest.TestCase):
    """重視軸の申告が無いときは重みを仮定せず、格付けを出さない。"""

    def test_missing_company_quality_axes_yields_null_level(self):
        tier = cc.build_company_tier(_research({"compensation_level": "high"}), {"schema_version": "2.0"})
        self.assertIsNone(tier["level"])
        self.assertFalse(tier["provisional"])
        self.assertEqual(tier["axes"], [])
        self.assertIn("申告", tier["rationale"])

    def test_empty_company_quality_axes_yields_null_level(self):
        tier = cc.build_company_tier(_research({"compensation_level": "high"}), _profile())
        self.assertIsNone(tier["level"])
        self.assertFalse(tier["provisional"])

    def test_reference_only_declaration_yields_null_level(self):
        tier = cc.build_company_tier(
            _research({"growth": "high"}), _profile(("growth", "reference"))
        )
        self.assertIsNone(tier["level"])
        self.assertFalse(tier["provisional"])
        self.assertEqual(len(tier["axes"]), 1)


class AxesOutputTest(unittest.TestCase):
    """axes は申告順に並べ、参考の軸も併記する。"""

    def test_axes_keep_declared_order(self):
        tier = cc.build_company_tier(
            _research({"retention": "high", "compensation_level": "medium"}),
            _profile(
                ("retention", "high"), ("compensation_level", "top"), ("growth", "reference")
            ),
        )
        self.assertEqual(
            [a["axis"] for a in tier["axes"]],
            ["retention", "compensation_level", "growth"],
        )
        self.assertEqual([a["emphasis"] for a in tier["axes"]], ["high", "top", "reference"])

    def test_axis_not_assessed_by_research_is_unknown(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "high"}),
            _profile(("compensation_level", "top"), ("tech_advancement", "high")),
        )
        ratings = {a["axis"]: a["rating"] for a in tier["axes"]}
        self.assertEqual(ratings["tech_advancement"], "unknown")

    def test_reference_axis_is_excluded_from_aggregation(self):
        # 参考の軸が low でも C にせず、報告のために axes へは残す。
        tier = cc.build_company_tier(
            _research({"compensation_level": "high", "retention": "high", "growth": "low"}),
            _profile(
                ("compensation_level", "top"), ("retention", "high"), ("growth", "reference")
            ),
        )
        self.assertEqual(tier["level"], "S")
        self.assertIn("growth", [a["axis"] for a in tier["axes"]])

    def test_reference_high_does_not_raise_the_level(self):
        # 参考の軸の high を A の集計（high 2件以上）に数えない。
        tier = cc.build_company_tier(
            _research({"compensation_level": "high", "growth": "high"}),
            _profile(("compensation_level", "high"), ("growth", "reference")),
        )
        self.assertEqual(tier["level"], "B")


class MissingTierTest(unittest.TestCase):
    """企業研究に tier が無い場合は全軸 unknown として扱う。"""

    def test_missing_tier_treats_all_axes_as_unknown(self):
        tier = cc.build_company_tier(
            _research(with_tier=False),
            _profile(("compensation_level", "top"), ("retention", "high")),
        )
        self.assertEqual([a["rating"] for a in tier["axes"]], ["unknown", "unknown"])
        self.assertTrue(tier["provisional"])
        self.assertIsNone(tier["level"])

    def test_missing_tier_falls_back_to_current_rubric_version(self):
        tier = cc.build_company_tier(_research(with_tier=False), _profile(("retention", "high")))
        self.assertEqual(tier["rubric_version"], cc.RUBRIC_VERSION)
        self.assertIsNone(tier["assessed_date"])


class NoRatedAxisTest(unittest.TestCase):
    """対象軸がすべて unknown の場合は格付けせず、暫定であることを示す。"""

    def test_single_high_axis_unknown_yields_null_level(self):
        tier = cc.build_company_tier(
            _research({"retention": "unknown"}), _profile(("retention", "high"))
        )
        self.assertIsNone(tier["level"])
        self.assertTrue(tier["provisional"])

    def test_reference_axis_rating_does_not_make_level(self):
        """参考の軸に評価があっても、対象軸が無ければ格付けしない。"""
        tier = cc.build_company_tier(
            _research({"retention": "unknown", "growth": "high"}),
            _profile(("retention", "high"), ("growth", "reference")),
        )
        self.assertIsNone(tier["level"])
        self.assertTrue(tier["provisional"])

    def test_rationale_states_no_rated_axis(self):
        tier = cc.build_company_tier(
            _research({"retention": "unknown"}), _profile(("retention", "high"))
        )
        self.assertIn("評価できた軸が無い", tier["rationale"])


class RationaleTest(unittest.TestCase):
    """rationale は決定的に組み立てる。"""

    def _tier(self) -> dict:
        return cc.build_company_tier(
            _research({"compensation_level": "high", "retention": "medium", "growth": "unknown"}),
            _profile(
                ("compensation_level", "top"), ("retention", "high"), ("growth", "reference")
            ),
        )

    def test_same_input_yields_same_rationale(self):
        self.assertEqual(self._tier()["rationale"], self._tier()["rationale"])

    def test_rationale_names_the_deciding_axis(self):
        self.assertIn("処遇水準", self._tier()["rationale"])

    def test_provisional_is_stated_in_the_rationale(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "unknown", "retention": "high"}),
            _profile(("compensation_level", "top"), ("retention", "high")),
        )
        self.assertIn("暫定", tier["rationale"])

    def test_reference_axis_is_stated_in_the_rationale(self):
        self.assertIn("参考", self._tier()["rationale"])


class ShapeTest(unittest.TestCase):
    def test_output_keys(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "high"}), _profile(("compensation_level", "top"))
        )
        for key in ("level", "provisional", "rubric_version", "assessed_date", "axes", "rationale"):
            self.assertIn(key, tier)
        self.assertEqual(tier["assessed_date"], "2026-07-29")
        self.assertEqual(tier["rubric_version"], 2)

    def test_output_is_json_serializable(self):
        tier = cc.build_company_tier(
            _research({"compensation_level": "high"}), _profile(("compensation_level", "top"))
        )
        json.dumps(tier, ensure_ascii=False)


class ContradictionTest(unittest.TestCase):
    """入力の矛盾は CalcError を送出する。"""

    def test_unknown_axis_key_raises(self):
        with self.assertRaises(cc.CalcError):
            cc.build_company_tier(_research({}), _profile(("salary_level", "top")))

    def test_unknown_emphasis_raises(self):
        with self.assertRaises(cc.CalcError):
            cc.build_company_tier(_research({}), _profile(("compensation_level", "highest")))

    def test_duplicated_axis_raises(self):
        with self.assertRaises(cc.CalcError):
            cc.build_company_tier(
                _research({}), _profile(("retention", "top"), ("retention", "high"))
            )

    def test_company_quality_axes_not_list_raises(self):
        with self.assertRaises(cc.CalcError):
            cc.build_company_tier(_research({}), {"company_quality_axes": "compensation_level"})


class CliTest(unittest.TestCase):
    def _write(self, obj: dict) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def _args(self) -> list:
        research = self._write(_research({"compensation_level": "high", "retention": "medium"}))
        profile = self._write(_profile(("compensation_level", "top"), ("retention", "high")))
        return ["--research", research, "--profile", profile]

    def test_main_returns_0(self):
        self.assertEqual(cc.main(self._args() + ["--json"]), 0)

    def test_main_out_writes_file_and_creates_parent(self):
        directory = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(directory, ignore_errors=True))
        out_path = os.path.join(directory, "nested", "company_tier.json")
        self.assertEqual(cc.main(self._args() + ["--out", out_path]), 0)
        with open(out_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        self.assertEqual(data["level"], "S")

    def test_main_contradiction_exit_2(self):
        research = self._write(_research({}))
        profile = self._write(_profile(("salary_level", "top")))
        self.assertEqual(cc.main(["--research", research, "--profile", profile]), 2)

    def test_main_unreadable_input_exit_2(self):
        research = self._write(_research({}))
        self.assertEqual(
            cc.main(["--research", research, "--profile", os.path.join(research, "no-such.json")]),
            2,
        )


if __name__ == "__main__":
    unittest.main()
