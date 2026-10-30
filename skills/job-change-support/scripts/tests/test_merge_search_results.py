"""merge_search_results.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import merge_search_results as msr  # noqa: E402
import validate_job_search_results as vjs  # noqa: E402
from test_validate_job_search_results import make_doc, make_result  # noqa: E402

_SEARCHER = "job_search_results.partial-searcher.json"
_CHROME = "job_search_results.partial-chrome.json"
_OUT = "job_search_results.json"


def _write(directory, name, doc):
    with open(os.path.join(directory, name), "w", encoding="utf-8") as f:
        if isinstance(doc, str):
            f.write(doc)
        else:
            json.dump(doc, f, ensure_ascii=False)


def _read(directory, name=_OUT):
    with open(os.path.join(directory, name), encoding="utf-8") as f:
        return json.load(f)


class MergeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def run_main(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = msr.main([self.dir, *args])
        return code, buf.getvalue()

    def _merge_searcher_and_chrome(self):
        searcher = make_doc()
        chrome = make_doc()
        chrome["results"] = [
            make_result(title="データ基盤エンジニア", company_name="サンプルデータ株式会社", read_via="chrome")
        ]
        chrome["search_log"] = [dict(chrome["search_log"][0], query="chrome-q", source="chrome")]
        chrome["derivations"] = []
        chrome["coverage_notes"] = "Chrome で 1 件読んだ"
        chrome["open_questions"] = ["Q1"]
        searcher["open_questions"] = ["Q1", "Q2"]
        _write(self.dir, _SEARCHER, searcher)
        _write(self.dir, _CHROME, chrome)
        self.assertEqual(self.run_main()[0], 0)
        return _read(self.dir)

    def test_merge_concatenates_partials(self):
        merged = self._merge_searcher_and_chrome()
        self.assertEqual(len(merged["results"]), 3)
        self.assertEqual(len(merged["search_log"]), 3)
        self.assertEqual(merged["open_questions"], ["Q1", "Q2"])
        self.assertEqual(merged["coverage_notes"], "1 ページ目のみ\nChrome で 1 件読んだ")

    def test_merge_output_passes_validate(self):
        merged = self._merge_searcher_and_chrome()
        res = vjs.validate(merged)
        self.assertEqual(res.errors, [], res.errors)

    def _merge_with_duplicate(self):
        searcher = make_doc()
        chrome = make_doc()
        # 法人格・空白・全角半角・大文字小文字の差は同じ求人とみなす。
        chrome["results"] = [
            make_result(company_name="(株)アクメクラウド", title="インフラ エンジニア", read_via="chrome")
        ]
        chrome["search_log"] = []
        _write(self.dir, _SEARCHER, searcher)
        _write(self.dir, _CHROME, chrome)
        self.assertEqual(self.run_main("--json")[0], 0)
        return _read(self.dir)

    def test_duplicate_chrome_copy_removed(self):
        merged = self._merge_with_duplicate()
        self.assertEqual([r["read_via"] for r in merged["results"]], ["webfetch", "webfetch"])

    def test_duplicates_note_count(self):
        merged = self._merge_with_duplicate()
        self.assertTrue(merged["coverage_notes"].endswith("重複 1 件を除いた"))

    def test_same_company_different_title_not_duplicate(self):
        doc = make_doc()
        doc["results"].append(make_result(title="別の職種"))
        _write(self.dir, _SEARCHER, doc)
        self.run_main()
        merged = _read(self.dir)
        self.assertEqual(len(merged["results"]), 3)
        self.assertNotIn("重複", merged["coverage_notes"])

    def test_derivations_deduplicated_by_lane(self):
        a, b = make_doc(), make_doc()
        b["derivations"].append({"lane": "remote_widen", "changed_conditions": ["c002"], "rationale": "広げる"})
        _write(self.dir, _SEARCHER, a)
        _write(self.dir, _CHROME, b)
        self.run_main()
        self.assertEqual([d["lane"] for d in _read(self.dir)["derivations"]], ["better_salary", "remote_widen"])

    def test_header_from_searcher_over_chrome(self):
        searcher, chrome = make_doc(), make_doc()
        searcher["mode"] = "similar_better"
        searcher["baseline"] = {"posting_id": "アクメクラウド-20261020-01"}
        chrome["mode"] = "fuzzy"
        _write(self.dir, _SEARCHER, searcher)
        _write(self.dir, _CHROME, chrome)
        self.run_main()
        merged = _read(self.dir)
        self.assertEqual(merged["mode"], "similar_better")
        self.assertEqual(merged["baseline"], {"posting_id": "アクメクラウド-20261020-01"})

    def test_header_without_searcher_from_chrome(self):
        doc = make_doc()
        doc["search_id"] = "20261025-only-chrome"
        _write(self.dir, _CHROME, doc)
        self.assertEqual(self.run_main()[0], 0)
        self.assertEqual(_read(self.dir)["search_id"], "20261025-only-chrome")

    def test_no_partial_exit_1(self):
        code, out = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("ERROR", out)
        self.assertFalse(os.path.exists(os.path.join(self.dir, _OUT)))

    def test_unparsable_partial_exit_1_writes_nothing(self):
        _write(self.dir, _SEARCHER, make_doc())
        _write(self.dir, _CHROME, "{broken")
        self.assertEqual(self.run_main()[0], 1)
        self.assertFalse(os.path.exists(os.path.join(self.dir, _OUT)))

    def test_non_object_partial_exit_1(self):
        _write(self.dir, _SEARCHER, "[]")
        self.assertEqual(self.run_main()[0], 1)

    def test_json_output_success_fields(self):
        _write(self.dir, _SEARCHER, make_doc())
        code, out = self.run_main("--json")
        data = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual(data["result_count"], 2)
        self.assertEqual(data["removed_count"], 0)
        self.assertEqual(data["output_path"], os.path.join(self.dir, _OUT))
        self.assertEqual(data["errors"], [])

    def test_json_output_without_partials_exit_1(self):
        code, out = self.run_main("--json")
        self.assertEqual(code, 1)
        self.assertTrue(json.loads(out)["errors"])

    def test_cleanup_deletes_partials_only(self):
        _write(self.dir, _SEARCHER, make_doc())
        _write(self.dir, _CHROME, make_doc())
        _write(self.dir, _OUT, make_doc())
        self.assertEqual(self.run_main("--cleanup")[0], 0)
        self.assertEqual(os.listdir(self.dir), [_OUT])

    def test_cleanup_without_partials_exit_0(self):
        self.assertEqual(self.run_main("--cleanup")[0], 0)


if __name__ == "__main__":
    unittest.main()
