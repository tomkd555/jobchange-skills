"""validate_job_search_results.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
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

import validate_job_search_results as v  # noqa: E402


def _legal(**over):
    base = {
        "scope_of_change_duties": {"result": "stated", "quote": "業務の変更の範囲"},
        "scope_of_change_location": {"result": "stated", "quote": "勤務地の変更の範囲"},
        "contract_renewal_cap": {"result": "not_applicable", "quote": "正社員"},
        "posted_at": {"result": "stated", "quote": "掲載日 2026/10/20"},
        "salary_range": {"result": "stated", "quote": "年収 650 万〜900 万円"},
    }
    base.update(over)
    return base


def make_result(**over):
    r = {
        "title": "インフラエンジニア",
        "company_name": "アクメクラウド株式会社",
        "url": "https://example.com/jobs/1",
        "source_site": "求人ボックス",
        "read_via": "webfetch",
        "quote": "年収 650 万〜900 万円",
        "salary_range": "650万〜900万円",
        "location": "東京都",
        "remote_policy": "フルリモート可",
        "employment_type": "正社員",
        "annual_holidays": 125,
        "posted_at": "2026-10-20",
        "lane": None,
        "legal_check": _legal(),
        "must_match": [
            {"condition_id": "c001", "result": "meets", "basis": "下限 650 万円"},
            {"condition_id": "c002", "result": "unknown", "basis": None},
        ],
        "match_notes": "年収を満たす。",
        "considering": True,
    }
    r.update(over)
    return r


def make_doc():
    return {
        "schema_version": "3.0",
        "search_id": "20261025-remote-infra",
        "mode": "fuzzy",
        "executed_at": "2026-10-25",
        "conditions": [
            {"condition_id": "c001", "kind": "salary_min", "text": "年収 600 万円以上", "level": "must"},
            {"condition_id": "c002", "kind": "remote", "text": "リモート中心", "level": "must"},
            {"condition_id": "c004", "kind": "industry", "text": "SaaS", "level": "want"},
        ],
        "baseline": None,
        "derivations": [
            {"lane": "better_salary", "changed_conditions": ["c001"], "rationale": "下限を上げる"},
        ],
        "results": [make_result(), make_result(title="SRE", lane="better_salary")],
        "search_log": [
            {"query": "q1", "source": "求人ボックス", "url": "https://example.com/s", "fetched_at": "2026-10-25",
             "hit_count": 10, "adopted_count": 1, "lane": None},
            {"query": "q2", "source": "chrome", "url": None, "fetched_at": None,
             "hit_count": None, "adopted_count": None, "lane": "better_salary"},
        ],
        "coverage_notes": "1 ページ目のみ",
        "open_questions": [],
    }


class ValidateTest(unittest.TestCase):
    def check(self, mutate, *, error=None, warn=None):
        """mutate を適用した文書を検証し、指定した部分文字列が ERROR / WARN に出ることを確かめる。

        error / warn が None のときは、その種別が 0 件であることを確かめる。
        """
        doc = make_doc()
        mutate(doc)
        res = v.validate(doc)
        if error is None:
            self.assertEqual(res.errors, [], res.errors)
        else:
            self.assertTrue(any(error in e for e in res.errors), res.errors)
        if warn is None:
            self.assertEqual(res.warnings, [], res.warnings)
        else:
            self.assertTrue(any(warn in w for w in res.warnings), res.warnings)
        return res

    def test_valid(self):
        res = v.validate(make_doc())
        self.assertEqual((res.errors, res.warnings), ([], []))

    def test_example_asset_is_valid(self):
        skill_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        res = v.validate(v.load_json(os.path.join(skill_dir, "assets", "job_search_results_example.json")))
        self.assertEqual((res.errors, res.warnings), ([], []))

    # ---- ルート ERROR ----
    def test_root_not_object(self):
        self.assertFalse(v.validate([]).ok)

    def test_missing_required_root_field(self):
        for key in ("schema_version", "search_id", "mode", "executed_at", "conditions",
                    "derivations", "results", "search_log"):
            with self.subTest(key=key):
                doc = make_doc()
                del doc[key]
                self.assertTrue(any(e.startswith(f"[ERROR] {key}:") for e in v.validate(doc).errors))

    def test_root_wrong_type(self):
        self.check(lambda d: d.update(results={}), error="results: list")

    def test_search_id_malformed(self):
        self.check(lambda d: d.update(search_id="Remote_Infra"), error="search_id")

    def test_search_id_date_mismatch(self):
        self.check(lambda d: d.update(search_id="20261024-remote-infra"), error="日付部分")

    def test_mode_invalid(self):
        self.check(lambda d: d.update(mode="exact"), error="mode")

    def test_executed_at_invalid(self):
        self.check(lambda d: d.update(executed_at="2026-13-45", search_id="20261345-x"), error="executed_at")

    def test_baseline_malformed(self):
        self.check(lambda d: d.update(baseline="x"), error="baseline", warn="fuzzy では baseline")
        self.check(lambda d: d.update(baseline={"posting_id": "bad id"}, mode="similar_better"),
                   error="baseline.posting_id")

    def test_baseline_valid_under_similar_better(self):
        self.check(lambda d: d.update(baseline={"posting_id": "アクメクラウド-20261020-01"}, mode="similar_better"))

    def test_derivation_errors(self):
        self.check(lambda d: d["derivations"].append("x"), error="derivations[1]")
        self.check(lambda d: d["derivations"][0].update(lane="nope"), error="derivations[0].lane")
        self.check(lambda d: d["derivations"].append(copy.deepcopy(d["derivations"][0])), error="重複")
        self.check(lambda d: d["derivations"][0].update(changed_conditions=["", "c1"]), error="changed_conditions")
        self.check(lambda d: d["derivations"][0].update(rationale=" "), error="rationale")

    # ---- results ERROR ----
    def test_result_missing_key(self):
        for key in ("title", "company_name", "url", "source_site", "read_via", "quote", "salary_range",
                    "location", "remote_policy", "employment_type", "annual_holidays", "posted_at",
                    "lane", "legal_check", "must_match", "match_notes", "considering"):
            with self.subTest(key=key):
                doc = make_doc()
                del doc["results"][0][key]
                self.assertTrue(any(f"results[0].{key}" in e for e in v.validate(doc).errors))

    def test_result_field_rules(self):
        self.check(lambda d: d["results"][0].update(url="ftp://x"), error="results[0].url")
        self.check(lambda d: d["results"][0].update(read_via="curl"), error="read_via")
        self.check(lambda d: d["results"][0].update(title=""), error="results[0].title")
        self.check(lambda d: d["results"][0].update(location=3), error="results[0].location")
        self.check(lambda d: d["results"][0].update(annual_holidays="125"), error="annual_holidays")
        self.check(lambda d: d["results"][0].update(annual_holidays=True), error="annual_holidays")
        self.check(lambda d: d["results"][0].update(posted_at="2026/10/20"), error="posted_at")
        self.check(lambda d: d["results"][0].update(considering="yes"), error="considering")

    def test_result_nullable_fields_accept_null(self):
        def nullify(d):
            d["results"][0].update(salary_range=None, location=None, remote_policy=None,
                                   employment_type=None, annual_holidays=None, posted_at=None)
        self.check(nullify)

    def test_result_lane_absent_from_derivations(self):
        self.check(lambda d: d["results"][0].update(lane="remote_widen"), error="results[0].lane")

    def test_result_lane_without_search_log(self):
        self.check(lambda d: d["search_log"].pop(), error="lane better_salary を持つ search_log が無い")

    # ---- legal_check ----
    def test_legal_check_key_set(self):
        self.check(lambda d: d["results"][0]["legal_check"].pop("posted_at"), error="legal_check.posted_at")
        self.check(lambda d: d["results"][0]["legal_check"].update(extra={"result": "stated", "quote": "x"}),
                   error="仕様に無いキー")

    def test_legal_check_item_rules(self):
        self.check(lambda d: d["results"][0]["legal_check"].update(
            posted_at={"result": "maybe", "quote": "x"}), error="legal_check.posted_at.result")
        self.check(lambda d: d["results"][0]["legal_check"].update(
            posted_at={"result": "stated", "quote": ""}), error="quote")
        self.check(lambda d: d["results"][0]["legal_check"].update(posted_at="stated"),
                   error="legal_check.posted_at")

    def test_legal_check_two_missing_warns(self):
        def two_missing(d):
            d["results"][0]["legal_check"].update(
                scope_of_change_duties={"result": "missing", "quote": None},
                scope_of_change_location={"result": "missing", "quote": None})
        self.check(two_missing, warn="missing が 2 件以上")

    def test_legal_check_one_missing_is_quiet(self):
        self.check(lambda d: d["results"][0]["legal_check"].update(
            scope_of_change_duties={"result": "missing", "quote": None}))

    # ---- must_match ----
    def test_must_match_coverage(self):
        self.check(lambda d: d["results"][0]["must_match"].pop(), error="must 条件 c002")
        self.check(lambda d: d["results"][0]["must_match"].append(
            {"condition_id": "c004", "result": "unknown", "basis": None}), error="c004")
        self.check(lambda d: d["results"][0]["must_match"].append(
            {"condition_id": "c001", "result": "unknown", "basis": None}), error="重複")

    def test_must_match_item_rules(self):
        self.check(lambda d: d["results"][0]["must_match"][0].update(result="ok"), error="must_match[0].result")
        self.check(lambda d: d["results"][0]["must_match"][0].update(basis=""), error="basis")
        self.check(lambda d: d["results"][0]["must_match"][0].update(result="not_meets", basis=None), error="basis")

    # ---- search_log ----
    def test_search_log_empty(self):
        self.check(lambda d: d.update(search_log=[], results=[make_result()]), error="search_log")

    def test_search_log_element_rules(self):
        self.check(lambda d: d["search_log"][0].pop("hit_count"), error="search_log[0].hit_count")
        self.check(lambda d: d["search_log"][0].update(query=""), error="query")
        self.check(lambda d: d["search_log"][0].update(source=""), error="source")
        self.check(lambda d: d["search_log"][0].update(url="ftp://x"), error="search_log[0].url")
        self.check(lambda d: d["search_log"][0].update(fetched_at="x"), error="fetched_at")
        self.check(lambda d: d["search_log"][0].update(hit_count=-1), error="hit_count")
        self.check(lambda d: d["search_log"][0].update(adopted_count=1.5), error="adopted_count")
        self.check(lambda d: d["search_log"][0].update(lane="remote_widen"), error="search_log[0].lane")

    # ---- WARN ----
    def test_warn_unknown_schema_version(self):
        self.check(lambda d: d.update(schema_version="2.3"), warn="schema_version")

    def test_warn_empty_conditions(self):
        def empty(d):
            d["conditions"] = []
            for r in d["results"]:
                r["must_match"] = []
        self.check(empty, warn="conditions が空")

    def test_warn_empty_results(self):
        self.check(lambda d: d.update(results=[]), warn="results が空")

    def test_warn_baseline_missing_under_similar_better(self):
        self.check(lambda d: d.update(mode="similar_better"), warn="baseline が必要")

    def test_warn_too_many_queries_for_lane(self):
        def many(d):
            d["search_log"] += [dict(d["search_log"][1]) for _ in range(3)]
        self.check(many, warn="lane better_salary の検索が 4 件")

    def test_warn_considering_all_null(self):
        def all_null(d):
            for r in d["results"]:
                r["considering"] = None
        self.check(all_null, warn="considering が全件 null")


class NormalizeTest(unittest.TestCase):
    def test_strips_legal_entity_and_width(self):
        self.assertEqual(v.normalize_company_key("株式会社 ＡＢＣ"), "abc")
        self.assertEqual(v.normalize_company_key("ABC（株）"), "abc")
        self.assertEqual(v.normalize_company_key("日本株式会社テスト"), "日本株式会社テスト")
        self.assertEqual(v.normalize_company_key(None), "")


class CliTest(unittest.TestCase):
    def run_cli(self, doc, *extra):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "r.json")
            with open(path, "w", encoding="utf-8") as f:
                if isinstance(doc, str):
                    f.write(doc)
                else:
                    json.dump(doc, f, ensure_ascii=False)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = v.main([path, *extra])
        return code, buf.getvalue()

    def test_pass_exit_0(self):
        code, out = self.run_cli(make_doc())
        self.assertEqual(code, 0)
        self.assertIn("PASS", out)

    def test_warn_only_exit_0(self):
        doc = make_doc()
        doc["results"] = []
        doc["search_log"] = doc["search_log"][:1]
        doc["derivations"] = []
        self.assertEqual(self.run_cli(doc)[0], 0)

    def test_fail_exit_1(self):
        doc = make_doc()
        doc["mode"] = "x"
        self.assertEqual(self.run_cli(doc)[0], 1)

    def test_unparsable_exit_1(self):
        code, out = self.run_cli("{not json")
        self.assertEqual(code, 1)
        self.assertIn("JSON として読み込めない", out)

    def test_json_output(self):
        doc = make_doc()
        doc["mode"] = "x"
        code, out = self.run_cli(doc, "--json")
        data = json.loads(out)
        self.assertEqual(code, 1)
        self.assertEqual(data["status"], "FAIL")
        self.assertEqual(data["error_count"], len(data["errors"]))
        self.assertEqual(set(data), {"status", "error_count", "warning_count", "errors", "warnings"})


if __name__ == "__main__":
    unittest.main()
