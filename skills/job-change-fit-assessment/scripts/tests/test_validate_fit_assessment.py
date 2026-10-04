"""validate_fit_assessment.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_validate_fit_assessment
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

import validate_fit_assessment as vf  # noqa: E402


def _dimension(dim_id: str, score=3) -> dict:
    dimension = {
        "id": dim_id,
        "score": score,
        "verdict": f"{dim_id} の判定根拠",
        "evidence": [{"source": "company_research", "ref": "C001", "note": "根拠"}],
    }
    if dim_id == "experience_proximity":
        dimension["skill_gap"] = "none"
        dimension["skill_gap_items"] = []
    if dim_id == "aspiration_alignment":
        dimension["evidence"] = [
            {"source": "self_analysis", "ref": "career_narrative.future_direction", "note": "根拠"}
        ]
    return dimension


def _must_result(ref: str, met: str = "yes", **extra) -> dict:
    entry = {
        "ref": ref,
        "condition": f"{ref} の条件文",
        "met": met,
        "evidence": [{"source": "job_posting", "ref": "location.remote_policy", "note": "根拠"}],
    }
    if met == "unknown":
        entry["evidence"] = []
    entry.update(extra)
    return entry


def _valid_fit() -> dict:
    """schema_version 1.0（5次元）で ERROR 0件・WARN 0件になる fit_assessment。"""
    return {
        "schema_version": "1.0",
        "slug": "kakuu-cloudworks",
        "assessed_at": "2026-07-15",
        "inputs": {
            "job_posting": True,
            "company_research": True,
            "self_analysis": True,
            "time_analysis": True,
        },
        "dimensions": [_dimension(d) for d in vf._V1_DIMENSION_IDS],
        "must_condition_results": [_must_result("cond-remote"), _must_result("cond-side", "unknown")],
        "overall": {
            "recommendation": "条件付き推奨",
            "rationale": "必須条件は概ね満たすが副業可否が未確認である。",
            "open_questions": ["副業許可の有無"],
        },
    }


def _valid_v2_fit(**overrides) -> dict:
    """schema_version 2.0（7次元）で、_v2_profile() と組にして ERROR 0件・WARN 0件になる。"""
    document = {
        "schema_version": "2.0",
        "slug": "kakuu-cloudworks",
        "assessed_at": "2026-07-25",
        "inputs": {
            "job_posting": True,
            "company_research": True,
            "self_analysis": True,
            "time_analysis": True,
            "job_search_screening": False,
        },
        "dimensions": [_dimension(d) for d in vf._V2_DIMENSION_IDS],
        "must_condition_results": [_must_result("cond-remote"), _must_result("no_oncall")],
        "overall": {"recommendation": "推奨", "rationale": "必須条件を満たす", "open_questions": []},
    }
    document.update(overrides)
    return document


def _v2_profile() -> dict:
    return {
        "schema_version": "2.0",
        "job_change_axis": {
            "conditions": [
                {"id": "cond-remote", "level": "must"},
                {"id": "cond-salary", "level": "want"},
            ],
            "work_character_preferences": [
                {"trait": "no_oncall", "desire": "must"},
                {"trait": "hands_on", "desire": "important"},
            ],
        },
    }


def _company_score(**overrides) -> dict:
    score = {
        "total": 72,
        "coverage": 85,
        "provisional": False,
        "axes": [
            {"axis": "compensation_level", "kind": "quantitative", "weight": 50, "score": 65},
            {"axis": "tech_discretion", "kind": "qualitative", "weight": 35, "score": 82},
            {"axis": "annual_holidays", "kind": "quantitative", "weight": 15, "score": None},
        ],
        "rationale": "総合点 72 点は、判定できた2軸の加重平均である。",
    }
    score.update(overrides)
    return score


def _dim(d: dict, dim_id: str) -> dict:
    return next(x for x in d["dimensions"] if x["id"] == dim_id)


def _gap_item(level: str, **extra) -> dict:
    item = {
        "requirement": "Kubernetes 運用",
        "gap_level": level,
        "basis": "隣接経験が無い",
        "evidence": [{"source": "job_posting", "ref": "requirements.must[1]", "note": "根拠"}],
    }
    item.update(extra)
    return item


def _set_gap(d: dict, gap: str, items: list) -> None:
    _dim(d, "experience_proximity").update(skill_gap=gap, skill_gap_items=items)


def _unmet(d: dict, **extra) -> None:
    d["must_condition_results"][0] = _must_result("cond-remote", "no", **extra)


def _screening_case(d: dict, index: int):
    """求人検索で must を満たした軸があり、評価では met=no になった状態を作る。"""
    d["screening_source"] = {"result_index": index}
    _unmet(d, negotiable=True)
    d["overall"]["recommendation"] = "条件付き推奨"
    screening = {"results": [{"axis_judgements": [{"axis": "cond-remote", "level": "must", "judgement": "meets"}]}]}
    return {"screening": screening}


def _run(base: str, mutate):
    """base（"v1" / "v2"）の fixture に mutate を適用して検証する。
    mutate が dict を返したときは validate の追加引数（profile / screening）として使う。"""
    d = _valid_fit() if base == "v1" else _valid_v2_fit()
    kwargs = {} if base == "v1" else {"profile": _v2_profile()}
    extra = mutate(d)
    if isinstance(extra, dict):
        kwargs.update(extra)
    return vf.validate(d, **kwargs)


# (ラベル, base, 変更, ERROR に含まれる文字列)。同じ補助関数を通る検査は代表1行にする。
ERROR_ROWS = [
    ("必須の文字列（slug 欠落）", "v2", lambda d: d.pop("slug"), "slug"),
    ("slug の形式（記号・空白）", "v2", lambda d: d.update(slug="Kakuu CloudWorks"), "slug"),
    ("inputs の型", "v2", lambda d: d["inputs"].update(job_posting="yes"), "job_posting"),
    ("v2 で job_search_screening が必須", "v2", lambda d: d["inputs"].pop("job_search_screening"), "job_search_screening"),
    ("次元 id の欠落", "v2", lambda d: d.update(dimensions=d["dimensions"][:-1]), "time_fit"),
    ("次元 id の重複", "v2", lambda d: d["dimensions"].append(_dimension("time_fit")), "重複"),
    ("v2 で v1 の次元 id", "v2", lambda d: d["dimensions"][0].update(id="skill_fit"), "いずれかでなければ"),
    ("v1 で v2 の次元 id", "v1", lambda d: d["dimensions"][0].update(id="experience_proximity"), "いずれかでなければ"),
    ("score の範囲", "v2", lambda d: d["dimensions"][0].update(score=6), "score"),
    ("score に bool", "v2", lambda d: d["dimensions"][0].update(score=True), "score"),
    ("次元の evidence が空", "v2", lambda d: d["dimensions"][0].update(evidence=[]), "evidence"),
    ("evidence.source の列挙", "v2", lambda d: d["dimensions"][0]["evidence"][0].update(source="hearsay"), "source"),
    ("v1 で job_search_screening を根拠にする", "v1",
     lambda d: d["dimensions"][0]["evidence"][0].update(source="job_search_screening"), "source"),
    ("met の列挙", "v2", lambda d: d["must_condition_results"][0].update(met="maybe"), "met"),
    ("met=yes で evidence が空", "v2", lambda d: d["must_condition_results"][0].update(evidence=[]), "evidence"),
    ("recommendation の列挙", "v2", lambda d: d["overall"].update(recommendation="たぶん推奨"), "recommendation"),
    ("open_questions の型", "v2", lambda d: d["overall"].update(open_questions="なし"), "open_questions"),
    ("skill_gap の列挙", "v2", lambda d: _dim(d, "experience_proximity").update(skill_gap="soon"), "skill_gap"),
    ("skill_gap_items の欠落", "v2", lambda d: _dim(d, "experience_proximity").pop("skill_gap_items"), "skill_gap_items"),
    ("skill_gap が内訳の最重段階と不一致", "v2",
     lambda d: _set_gap(d, "complementable_within_3m", [_gap_item("needs_6_12m_study")]), "最も重い段階"),
    ("gap 項目の basis が空", "v2",
     lambda d: _set_gap(d, "needs_6_12m_study", [_gap_item("needs_6_12m_study", basis="")]), "basis"),
    ("not_applicable_now で応募を勧める", "v2",
     lambda d: _set_gap(d, "not_applicable_now", [_gap_item("not_applicable_now")]), "応募困難"),
    ("must の ref 欠落", "v2", lambda d: d["must_condition_results"][0].pop("ref"), "ref"),
    ("must の ref 重複", "v2", lambda d: d["must_condition_results"].append(_must_result("cond-remote")), "重複している"),
    ("軸の必須条件に対応する判定が無い", "v2",
     lambda d: d.update(must_condition_results=[_must_result("cond-remote")]), "対応する判定が無い"),
    ("軸に無い必須条件を判定", "v2",
     lambda d: d["must_condition_results"].append(_must_result("cond-salary")), "存在しない必須条件"),
    ("negotiable=true で evidence が空", "v2",
     lambda d: (_unmet(d, negotiable=True), d["must_condition_results"][0].update(evidence=[]),
                d["overall"].update(recommendation="条件付き推奨")), "negotiable"),
    ("must 未達で「推奨」", "v2", lambda d: _unmet(d), "「推奨」"),
    ("交渉不能の未達で「条件付き推奨」", "v2",
     lambda d: (_unmet(d), d["overall"].update(recommendation="条件付き推奨")), "交渉で解消できない"),
    ("自己分析なしで志向を高評価", "v2",
     lambda d: (d["inputs"].update(self_analysis=False), _dim(d, "aspiration_alignment").update(score=4)),
     "志向の一致を高く評価"),
    ("志向の根拠が求人票だけ", "v2",
     lambda d: _dim(d, "aspiration_alignment").update(
         evidence=[{"source": "job_posting", "ref": "responsibilities[0]", "note": "根拠"}]), "志向を断定しない"),
    ("--axis が職歴だけの 3.0", "v2", lambda d: {"profile": {"schema_version": "3.0"}}, "--axis"),
    ("--axis がオブジェクトでない", "v2", lambda d: {"profile": []}, "--axis"),
    ("company_score の型", "v2", lambda d: d.update(company_score=72), "company_score"),
    ("company_score.total の範囲", "v2", lambda d: d.update(company_score=_company_score(total=120)), "company_score.total"),
    ("company_score.coverage が null", "v2",
     lambda d: d.update(company_score=_company_score(coverage=None)), "company_score.coverage"),
    ("company_score の kind の列挙", "v2",
     lambda d: d.update(company_score=_company_score(axes=[{"axis": "a", "kind": "numeric", "weight": 10, "score": 1}])),
     "axes[0].kind"),
    ("company_score の weight の範囲", "v2",
     lambda d: d.update(company_score=_company_score(axes=[{"axis": "a", "kind": "qualitative", "weight": 0, "score": 1}])),
     "axes[0].weight"),
    ("company_score.rationale が空", "v2", lambda d: d.update(company_score=_company_score(rationale="")), "rationale"),
]

# (ラベル, base, 変更, WARN に含まれる文字列)。
WARN_ROWS = [
    ("未知の schema_version", "v1", lambda d: d.update(schema_version="9.9"), "schema_version"),
    ("assessed_at の形式", "v1", lambda d: d.update(assessed_at="2026/07/15"), "assessed_at"),
    ("inputs が全て false", "v1", lambda d: d["inputs"].update({k: False for k in d["inputs"]}), "入力が1つも存在しない"),
    ("score が null", "v2", lambda d: d["dimensions"][2].update(score=None), "score"),
    ("evidence の ref が空", "v2", lambda d: d["dimensions"][0]["evidence"][0].update(ref=""), "ref"),
    ("v1: must 未達で「推奨」", "v1",
     lambda d: (_unmet(d), d["overall"].update(recommendation="推奨")), "recommendation"),
    ("v2: 入力の3つ以上が false で「推奨」", "v2",
     lambda d: d["inputs"].update(job_posting=False, company_research=False, time_analysis=False), "3つ以上"),
    ("v2: 自己分析が無く志向の根拠が弱い", "v2", lambda d: d["inputs"].update(self_analysis=False), "志向の根拠が弱い"),
    ("v2: --axis 未指定で1対1が未検証", "v2", lambda d: {"profile": None}, "未検証"),
    ("v2: --axis が 2.0 でなく1対1が未検証", "v2",
     lambda d: {"profile": {"schema_version": "1.1", "job_change_axis": {}}}, "未検証"),
    ("company_score.total が null", "v2",
     lambda d: d.update(company_score=_company_score(total=None, coverage=0, provisional=False, axes=[])), "company_score.total"),
    ("company_score が暫定", "v2",
     lambda d: d.update(company_score=_company_score(provisional=True, coverage=50)), "company_score.provisional"),
    ("スクリーニングでは満たした must が met=no", "v2", lambda d: _screening_case(d, 0), "求人検索では必須条件を満たす"),
    ("スクリーニングの result_index が範囲外", "v2", lambda d: _screening_case(d, 5), "result_index"),
]


class ValidatePassTest(unittest.TestCase):
    def test_valid_fixtures_have_no_errors_or_warnings(self):
        rows = [
            ("v1", _valid_fit(), {}),
            ("v2", _valid_v2_fit(), {"profile": _v2_profile()}),
            ("v2+company_score", _valid_v2_fit(company_score=_company_score()), {"profile": _v2_profile()}),
        ]
        for label, document, kwargs in rows:
            with self.subTest(label):
                result = vf.validate(document, **kwargs)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_bundled_example_passes(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        document = vf.load_fit_assessment(os.path.join(base, "assets", "fit_assessment_example.json"))
        profile = vf.load_fit_assessment(
            os.path.join(os.path.dirname(base), "job-change-support", "assets", "axis_example.json")
        )
        result = vf.validate(document, profile=profile)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_validate_does_not_mutate_input(self):
        d = _valid_v2_fit()
        snapshot = copy.deepcopy(d)
        vf.validate(d, profile=_v2_profile())
        self.assertEqual(d, snapshot)


class ValidateRulesTest(unittest.TestCase):
    def test_root_not_object_is_an_error(self):
        self.assertFalse(vf.validate(["x"]).ok)

    def test_error_rules(self):
        for label, base, mutate, expected in ERROR_ROWS:
            with self.subTest(label):
                result = _run(base, mutate)
                self.assertFalse(result.ok)
                self.assertTrue(any(expected in e for e in result.errors), msg=result.errors)

    def test_warn_rules(self):
        for label, base, mutate, expected in WARN_ROWS:
            with self.subTest(label):
                result = _run(base, mutate)
                self.assertTrue(any(expected in w for w in result.warnings), msg=result.warnings)

    def test_valid_variants_that_look_risky_pass(self):
        # met=unknown は evidence 空でよい（v1 fixture に含む）。交渉可能な未達は「条件付き推奨」、
        # 交渉不能な未達は「非推奨」で ERROR にならない。company_score の score=null も許容する。
        rows = [
            ("negotiable な未達 + 条件付き推奨", lambda d: (_unmet(d, negotiable=True), d["overall"].update(recommendation="条件付き推奨"))),
            ("交渉不能な未達 + 非推奨", lambda d: (_unmet(d), d["overall"].update(recommendation="非推奨"))),
            ("null score の志向は検査を飛ばす", lambda d: _dim(d, "aspiration_alignment").update(
                score=None, evidence=[{"source": "job_posting", "ref": "x", "note": "根拠"}])),
        ]
        for label, mutate in rows:
            with self.subTest(label):
                self.assertEqual(_run("v2", mutate).errors, [])


class CliTest(unittest.TestCase):
    def _write(self, obj, encoding="utf-8") -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding=encoding) as f:
            if isinstance(obj, str):
                f.write(obj)
            else:
                json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def test_exit_codes(self):
        invalid = _valid_fit()
        del invalid["schema_version"]
        extended = _v2_profile()
        extended["job_change_axis"]["conditions"].append({"id": "cond-added", "level": "must"})
        fit_v2 = self._write(_valid_v2_fit())
        rows = [
            ("valid", [self._write(_valid_fit())], 0),
            ("valid with BOM", [self._write(_valid_fit(), encoding="utf-8-sig")], 0),
            ("invalid", [self._write(invalid)], 1),
            ("broken JSON", [self._write("{ not valid json ")], 1),
            ("missing file", [os.path.join(tempfile.gettempdir(), "no-such-fit.json")], 1),
            ("--axis matches", [fit_v2, "--axis", self._write(_v2_profile())], 0),
            ("--profile alias", [fit_v2, "--profile", self._write(_v2_profile())], 0),
            ("--axis lacks a must", [fit_v2, "--axis", self._write(extended)], 1),
            ("--axis broken JSON", [fit_v2, "--axis", self._write("{")], 1),
        ]
        for label, argv, code in rows:
            with self.subTest(label), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(vf.main(argv), code)

    def test_json_output_keys(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            vf.main([self._write(_valid_fit()), "--json"])
        out = json.loads(buf.getvalue())
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(set(out), {"status", "error_count", "warning_count", "errors", "warnings"})


if __name__ == "__main__":
    unittest.main()
