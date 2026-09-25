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


def _base_doc(**overrides) -> dict:
    doc = {
        "schema_version": "2.3",
        "search_id": "20260901-remote-be",
        "mode": "fuzzy",
        "executed_at": "2026-09-01",
        "conditions": {"roles": ["バックエンドエンジニア"]},
        "search_sets": {"primary": {"roles": ["バックエンドエンジニア"]}, "derivations": []},
        "results": [],
        "search_log": [
            {
                "query": "バックエンドエンジニア リモート",
                "source": "求人ボックス",
                "url": "https://example.com/search",
                "fetched_at": "2026-09-01",
                "hit_count": 10,
                "adopted_count": 1,
            }
        ],
        "coverage_notes": "",
        "open_questions": [],
    }
    doc.update(overrides)
    return doc


def _partial(search_set="primary", lane=None, results=None, derivations=None, **overrides) -> dict:
    """partial ドキュメントの雛形を返す。lane を渡すと該当レーンの derivations を1件だけ用意する。"""
    doc = _base_doc()
    if results is not None:
        doc["results"] = results
    if derivations is not None:
        doc["search_sets"]["derivations"] = derivations
    elif search_set == "derived" and lane is not None:
        doc["search_sets"]["derivations"] = [
            {"lane": lane, "queries": ["q"], "rationale": "隣接職種へ広げた"}
        ]
    doc.update(overrides)
    return doc


def _profile(company="架空現職株式会社") -> dict:
    return {
        "career_history": [{"company": company, "period": "2020年4月〜現在"}],
        "basic": {},
        "salary": {},
    }


def _company_profile(name: str, filled: int = 9) -> dict:
    metrics = {}
    for i, (axis, unit) in enumerate(msr._METRIC_UNITS.items()):
        metrics[axis] = {
            "value": (100 + i) if i < filled else None,
            "unit": unit,
            "source_url": "https://example.com/ir",
            "grade": "B",
            "as_of": "2026",
            "note": "",
        }
    return {
        "name": name,
        "aliases": [],
        "basics": {},
        "metrics": metrics,
        "negative_checks": {},
        "recent_news": [],
        "open_questions": [],
    }


