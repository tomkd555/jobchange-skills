"""validate_profile.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_profile
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

import validate_profile as vp  # noqa: E402


def _valid_profile() -> dict:
    """schema_version 1.0 の、移行推奨の WARN 以外が出ない完全なプロファイルを返す。"""
    return {
        "schema_version": "1.0",
        "updated_at": "2026-07-12",
        "basic": {
            "current_role": "バックエンドエンジニア",
            "years_of_experience": 6,
            "location": "東京都",
            "education": ["○○大学 情報工学科"],
        },
        "career_history": [
            {
                "company": "架空システム株式会社",
                "period": "2020-04〜2026-06",
                "role": "バックエンドエンジニア",
                "responsibilities": ["API 設計", "チームリード"],
                "achievements": [
                    {"description": "処理時間短縮", "metric": "応答時間を40%削減"}
                ],
            }
        ],
        "skills": {
            "technical": ["Python", "AWS"],
            "business": ["要件定義"],
            "languages": [{"language": "英語", "level": "TOEIC 800"}],
            "certifications": ["応用情報技術者"],
        },
        "strengths": ["設計力"],
        "job_change_axis": {
            "reasons": ["裁量の拡大"],
            "must_conditions": ["リモート可"],
            "want_conditions": ["年収600万以上"],
        },
        "targets": {
            "industries": ["SaaS"],
            "roles": ["テックリード"],
            "companies": ["架空クラウド社"],
        },
        "salary": {"current": 5500000, "desired": 7000000},
        "notes": "",
    }


def _work_character_preferences(**desires: str) -> list[dict]:
    """8特性すべてを持つ work_character_preferences を返す。既定は neutral。"""
    preferences = []
    for trait in vp._WORK_CHARACTER_TRAITS:
        desire = desires.get(trait, "neutral")
        entry = {"trait": trait, "desire": desire}
        if desire == "must":
            entry["statement"] = f"{trait} を満たすこと"
        preferences.append(entry)
    return preferences


def _company_score_axes() -> list[dict]:
    """ERROR 0件・WARN 0件になる company_score_axes を返す。"""
    return [
        {
            "axis": "compensation_level",
            "kind": "quantitative",
            "weight": 40,
            "thresholds": {"zero": 4500000, "full": 7000000},
        },
        {"axis": "annual_holidays", "kind": "quantitative", "weight": 25},
        {
            "axis": "discretion",
            "kind": "qualitative",
            "weight": 35,
            "label": "裁量の大きさ",
            "definition": "設計方針を自分で決められること",
            "judgment": [
                {"score": 100, "condition": "求人票に設計裁量の記載があり、面接でも確認できた"},
                {"score": 50, "condition": "求人票に記載があるが未確認"},
                {"score": 0, "condition": "上位者の承認が必要と明記されている"},
            ],
        },
    ]


def _valid_v2_profile() -> dict:
    """ERROR 0件・WARN 0件になる schema_version 2.0 のプロファイルを返す。"""
    profile = _valid_profile()
    profile["schema_version"] = "2.0"
    profile["job_change_axis"] = {
        "reasons": ["裁量の拡大"],
        "conditions": [
            {
                "id": "cond-remote",
                "level": "must",
                "statement": "フルリモートが制度として保証されていること",
                "axis": "remote_certainty",
                "operator": "==",
                "value": "guaranteed",
                "unit": "none",
                "verification": "posting",
                "priority": 1,
            },
            {
                "id": "cond-salary",
                "level": "want",
                "statement": "年収600万円以上",
                "axis": "salary_condition",
                "operator": ">=",
                "value": 6000000,
                "unit": "yen",
                "verification": "posting",
            },
        ],
        "work_character_preferences": _work_character_preferences(hands_on="important"),
    }
    profile["company_score_axes"] = _company_score_axes()
    return profile


def _valid_v3_profile() -> dict:
    """schema_version 3.0 の、職歴の事実だけを持つプロファイルを返す。"""
    profile = _valid_v2_profile()
    for key in vp._AXIS_KEYS:
        profile.pop(key, None)
    profile["schema_version"] = "3.0"
    return profile


def _minimal_v1_0_profile() -> dict:
    """v1.0 の必須項目のみを持つ最小プロファイル（後方互換確認用）。"""
    return {
        "schema_version": "1.0",
        "basic": {"current_role": "エンジニア"},
        "career_history": [
            {"company": "架空株式会社", "period": "2022-04〜現在", "role": "エンジニア"}
        ],
        "job_change_axis": {"reasons": ["裁量の拡大"]},
    }


def _career(period: str, company: str = "架空職場") -> dict:
    return {
        "company": company,
        "period": period,
        "role": "エンジニア",
        "achievements": [{"description": "実績", "metric": "10%改善"}],
    }


def _cond(p: dict, i: int = 0) -> dict:
    return p["job_change_axis"]["conditions"][i]


def _prefs(p: dict) -> list:
    return p["job_change_axis"]["work_character_preferences"]


def _set(target: dict, key: str, value):
    target[key] = value


def _make_must_salary(p: dict, value: int) -> None:
    c = _cond(p, 1)
    c.update(level="must", priority=2, value=value)


def _make_four_musts(p: dict) -> None:
    c = _cond(p, 1)
    c.update(level="must", priority=2)
    for pref in _prefs(p)[:2]:
        pref.update(desire="must", statement="満たすこと")


def _duplicate_must_axis(p: dict) -> None:
    extra = dict(_cond(p))
    extra["id"] = "cond-remote-2"
    p["job_change_axis"]["conditions"].append(extra)


class ValidateTest(unittest.TestCase):
    def test_valid_documents_pass(self):
        # (ラベル, 文書, 期待する WARN の部分文字列。None は WARN 0件)
        rows = [
            ("v1 完全版は移行推奨の WARN だけ", _valid_profile(), "2.0 への移行"),
            ("v1.1 も移行推奨の WARN だけ", {**_valid_profile(), "schema_version": "1.1"}, "2.0 への移行"),
            ("v1.0 最小形（後方互換）", _minimal_v1_0_profile(), "2.0 への移行"),
            ("v2 完全版", _valid_v2_profile(), None),
            ("v3 完全版", _valid_v3_profile(), None),
        ]
        for label, doc, warn in rows:
            with self.subTest(label):
                result = vp.validate(doc)
                self.assertEqual(result.errors, [])
                if warn is None:
                    self.assertEqual(result.warnings, [])
                else:
                    self.assertTrue(
                        any(warn in w for w in result.warnings), result.warnings
                    )

    def test_bundled_example_passes_without_warnings(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "assets",
            "profile_example.json",
        )
        result = vp.validate(vp.load_profile(path))
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_error_rules(self):
        # (ラベル, 基準文書, 変更, 期待する ERROR の部分文字列)
        v2, v3 = _valid_v2_profile, _valid_v3_profile
        rows = [
            ("ルートがオブジェクトでない", v2, lambda p: ["x"], "(root)"),
            ("必須項目の欠落（代表: schema_version）", v2, lambda p: p.pop("schema_version"), "schema_version"),
            ("basic.current_role が空", v2, lambda p: p["basic"].__setitem__("current_role", " "), "current_role"),
            ("career_history が空", v2, lambda p: _set(p, "career_history", []), "career_history"),
            ("職歴の company が欠落", v2, lambda p: p["career_history"][0].pop("company"), "company"),
            ("v3 でも職歴の誤りを検出", v3, lambda p: _set(p, "career_history", []), "career_history"),
            ("reasons が空白だけ", v2, lambda p: p["job_change_axis"].__setitem__("reasons", ["", " "]), "reasons"),
            ("conditions が配列でない", v2, lambda p: p["job_change_axis"].__setitem__("conditions", {}), "conditions"),
            ("conditions の id 重複", v2, lambda p: _cond(p, 1).__setitem__("id", "cond-remote"), "重複"),
            ("conditions の id が正規表現に不一致", v2, lambda p: _cond(p).__setitem__("id", "Cond Remote"), ".id"),
            ("conditions の level が列挙外", v2, lambda p: _cond(p).__setitem__("level", "nice"), ".level"),
            ("conditions の axis が8軸外", v2, lambda p: _cond(p).__setitem__("axis", "vibes"), ".axis"),
            ("qualitative 以外で value が無い", v2, lambda p: _cond(p).__setitem__("value", None), ".value"),
            ("unit が列挙外", v2, lambda p: _cond(p).__setitem__("unit", "万円"), ".unit"),
            ("work_character の特性が欠落", v2, lambda p: _prefs(p).pop(), "欠落"),
            ("work_character の trait 重複", v2, lambda p: _prefs(p)[1].__setitem__("trait", _prefs(p)[0]["trait"]), "重複"),
            (
                "desire=must で statement が無い",
                v2,
                lambda p: _prefs(p)[0].update(desire="must"),
                "statement",
            ),
            ("company_score_axes が配列でない", v2, lambda p: _set(p, "company_score_axes", {"a": 1}), "company_score_axes"),
            ("score 軸の axis 重複", v2, lambda p: p["company_score_axes"][1].__setitem__("axis", "compensation_level"), "重複"),
            ("kind が列挙外", v2, lambda p: p["company_score_axes"][0].__setitem__("kind", "mixed"), ".kind"),
            ("定量軸が候補9個の外", v2, lambda p: p["company_score_axes"][1].__setitem__("axis", "vibes"), "定量候補軸"),
            ("定性軸の識別子に大文字", v2, lambda p: p["company_score_axes"][2].__setitem__("axis", "Onboarding"), "定性軸の axis"),
            ("weight が範囲外（代表: 0）", v2, lambda p: p["company_score_axes"][0].__setitem__("weight", 0), ".weight"),
            ("weight の合計が100でない", v2, lambda p: p["company_score_axes"][1].__setitem__("weight", 20), "合計"),
            ("定性軸に thresholds", v2, lambda p: p["company_score_axes"][2].__setitem__("thresholds", {"zero": 0, "full": 1}), "thresholds"),
            ("thresholds の zero と full が同値", v2, lambda p: p["company_score_axes"][0].__setitem__("thresholds", {"zero": 1, "full": 1}), "異なる値"),
            ("thresholds が数値でない", v2, lambda p: p["company_score_axes"][0].__setitem__("thresholds", {"zero": "a", "full": 1}), "数値"),
            ("定性軸の label が欠落", v2, lambda p: p["company_score_axes"][2].pop("label"), "label"),
            ("定性軸の judgment が空", v2, lambda p: p["company_score_axes"][2].__setitem__("judgment", []), "judgment"),
            ("judgment の score が範囲外", v2, lambda p: p["company_score_axes"][2]["judgment"][0].__setitem__("score", 120), ".score"),
        ]
        for label, base, mutate, expected in rows:
            with self.subTest(label):
                doc = base()
                replaced = mutate(doc)
                if isinstance(replaced, list):
                    doc = replaced
                result = vp.validate(doc)
                self.assertFalse(result.ok)
                self.assertTrue(any(expected in e for e in result.errors), result.errors)

    def test_warn_rules(self):
        # (ラベル, 基準文書, 変更, 期待する WARN の部分文字列)。いずれも ERROR は 0件のまま
        v1, v2, v3 = _valid_profile, _valid_v2_profile, _valid_v3_profile
        gap = [_career("2018-04〜2019-03"), _career("2020-01〜現在")]
        rows = [
            ("metric が1件も無い", v2, lambda p: p["career_history"][0].__setitem__("achievements", [{"metric": None}]), "metric"),
            ("skills の全カテゴリが空", v2, lambda p: _set(p, "skills", {"technical": [], "portable": []}), "全カテゴリが空"),
            ("targets の全カテゴリが空", v2, lambda p: _set(p, "targets", {"industries": []}), "targets"),
            ("updated_at が未設定", v2, lambda p: p.pop("updated_at"), "updated_at"),
            ("schema_version が未知", v2, lambda p: _set(p, "schema_version", "9.9"), "既知のバージョン"),
            ("period の形式不一致", v2, lambda p: p["career_history"][0].__setitem__("period", "2020/04-2026/06"), "career_history[0].period"),
            ("6ヶ月以上の空白で career_gaps が無い", v2, lambda p: _set(p, "career_history", gap), "career_gaps"),
            (
                "並行職歴の後の実際の空白",
                v2,
                lambda p: _set(
                    p,
                    "career_history",
                    [_career("2015-04〜2018-03"), _career("2016-04〜2017-03"), _career("2019-06〜現在")],
                ),
                "career_gaps",
            ),
            ("languages の形式不一致", v2, lambda p: p["skills"].__setitem__("languages", [{"language": "英語"}]), "skills.languages[0]"),
            ("salary が数値でも null でもない", v2, lambda p: p["salary"].__setitem__("current", "五百万円"), "salary.current"),
            ("career_gaps の period 不一致", v2, lambda p: _set(p, "career_gaps", [{"period": "2019年4月", "explanation": "休養"}]), "career_gaps[0].period"),
            ("career_gaps の explanation が空", v2, lambda p: _set(p, "career_gaps", [{"period": "2019-04〜2019-09", "explanation": ""}]), "career_gaps[0].explanation"),
            ("portable の category が列挙外", v2, lambda p: p["skills"].__setitem__("portable", [{"skill": "傾聴力", "category": "その他"}]), "skills.portable[0].category"),
            ("v1 の must_conditions が4件", v1, lambda p: p["job_change_axis"].__setitem__("must_conditions", list("ABCD")), "must_conditions"),
            ("v2 の必須条件の合計が4件", v2, _make_four_musts, "合計が4件"),
            ("v2 に旧配列が残っている", v2, lambda p: p["job_change_axis"].__setitem__("must_conditions", ["リモート可"]), "must_conditions"),
            ("必須の年収下限が希望年収超え", v2, lambda p: _make_must_salary(p, 9000000), "希望年収"),
            ("level=must の条件が無い", v2, lambda p: _cond(p).__setitem__("level", "want"), "must の条件が1件も無い"),
            ("同じ軸に必須条件が複数", v2, _duplicate_must_axis, "同じ軸に必須条件"),
            ("must の priority が無い", v2, lambda p: _cond(p).pop("priority"), "priority"),
            ("judgment が降順でない", v2, lambda p: p["company_score_axes"][2]["judgment"].reverse(), "降順"),
            ("company_score_axes が空配列", v2, lambda p: _set(p, "company_score_axes", []), "company_score_axes"),
            (
                "compensation_level が軸に無い",
                v2,
                lambda p: _set(
                    p,
                    "company_score_axes",
                    [
                        {"axis": "annual_holidays", "kind": "quantitative", "weight": 60},
                        {"axis": "monthly_overtime", "kind": "quantitative", "weight": 40},
                    ],
                ),
                "compensation_level",
            ),
            ("v3 に軸のキーが残っている", v3, lambda p: _set(p, "salary", {"desired": 7000000}), "axis.json"),
        ]
        for label, base, mutate, expected in rows:
            with self.subTest(label):
                doc = base()
                mutate(doc)
                result = vp.validate(doc)
                self.assertEqual(result.errors, [])
                self.assertTrue(any(expected in w for w in result.warnings), result.warnings)

    def test_inputs_that_must_not_warn(self):
        # (ラベル, 基準文書, 変更, 出てはならない WARN の部分文字列)
        v1, v2 = _valid_profile, _valid_v2_profile
        rows = [
            ("v1.1 は既知のバージョン", v1, lambda p: _set(p, "schema_version", "1.1"), "既知のバージョン"),
            ("現在までの period", v2, lambda p: p["career_history"][0].__setitem__("period", "2020-04〜現在"), "period"),
            ("5ヶ月の空白", v2, lambda p: _set(p, "career_history", [_career("2018-04〜2019-03"), _career("2019-09〜現在")]), "career_gaps"),
            (
                "空白が career_gaps で覆われている",
                v2,
                lambda p: p.update(
                    career_history=[_career("2018-04〜2019-03"), _career("2020-01〜現在")],
                    career_gaps=[{"period": "2019-04〜2019-12", "explanation": "学習期間"}],
                ),
                "career_gaps",
            ),
            ("解析不能な period があると空白判定を省く", v2, lambda p: _set(p, "career_history", [_career("不明"), _career("2020-01〜現在")]), "career_gaps"),
            (
                "本業が覆う範囲の副業2件",
                v2,
                lambda p: _set(
                    p,
                    "career_history",
                    [_career("2015-04〜現在"), _career("2020-04〜2021-03"), _career("2023-04〜現在")],
                ),
                "career_gaps",
            ),
            ("期間が完全に一致する2件", v2, lambda p: _set(p, "career_history", [_career("2020-04〜2022-03"), _career("2020-04〜2022-03")]), "career_gaps"),
            ("salary の null", v2, lambda p: p["salary"].__setitem__("current", None), "salary."),
            ("portable だけが埋まった skills", v2, lambda p: _set(p, "skills", {"technical": [], "portable": [{"skill": "x", "category": "対課題"}]}), "skills"),
            ("v1 の must_conditions が3件", v1, lambda p: p["job_change_axis"].__setitem__("must_conditions", list("ABC")), "must_conditions"),
            ("v1 は v2 の conditions 規則を適用しない", v1, lambda p: p["job_change_axis"].__setitem__("conditions", "x"), "conditions"),
            ("v1 は company_score_axes 規則を適用しない", v1, lambda p: _set(p, "company_score_axes", "x"), "company_score_axes"),
            ("unit の省略と null", v2, lambda p: _cond(p).__setitem__("unit", None), "unit"),
            ("qualitative 条件は value が null でよい", v2, lambda p: _cond(p).update(operator="qualitative", value=None, axis=None), "value"),
        ]
        for label, base, mutate, forbidden in rows:
            with self.subTest(label):
                doc = base()
                mutate(doc)
                result = vp.validate(doc)
                self.assertEqual(result.errors, [])
                self.assertFalse(any(forbidden in w for w in result.warnings), result.warnings)

    def test_every_defined_unit_passes(self):
        for unit in vp._CONDITION_UNITS:
            with self.subTest(unit=unit):
                p = _valid_v2_profile()
                _cond(p)["unit"] = unit
                result = vp.validate(p)
                self.assertEqual((result.errors, result.warnings), ([], []))


class CliTest(unittest.TestCase):
    def _write(self, text: str, encoding: str = "utf-8") -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(text)
        self.addCleanup(os.remove, path)
        return path

    def _run(self, argv) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = vp.main(argv)
        return code, buf.getvalue()

    def test_exit_codes(self):
        invalid = _valid_profile()
        del invalid["schema_version"]
        rows = [
            ("正常", self._write(json.dumps(_valid_profile(), ensure_ascii=False)), 0),
            ("BOM 付きの正常", self._write(json.dumps(_valid_profile(), ensure_ascii=False), "utf-8-sig"), 0),
            ("検証エラー", self._write(json.dumps(invalid)), 1),
            ("壊れた JSON", self._write("{ not valid json "), 1),
            ("存在しないファイル", os.path.join(tempfile.gettempdir(), "no-such-profile.json"), 1),
        ]
        for label, path, expected in rows:
            with self.subTest(label):
                self.assertEqual(self._run([path])[0], expected)

    def test_json_output_keys(self):
        path = self._write(json.dumps(_valid_profile(), ensure_ascii=False))
        code, out = self._run([path, "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(
            sorted(data),
            ["error_count", "errors", "status", "warning_count", "warnings"],
        )
        self.assertEqual(data["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
