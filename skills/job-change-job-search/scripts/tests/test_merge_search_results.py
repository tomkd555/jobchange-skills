"""merge_search_results.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_merge_search_results
"""
from __future__ import annotations

import contextlib
import glob
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import merge_search_results as msr  # noqa: E402

_PRIMARY = "job_search_results.partial-primary.json"
_LANES_1 = "job_search_results.partial-lanes-1.json"
_OUT = "job_search_results.json"


def _write(dir_path: str, name: str, obj) -> str:
    path = os.path.join(dir_path, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return path


def _result_item(
    company_name="架空テック株式会社",
    title="バックエンドエンジニア",
    url="https://hrmos.co/pages/kakuu/jobs/1",
    source_site="HRMOS",
    location="東京都渋谷区",
    salary_range="600万〜800万円",
    search_set="primary",
    lane=None,
    **overrides,
) -> dict:
    item = {
        "search_set": search_set,
        "company_name": company_name,
        "title": title,
        "url": url,
        "source_site": source_site,
        "location": location,
        "salary_range": salary_range,
        "remote_policy": None,
        "annual_holidays": None,
        "match_notes": "条件に合致する。",
        "quote": "年収600万〜800万円",
    }
    if lane is not None:
        item["lane"] = lane
    item.update(overrides)
    return item


def _partial(search_set="primary", lane=None, results=None, **overrides) -> dict:
    """partial ドキュメントの雛形を返す。derived で lane を渡すと該当レーンの derivations を1件用意する。"""
    doc = {
        "schema_version": "2.3",
        "search_id": "20260901-remote-be",
        "mode": "fuzzy",
        "executed_at": "2026-09-01",
        "conditions": {"roles": ["バックエンドエンジニア"]},
        "search_sets": {"primary": {"roles": ["バックエンドエンジニア"]}, "derivations": []},
        "results": results or [],
        "search_log": [{"query": "q", "source": "求人ボックス", "url": None, "fetched_at": None,
                        "hit_count": 1, "adopted_count": 1}],
        "coverage_notes": "",
        "open_questions": [],
    }
    if search_set == "derived" and lane is not None:
        doc["search_sets"]["derivations"] = [{"lane": lane, "queries": ["q"], "rationale": "隣接職種へ広げた"}]
    doc.update(overrides)
    return doc


def _profile(company="架空現職株式会社") -> dict:
    return {"career_history": [{"company": company, "period": "2020年4月〜現在"}], "basic": {}, "salary": {}}


def _company_profile(name: str, filled: int = 9) -> dict:
    metrics = {
        axis: {"value": (100 + i) if i < filled else None, "unit": unit, "source_url": "https://example.com/ir",
               "grade": "B", "as_of": "2026", "note": ""}
        for i, (axis, unit) in enumerate(msr._METRIC_UNITS.items())
    }
    return {"name": name, "aliases": [], "basics": {}, "metrics": metrics, "negative_checks": {},
            "recent_news": [], "open_questions": []}


def _setup(d, primary, lane_items=None, lane="adjacent_role", profile_names=None) -> None:
    """partial と企業プロファイルの batch を書く。profile_names 省略時は全企業ぶんを書く。"""
    _write(d, _PRIMARY, _partial(results=primary))
    if lane_items is not None:
        _write(d, _LANES_1, _partial(search_set="derived", lane=lane, results=lane_items))
    if profile_names is None:
        profile_names = {i["company_name"] for i in primary + (lane_items or [])}
    if profile_names:
        profiles = {msr.normalize_company_key(n): _company_profile(n) for n in profile_names}
        _write(d, "company_profiles.batch-1.json", {"schema_version": "2.3", "company_profiles": profiles})


def _merged(result) -> dict:
    with open(result.output_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _main_json(argv) -> tuple[int, str, dict]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = msr.main(argv + ["--json"])
    return code, out.getvalue(), json.loads(out.getvalue())


class MergeTest(unittest.TestCase):
    def test_merges_primary_and_lane_partial(self):
        with tempfile.TemporaryDirectory() as d:
            lane_item = _result_item(company_name="架空クラウド株式会社", title="SRE",
                                     url="https://findy-code.io/jobs/2", search_set="derived", lane="adjacent_role")
            _setup(d, [_result_item()], [lane_item])
            result = msr.merge(d, lanes=["adjacent_role", "region_widen"])
            self.assertTrue(result.ok, result.errors)
            merged = _merged(result)
            self.assertEqual(merged["schema_version"], "2.3")
            self.assertEqual([r["company_key"] for r in merged["results"]], ["架空テック", "架空クラウド"])
            self.assertEqual([x["lane"] for x in merged["search_sets"]["derivations"]], ["adjacent_role"])
            self.assertIsNone(merged["search_sets"]["exploration"])
            # 応答の無かったレーンは ERROR にせず報告だけする。
            self.assertEqual(result.missing_lanes, ["region_widen"])
            self.assertIn("レーン region_widen は検索担当が応答せず未実施", merged["coverage_notes"])
            # 統合しても partial・batch は残る。
            self.assertEqual(len(glob.glob(os.path.join(d, "job_search_results.partial-*.json"))), 2)
            self.assertEqual(len(glob.glob(os.path.join(d, "company_profiles.batch-*.json"))), 1)

    def test_dedup_keeps_expected_item(self):
        low = "https://xn--pckua2a7gp15o89zb.com/kakuu/jobs/1"
        high = "https://hrmos.co/pages/kakuu/jobs/9"
        mid1, mid2 = "https://green-japan.example.com/jobs/1", "https://green-japan.example.com/jobs/2"
        # (ラベル, primary の url 群, derived の url 群, 残る url, 残る search_set)
        rows = [
            ("主集合は出典順位が低くても派生に置き換えない", [low], [high], low, "primary"),
            ("同じ集合では出典順位が高い方を残す", [low, high], [], high, "primary"),
            ("同順位は primary を残す", [mid1], [mid2], mid1, "primary"),
        ]
        for label, primary_urls, lane_urls, expected_url, expected_set in rows:
            with self.subTest(label):
                with tempfile.TemporaryDirectory() as d:
                    def item(url, **kw):
                        return _result_item(company_name="架空データ株式会社", title="データアナリスト",
                                            location="大阪府大阪市北区", salary_range="500万〜700万円", url=url, **kw)

                    lane_items = [item(u, search_set="derived", lane="adjacent_role") for u in lane_urls]
                    _setup(d, [item(u) for u in primary_urls], lane_items or None)
                    result = msr.merge(d)
                    self.assertTrue(result.ok, result.errors)
                    results = _merged(result)["results"]
                    self.assertEqual(len(results), 1)
                    self.assertEqual(results[0]["url"], expected_url)
                    self.assertEqual(results[0]["search_set"], expected_set)

    def test_near_dup_keeps_both_and_notes(self):
        with tempfile.TemporaryDirectory() as d:
            a = _result_item(company_name="架空基盤株式会社", title="クラウド基盤エンジニア",
                             location="福岡県福岡市中央区")
            b = _result_item(company_name="架空基盤株式会社", title="クラウド基盤エンジニア候補",
                             location="福岡県福岡市中央区", url="https://hrmos.co/pages/kakuu/jobs/12",
                             search_set="derived", lane="adjacent_role")
            _setup(d, [a], [b])
            result = msr.merge(d)
            self.assertTrue(result.ok, result.errors)
            merged = _merged(result)
            self.assertEqual(len(merged["results"]), 2)
            self.assertIn("類似の可能性", merged["coverage_notes"])

    def test_current_employer_excluded_and_never_named(self):
        employer = "架空現職株式会社"
        with tempfile.TemporaryDirectory() as d:
            _setup(d, [_result_item(company_name=employer), _result_item()], profile_names=["架空テック株式会社"])
            result = msr.merge(d, profile=_profile(employer))
            self.assertTrue(result.ok, result.errors)
            self.assertEqual(result.excluded_count, 1)
            self.assertEqual(len(result.companies), 1)
            with open(result.output_path, "r", encoding="utf-8") as f:
                self.assertNotIn(employer, f.read())

    def test_list_companies_excludes_employer_groups_aliases_and_writes_nothing(self):
        employer = "架空現職株式会社"
        with tempfile.TemporaryDirectory() as d:
            _write(d, _PRIMARY, _partial(results=[
                _result_item(company_name=employer),
                _result_item(company_name="架空テック株式会社", url="https://hrmos.co/pages/kakuu/jobs/1"),
                _result_item(company_name="架空テック(株)", url="https://hrmos.co/pages/kakuu/jobs/2"),
            ]))
            result = msr.list_companies(d, _profile(employer))
            self.assertTrue(result.ok)
            self.assertEqual(result.excluded_count, 1)
            self.assertEqual(len(result.companies), 1)
            entry = result.companies[0]
            self.assertEqual(entry["company_key"], "架空テック")
            self.assertEqual(entry["aliases"], ["架空テック(株)"])
            self.assertEqual(len(entry["urls"]), 2)
            self.assertFalse(os.path.exists(os.path.join(d, _OUT)))

    def test_judgement_fields_stripped_with_warning(self):
        with tempfile.TemporaryDirectory() as d:
            item = _result_item(
                axis_judgements=[{"axis": "overtime_hours"}],
                classification="apply_candidate",
                classification_reasons=[{"axis": "overtime_hours", "reason": "残業が少ない"}],
                classification_override=None,
                slug="kakuu-tech",
                baseline_comparison={"axes": [], "overall": "better"},
            )
            _write(d, _PRIMARY, _partial(results=[item], screening={"screened_at": "2026-09-01"}))
            _write(d, "company_profiles.batch-1.json", {"company_profiles": {"架空テック": _company_profile("架空テック株式会社")}})
            result = msr.merge(d)
            self.assertTrue(result.ok, result.errors)
            self.assertTrue(result.warnings)
            merged = _merged(result)
            self.assertNotIn("screening", merged)
            for key in msr._JUDGEMENT_RESULT_KEYS:
                self.assertNotIn(key, merged["results"][0])
            self.assertNotIn("overall", merged["results"][0]["baseline_comparison"])

    def test_company_profile_handling(self):
        key = "架空テック"
        with self.subTest("batch が無いと ERROR で何も書かない"):
            with tempfile.TemporaryDirectory() as d:
                _setup(d, [_result_item()], profile_names=[])
                result = msr.merge(d)
                self.assertFalse(result.ok)
                self.assertFalse(os.path.exists(os.path.join(d, _OUT)))
        with self.subTest("stub_missing は9指標すべて null のスタブを補う"):
            with tempfile.TemporaryDirectory() as d:
                _setup(d, [_result_item()], profile_names=[])
                result = msr.merge(d, stub_missing=True)
                self.assertTrue(result.ok, result.errors)
                merged = _merged(result)
                metrics = merged["company_profiles"][key]["metrics"]
                self.assertEqual(len(metrics), 9)
                for axis, unit in msr._METRIC_UNITS.items():
                    self.assertIsNone(metrics[axis]["value"])
                    self.assertEqual(metrics[axis]["unit"], unit)
                self.assertIn("企業情報の未収集: 架空テック株式会社", merged["open_questions"])
        with self.subTest("重複は metrics の充足数が多い方を残す"):
            with tempfile.TemporaryDirectory() as d:
                _setup(d, [_result_item()], profile_names=[])
                for n, filled in ((1, 3), (2, 9)):
                    _write(d, f"company_profiles.batch-{n}.json",
                           {"company_profiles": {key: _company_profile("架空テック株式会社", filled=filled)}})
                result = msr.merge(d)
                self.assertTrue(result.ok, result.errors)
                self.assertTrue(any(key in w for w in result.warnings))
                metrics = _merged(result)["company_profiles"][key]["metrics"]
                self.assertEqual(sum(1 for m in metrics.values() if m["value"] is not None), 9)

    def test_merge_errors_write_nothing(self):
        # (ラベル, {ファイル名: partial}, 期待する ERROR の部分文字列)
        rows = [
            ("primary が無い", {_LANES_1: _partial(search_set="derived", lane="adjacent_role")}, "primary"),
            ("partial が無い", {}, "partials"),
            ("search_id の不一致",
             {_PRIMARY: _partial(search_id="20260901-a"), _LANES_1: _partial(search_id="20260902-b")}, "search_id"),
            ("schema_version が 2.3 でない", {_PRIMARY: _partial(schema_version="2.2")}, "schema_version"),
            ("レーンの重複",
             {_PRIMARY: _partial(),
              _LANES_1: _partial(search_set="derived", lane="adjacent_role"),
              "job_search_results.partial-lanes-2.json": _partial(search_set="derived", lane="adjacent_role")},
             "adjacent_role"),
        ]
        for label, files, expected in rows:
            with self.subTest(label):
                with tempfile.TemporaryDirectory() as d:
                    for name, doc in files.items():
                        _write(d, name, doc)
                    result = msr.merge(d)
                    self.assertFalse(result.ok)
                    self.assertTrue(any(expected in e for e in result.errors), result.errors)
                    self.assertIsNone(result.output_path)
                    self.assertFalse(os.path.exists(os.path.join(d, _OUT)))

    def test_cleanup(self):
        with tempfile.TemporaryDirectory() as d:
            _setup(d, [_result_item()])
            result = msr.cleanup(d)
            self.assertFalse(result.ok)
            self.assertEqual(len(glob.glob(os.path.join(d, "job_search_results.partial-*.json"))), 1)
            self.assertTrue(msr.merge(d).ok)
            result = msr.cleanup(d)
            self.assertTrue(result.ok, result.errors)
            self.assertEqual(glob.glob(os.path.join(d, "job_search_results.partial-*.json")), [])
            self.assertEqual(glob.glob(os.path.join(d, "company_profiles.batch-*.json")), [])
            self.assertTrue(os.path.isfile(os.path.join(d, _OUT)))


class CliTest(unittest.TestCase):
    def test_exit_codes_json_keys_and_employer_not_echoed(self):
        employer = "架空現職株式会社"
        with tempfile.TemporaryDirectory() as d:
            _setup(d, [_result_item(company_name=employer), _result_item()], profile_names=["架空テック株式会社"])
            profile_path = _write(d, "profile.json", _profile(employer))
            code, text, payload = _main_json([d, "--profile", profile_path])
            self.assertEqual(code, 0)
            self.assertEqual(payload["status"], "PASS")
            self.assertEqual(payload["excluded_count"], 1)
            self.assertNotIn(employer, text)
            self.assertEqual(
                set(payload),
                {"status", "errors", "warnings", "excluded_count", "companies", "missing_lanes", "output_path"},
            )
        with tempfile.TemporaryDirectory() as d:
            code, _, payload = _main_json([d])
            self.assertEqual(code, 1)
            self.assertEqual(payload["status"], "FAIL")
            self.assertIsNone(payload["output_path"])
        with tempfile.TemporaryDirectory() as d:
            code, _, payload = _main_json([d, "--profile", os.path.join(d, "missing.json")])
            self.assertEqual(code, 1)
            self.assertEqual(payload["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