class MergeTests(unittest.TestCase):
    def test_merges_primary_and_lane_partial(self):
        with tempfile.TemporaryDirectory() as d:
            primary_item = _result_item(company_name="架空テック株式会社")
            lane_item = _result_item(
                company_name="架空クラウド株式会社",
                title="SRE",
                url="https://findy-code.io/jobs/2",
                search_set="derived",
                lane="adjacent_role",
            )
            _write(d, "job_search_results.partial-primary.json", _partial(results=[primary_item]))
            _write(
                d,
                "job_search_results.partial-lanes-1.json",
                _partial(search_set="derived", lane="adjacent_role", results=[lane_item]),
            )
            _write(
                d,
                "company_profiles.batch-1.json",
                {
                    "schema_version": "2.3",
                    "company_profiles": {
                        "架空テック": _company_profile("架空テック株式会社"),
                        "架空クラウド": _company_profile("架空クラウド株式会社"),
                    },
                },
            )

            result = msr.merge(d)

            self.assertTrue(result.ok, result.errors)
            self.assertTrue(os.path.exists(result.output_path))
            with open(result.output_path, "r", encoding="utf-8") as f:
                merged = json.load(f)
            self.assertEqual(merged["schema_version"], "2.3")
            self.assertEqual(len(merged["results"]), 2)
            self.assertEqual(len(merged["search_sets"]["derivations"]), 1)
            self.assertEqual(merged["search_sets"]["derivations"][0]["lane"], "adjacent_role")
            self.assertIsNone(merged["search_sets"]["exploration"])

    def test_missing_primary_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            _write(
                d,
                "job_search_results.partial-lanes-1.json",
                _partial(search_set="derived", lane="adjacent_role", results=[_result_item()]),
            )
            result = msr.merge(d)
            self.assertFalse(result.ok)
            self.assertTrue(any("primary" in e for e in result.errors))
            self.assertIsNone(result.output_path)

    def test_no_partials_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            result = msr.merge(d)
            self.assertFalse(result.ok)
            self.assertIsNone(result.output_path)

    def test_search_id_mismatch_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "job_search_results.partial-primary.json", _partial(search_id="20260901-a"))
            _write(
                d,
                "job_search_results.partial-lanes-1.json",
                _partial(search_id="20260902-b", search_set="derived", lane="adjacent_role"),
            )
            result = msr.merge(d)
            self.assertFalse(result.ok)
            self.assertTrue(any("search_id" in e for e in result.errors))

    def test_schema_version_other_than_2_3_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "job_search_results.partial-primary.json", _partial(schema_version="2.2"))
            result = msr.merge(d)
            self.assertFalse(result.ok)
            self.assertTrue(any("schema_version" in e for e in result.errors))

    def test_duplicate_lane_across_partials_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "job_search_results.partial-primary.json", _partial())
            _write(
                d,
                "job_search_results.partial-lanes-1.json",
                _partial(search_set="derived", lane="adjacent_role"),
            )
            _write(
                d,
                "job_search_results.partial-lanes-2.json",
                _partial(search_set="derived", lane="adjacent_role"),
            )
            result = msr.merge(d)
            self.assertFalse(result.ok)
            self.assertTrue(any("adjacent_role" in e for e in result.errors))

    def test_exact_dup_keeps_lower_rank_source(self):
        with tempfile.TemporaryDirectory() as d:
            low_rank_primary = _result_item(
                company_name="架空データ株式会社",
                title="データアナリスト",
                location="大阪府大阪市北区",
                salary_range="500万〜700万円",
                url="https://xn--pckua2a7gp15o89zb.com/kakuu/jobs/1",
                source_site="求人ボックス",
            )
            high_rank_lane = _result_item(
                company_name="架空データ株式会社",
                title="データアナリスト",
                location="大阪府大阪市北区",
                salary_range="500万〜700万円",
                url="https://hrmos.co/pages/kakuu/jobs/9",
                source_site="HRMOS",
                search_set="derived",
                lane="direct_careers",
            )
            _write(d, "job_search_results.partial-primary.json", _partial(results=[low_rank_primary]))
            _write(
                d,
                "job_search_results.partial-lanes-1.json",
                _partial(search_set="derived", lane="direct_careers", results=[high_rank_lane]),
            )
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {"架空データ": _company_profile("架空データ株式会社")}},
            )
            result = msr.merge(d)
            self.assertTrue(result.ok, result.errors)
            with open(result.output_path, "r", encoding="utf-8") as f:
                merged = json.load(f)
            self.assertEqual(len(merged["results"]), 1)
            # 主集合の求人は、出典の順位が低くても派生の求人に置き換えない。
            self.assertEqual(merged["results"][0]["search_set"], "primary")
            self.assertEqual(merged["results"][0]["url"], "https://xn--pckua2a7gp15o89zb.com/kakuu/jobs/1")

    def test_exact_dup_same_set_keeps_lower_rank_source(self):
        with tempfile.TemporaryDirectory() as d:
            low_rank = _result_item(
                company_name="架空データ株式会社",
                title="データアナリスト",
                location="大阪府大阪市北区",
                salary_range="500万〜700万円",
                url="https://xn--pckua2a7gp15o89zb.com/kakuu/jobs/1",
                source_site="求人ボックス",
            )
            high_rank = _result_item(
                company_name="架空データ株式会社",
                title="データアナリスト",
                location="大阪府大阪市北区",
                salary_range="500万〜700万円",
                url="https://hrmos.co/pages/kakuu/jobs/9",
                source_site="HRMOS",
            )
            _write(d, "job_search_results.partial-primary.json", _partial(results=[low_rank, high_rank]))
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {"架空データ": _company_profile("架空データ株式会社")}},
            )
            result = msr.merge(d)
            self.assertTrue(result.ok, result.errors)
            with open(result.output_path, "r", encoding="utf-8") as f:
                merged = json.load(f)
            self.assertEqual(len(merged["results"]), 1)
            self.assertEqual(merged["results"][0]["url"], "https://hrmos.co/pages/kakuu/jobs/9")

    def test_exact_dup_tie_keeps_primary(self):
        with tempfile.TemporaryDirectory() as d:
            primary_item = _result_item(
                company_name="架空グリーン株式会社",
                title="フロントエンドエンジニア",
                location="東京都新宿区",
                salary_range="550万〜750万円",
                url="https://green-japan.example.com/jobs/1",
                source_site="Green",
            )
            lane_item = _result_item(
                company_name="架空グリーン株式会社",
                title="フロントエンドエンジニア",
                location="東京都新宿区",
                salary_range="550万〜750万円",
                url="https://green-japan.example.com/jobs/2",
                source_site="Green",
                search_set="derived",
                lane="adjacent_role",
            )
            _write(d, "job_search_results.partial-primary.json", _partial(results=[primary_item]))
            _write(
                d,
                "job_search_results.partial-lanes-1.json",
                _partial(search_set="derived", lane="adjacent_role", results=[lane_item]),
            )
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {"架空グリーン": _company_profile("架空グリーン株式会社")}},
            )
            result = msr.merge(d)
            self.assertTrue(result.ok, result.errors)
            with open(result.output_path, "r", encoding="utf-8") as f:
                merged = json.load(f)
            self.assertEqual(len(merged["results"]), 1)
            self.assertEqual(merged["results"][0]["url"], "https://green-japan.example.com/jobs/1")

    def test_near_dup_listed_in_coverage_notes_and_both_kept(self):
        with tempfile.TemporaryDirectory() as d:
            item_a = _result_item(
                company_name="架空基盤株式会社",
                title="クラウド基盤エンジニア",
                location="福岡県福岡市中央区",
                salary_range="600万〜850万円",
                url="https://hrmos.co/pages/kakuu/jobs/11",
            )
            item_b = _result_item(
                company_name="架空基盤株式会社",
                title="クラウド基盤エンジニア候補",
                location="福岡県福岡市中央区",
                salary_range="600万〜850万円",
                url="https://hrmos.co/pages/kakuu/jobs/12",
                search_set="derived",
                lane="adjacent_role",
            )
            _write(d, "job_search_results.partial-primary.json", _partial(results=[item_a]))
            _write(
                d,
                "job_search_results.partial-lanes-1.json",
                _partial(search_set="derived", lane="adjacent_role", results=[item_b]),
            )
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {"架空基盤": _company_profile("架空基盤株式会社")}},
            )
            result = msr.merge(d)
            self.assertTrue(result.ok, result.errors)
            with open(result.output_path, "r", encoding="utf-8") as f:
                merged = json.load(f)
            self.assertEqual(len(merged["results"]), 2)
            self.assertTrue(any("類似の可能性" in line for line in merged["coverage_notes"].splitlines()))

    def test_current_employer_excluded_and_never_named(self):
        with tempfile.TemporaryDirectory() as d:
            employer_name = "架空現職株式会社"
            employer_item = _result_item(company_name=employer_name, title="採用中ポジション")
            other_item = _result_item(company_name="架空テック株式会社")
            _write(
                d,
                "job_search_results.partial-primary.json",
                _partial(results=[employer_item, other_item]),
            )
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {"架空テック": _company_profile("架空テック株式会社")}},
            )
            result = msr.merge(d, profile=_profile(employer_name))
            self.assertTrue(result.ok, result.errors)
            self.assertEqual(result.excluded_count, 1)
            self.assertEqual(len(result.companies), 1)
            with open(result.output_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
            self.assertNotIn(employer_name, raw_text)

    def test_current_employer_excluded_via_cli_json(self):
        with tempfile.TemporaryDirectory() as d:
            employer_name = "架空現職株式会社"
            employer_item = _result_item(company_name=employer_name, title="採用中ポジション")
            other_item = _result_item(company_name="架空テック株式会社")
            _write(
                d,
                "job_search_results.partial-primary.json",
                _partial(results=[employer_item, other_item]),
            )
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {"架空テック": _company_profile("架空テック株式会社")}},
            )
            profile_path = _write(d, "profile.json", _profile(employer_name))

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = msr.main([d, "--profile", profile_path, "--json"])
            output_text = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertNotIn(employer_name, output_text)
            payload = json.loads(output_text)
            self.assertEqual(payload["excluded_count"], 1)
            self.assertEqual(payload["status"], "PASS")

    def test_list_companies_excludes_current_employer_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            employer_name = "架空現職株式会社"
            employer_item = _result_item(company_name=employer_name)
            other_item = _result_item(company_name="架空テック株式会社")
            _write(
                d,
                "job_search_results.partial-primary.json",
                _partial(results=[employer_item, other_item]),
            )
            result = msr.list_companies(d, _profile(employer_name))
            self.assertTrue(result.ok)
            self.assertEqual(result.excluded_count, 1)
            self.assertEqual(len(result.companies), 1)
            self.assertEqual(result.companies[0]["company_key"], msr.normalize_company_key("架空テック株式会社"))
            self.assertFalse(os.path.exists(os.path.join(d, "job_search_results.json")))

    def test_list_companies_collects_aliases_and_urls(self):
        with tempfile.TemporaryDirectory() as d:
            item_a = _result_item(company_name="架空テック株式会社", url="https://hrmos.co/pages/kakuu/jobs/1")
            item_b = _result_item(company_name="架空テック(株)", url="https://hrmos.co/pages/kakuu/jobs/2")
            _write(d, "job_search_results.partial-primary.json", _partial(results=[item_a, item_b]))
            result = msr.list_companies(d)
            self.assertEqual(len(result.companies), 1)
            entry = result.companies[0]
            self.assertIn("架空テック(株)", entry["aliases"])
            self.assertEqual(len(entry["urls"]), 2)

    def test_company_key_assigned(self):
        with tempfile.TemporaryDirectory() as d:
            item = _result_item(company_name="架空テック株式会社")
            _write(d, "job_search_results.partial-primary.json", _partial(results=[item]))
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {"架空テック": _company_profile("架空テック株式会社")}},
            )
            result = msr.merge(d)
            self.assertTrue(result.ok, result.errors)
            with open(result.output_path, "r", encoding="utf-8") as f:
                merged = json.load(f)
            self.assertEqual(merged["results"][0]["company_key"], msr.normalize_company_key("架空テック株式会社"))

    def test_missing_company_profile_is_error_and_nothing_written(self):
        with tempfile.TemporaryDirectory() as d:
            item = _result_item(company_name="架空テック株式会社")
            _write(d, "job_search_results.partial-primary.json", _partial(results=[item]))
            result = msr.merge(d)
            self.assertFalse(result.ok)
            self.assertFalse(os.path.exists(os.path.join(d, "job_search_results.json")))

    def test_stub_missing_writes_full_stub(self):
        with tempfile.TemporaryDirectory() as d:
            item = _result_item(company_name="架空テック株式会社")
            _write(d, "job_search_results.partial-primary.json", _partial(results=[item]))
            result = msr.merge(d, stub_missing=True)
            self.assertTrue(result.ok, result.errors)
            with open(result.output_path, "r", encoding="utf-8") as f:
                merged = json.load(f)
            key = msr.normalize_company_key("架空テック株式会社")
            stub = merged["company_profiles"][key]
            self.assertEqual(len(stub["metrics"]), 9)
            for axis, unit in msr._METRIC_UNITS.items():
                self.assertIsNone(stub["metrics"][axis]["value"])
                self.assertEqual(stub["metrics"][axis]["unit"], unit)
            self.assertIn("企業情報の未収集: 架空テック株式会社", merged["open_questions"])

    def test_conflicting_profiles_keep_more_complete_one(self):
        with tempfile.TemporaryDirectory() as d:
            item = _result_item(company_name="架空テック株式会社")
            _write(d, "job_search_results.partial-primary.json", _partial(results=[item]))
            key = "架空テック"
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {key: _company_profile("架空テック株式会社", filled=3)}},
            )
            _write(
                d,
                "company_profiles.batch-2.json",
                {"schema_version": "2.3", "company_profiles": {key: _company_profile("架空テック株式会社", filled=9)}},
            )
            result = msr.merge(d)
            self.assertTrue(result.ok, result.errors)
            self.assertTrue(any("架空テック" in w for w in result.warnings))
            with open(result.output_path, "r", encoding="utf-8") as f:
                merged = json.load(f)
            merged_key = msr.normalize_company_key("架空テック株式会社")
            filled_count = sum(
                1 for m in merged["company_profiles"][merged_key]["metrics"].values() if m["value"] is not None
            )
            self.assertEqual(filled_count, 9)

    def test_judgement_fields_stripped_with_warning(self):
        with tempfile.TemporaryDirectory() as d:
            item = _result_item(
                company_name="架空テック株式会社",
                axis_judgements=[{"axis": "overtime_hours", "level": "want", "judgement": "meets"}],
                classification="apply_candidate",
                classification_reasons=[{"axis": "overtime_hours", "reason": "残業が少ない"}],
                slug="kakuu-tech",
                baseline_comparison={"axes": [], "overall": "better"},
            )
            doc = _partial(results=[item], screening={"screened_at": "2026-09-01"})
            _write(d, "job_search_results.partial-primary.json", doc)
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {"架空テック": _company_profile("架空テック株式会社")}},
            )
            result = msr.merge(d)
            self.assertTrue(result.ok, result.errors)
            self.assertTrue(result.warnings)
            with open(result.output_path, "r", encoding="utf-8") as f:
                merged = json.load(f)
            self.assertNotIn("screening", merged)
            merged_item = merged["results"][0]
            for key in ("axis_judgements", "classification", "classification_reasons", "slug"):
                self.assertNotIn(key, merged_item)
            self.assertNotIn("overall", merged_item["baseline_comparison"])

    def test_missing_lane_reported_but_not_error(self):
        with tempfile.TemporaryDirectory() as d:
            item = _result_item(company_name="架空テック株式会社")
            _write(d, "job_search_results.partial-primary.json", _partial(results=[item]))
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {"架空テック": _company_profile("架空テック株式会社")}},
            )
            result = msr.merge(d, lanes=["region_widen"])
            self.assertTrue(result.ok, result.errors)
            self.assertEqual(result.missing_lanes, ["region_widen"])
            with open(result.output_path, "r", encoding="utf-8") as f:
                merged = json.load(f)
            self.assertIn("レーン region_widen は検索担当が応答せず未実施", merged["coverage_notes"])

    def test_partials_kept_after_merge(self):
        with tempfile.TemporaryDirectory() as d:
            item = _result_item(company_name="架空テック株式会社")
            _write(d, "job_search_results.partial-primary.json", _partial(results=[item]))
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {"架空テック": _company_profile("架空テック株式会社")}},
            )
            result = msr.merge(d)
            self.assertTrue(result.ok, result.errors)
            self.assertEqual(len(glob.glob(os.path.join(d, "job_search_results.partial-*.json"))), 1)
            self.assertEqual(len(glob.glob(os.path.join(d, "company_profiles.batch-*.json"))), 1)

    def test_cleanup_deletes_partials_after_merge(self):
        with tempfile.TemporaryDirectory() as d:
            item = _result_item(company_name="架空テック株式会社")
            _write(d, "job_search_results.partial-primary.json", _partial(results=[item]))
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {"架空テック": _company_profile("架空テック株式会社")}},
            )
            self.assertTrue(msr.merge(d).ok)
            result = msr.cleanup(d)
            self.assertTrue(result.ok, result.errors)
            self.assertEqual(glob.glob(os.path.join(d, "job_search_results.partial-*.json")), [])
            self.assertEqual(glob.glob(os.path.join(d, "company_profiles.batch-*.json")), [])
            self.assertTrue(os.path.isfile(os.path.join(d, "job_search_results.json")))

    def test_cleanup_without_merged_file_is_error_and_keeps_partials(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "job_search_results.partial-primary.json", _partial(results=[]))
            result = msr.cleanup(d)
            self.assertFalse(result.ok)
            self.assertEqual(len(glob.glob(os.path.join(d, "job_search_results.partial-*.json"))), 1)

    def test_cli_exit_codes_and_json_shape(self):
        with tempfile.TemporaryDirectory() as d:
            item = _result_item(company_name="架空テック株式会社")
            _write(d, "job_search_results.partial-primary.json", _partial(results=[item]))
            _write(
                d,
                "company_profiles.batch-1.json",
                {"schema_version": "2.3", "company_profiles": {"架空テック": _company_profile("架空テック株式会社")}},
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = msr.main([d, "--json"])
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(
                set(payload.keys()),
                {"status", "errors", "warnings", "excluded_count", "companies", "missing_lanes", "output_path"},
            )
            self.assertEqual(payload["status"], "PASS")

        with tempfile.TemporaryDirectory() as d:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = msr.main([d, "--json"])
            self.assertEqual(exit_code, 1)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["status"], "FAIL")
            self.assertIsNone(payload["output_path"])


if __name__ == "__main__":
    unittest.main()
