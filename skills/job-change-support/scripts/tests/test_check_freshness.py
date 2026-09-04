"""check_freshness.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_check_freshness
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_freshness as cf  # noqa: E402

TODAY = date(2026, 7, 17)


def _date_str(days_ago: int) -> str:
    return (TODAY - timedelta(days=days_ago)).isoformat()


def _manifest(job_posting_days_ago: int | None = 0, topics: dict | None = None) -> dict:
    """job_posting と company_research.topics を持つ manifest を組み立てる。"""
    artifacts: dict = {}
    if job_posting_days_ago is not None:
        artifacts["job_posting"] = {
            "updated_at": _date_str(job_posting_days_ago),
            "source_url": "https://example.com/jobs/1",
        }
    else:
        artifacts["job_posting"] = None

    if topics is not None:
        artifacts["company_research"] = {
            "updated_at": _date_str(0),
            "topics": {
                name: {"last_researched": _date_str(days_ago)}
                for name, days_ago in topics.items()
            },
        }
    else:
        artifacts["company_research"] = None

    return {"schema_version": 1, "artifacts": artifacts}


def _labels(entries: list[dict]) -> list[str]:
    return [e["artifact"] for e in entries]


class JobPostingFreshnessTest(unittest.TestCase):
    def test_ttl_exact_boundary_is_fresh(self):
        manifest = _manifest(job_posting_days_ago=30, topics={})
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("job_posting", _labels(result["fresh"]))

    def test_ttl_plus_one_is_stale(self):
        manifest = _manifest(job_posting_days_ago=31, topics={})
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("job_posting", _labels(result["stale"]))

    def test_null_job_posting_is_missing(self):
        manifest = _manifest(job_posting_days_ago=None, topics={})
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("job_posting", _labels(result["missing"]))

    def test_missing_updated_at_is_missing(self):
        manifest = _manifest(job_posting_days_ago=0, topics={})
        manifest["artifacts"]["job_posting"] = {"source_url": "https://example.com"}
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("job_posting", _labels(result["missing"]))

    def test_malformed_date_is_missing(self):
        manifest = _manifest(job_posting_days_ago=0, topics={})
        manifest["artifacts"]["job_posting"]["updated_at"] = "2026/07/01"
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("job_posting", _labels(result["missing"]))


class CompanyResearchTopicFreshnessTest(unittest.TestCase):
    def test_reputation_ttl_90_exact_boundary_is_fresh(self):
        manifest = _manifest(topics={"reputation": 90})
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("company_research.reputation", _labels(result["fresh"]))

    def test_reputation_ttl_90_plus_one_is_stale(self):
        manifest = _manifest(topics={"reputation": 91})
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("company_research.reputation", _labels(result["stale"]))

    def test_philosophy_ttl_365_exact_boundary_is_fresh(self):
        manifest = _manifest(topics={"philosophy": 365})
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("company_research.philosophy", _labels(result["fresh"]))

    def test_philosophy_ttl_365_plus_one_is_stale(self):
        manifest = _manifest(topics={"philosophy": 366})
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("company_research.philosophy", _labels(result["stale"]))

    def test_workstyle_ttl_180_exact_boundary_is_fresh(self):
        manifest = _manifest(topics={"workstyle": 180})
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("company_research.workstyle", _labels(result["fresh"]))

    def test_workstyle_ttl_180_plus_one_is_stale(self):
        manifest = _manifest(topics={"workstyle": 181})
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("company_research.workstyle", _labels(result["stale"]))

    def test_unknown_topic_falls_back_to_default_180(self):
        manifest = _manifest(topics={"custom_topic": 180})
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("company_research.custom_topic", _labels(result["fresh"]))

        manifest_stale = _manifest(topics={"custom_topic": 181})
        result_stale = cf.check_freshness(manifest_stale, TODAY)
        self.assertIn("company_research.custom_topic", _labels(result_stale["stale"]))

    def test_topic_missing_last_researched_is_missing(self):
        manifest = _manifest(topics={"benefits": 0})
        manifest["artifacts"]["company_research"]["topics"]["benefits"] = {}
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("company_research.benefits", _labels(result["missing"]))


class CompanyResearchWholeMissingTest(unittest.TestCase):
    def test_null_company_research_is_missing_as_whole(self):
        manifest = _manifest(topics=None)
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("company_research", _labels(result["missing"]))
        # トピック単位の内訳は出さない
        self.assertFalse(
            any(a.startswith("company_research.") for a in _labels(result["missing"]))
        )

    def test_topics_key_absent_is_missing_as_whole(self):
        manifest = _manifest(topics={})
        del manifest["artifacts"]["company_research"]["topics"]
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("company_research", _labels(result["missing"]))

    def test_null_topics_is_missing_as_whole(self):
        manifest = _manifest(topics={})
        manifest["artifacts"]["company_research"]["topics"] = None
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("company_research", _labels(result["missing"]))

    def test_empty_topics_produces_no_entries(self):
        manifest = _manifest(topics={})
        result = cf.check_freshness(manifest, TODAY)
        all_labels = _labels(result["fresh"]) + _labels(result["stale"]) + _labels(result["missing"])
        self.assertNotIn("company_research", all_labels)


class OptionalArtifactFreshnessTest(unittest.TestCase):
    def test_interview_intel_ttl_is_180(self):
        self.assertEqual(cf.OPTIONAL_ARTIFACT_TTL_DAYS["interview_intel"], 180)

    def test_only_dated_interview_intel_present_reports_others_missing(self):
        manifest = {"schema_version": 1, "artifacts": {"interview_intel": {"updated_at": _date_str(0)}}}
        result = cf.check_freshness(manifest, TODAY)
        self.assertEqual(sorted(_labels(result["missing"])), ["company_research", "job_posting"])
        self.assertIn("interview_intel", _labels(result["fresh"]))

    def test_interview_intel_ttl_180_exact_boundary_is_fresh(self):
        manifest = _manifest(topics={})
        manifest["artifacts"]["interview_intel"] = {"updated_at": _date_str(180)}
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("interview_intel", _labels(result["fresh"]))

    def test_interview_intel_ttl_180_plus_one_is_stale(self):
        manifest = _manifest(topics={})
        manifest["artifacts"]["interview_intel"] = {"updated_at": _date_str(181)}
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("interview_intel", _labels(result["stale"]))

    def test_absent_interview_intel_produces_no_entry(self):
        manifest = _manifest(topics={})
        result = cf.check_freshness(manifest, TODAY)
        all_labels = _labels(result["fresh"]) + _labels(result["stale"]) + _labels(result["missing"])
        self.assertNotIn("interview_intel", all_labels)

    def test_null_interview_intel_produces_no_entry(self):
        manifest = _manifest(topics={})
        manifest["artifacts"]["interview_intel"] = None
        result = cf.check_freshness(manifest, TODAY)
        all_labels = _labels(result["fresh"]) + _labels(result["stale"]) + _labels(result["missing"])
        self.assertNotIn("interview_intel", all_labels)

    def test_non_dict_interview_intel_produces_missing(self):
        manifest = _manifest(topics={})
        manifest["artifacts"]["interview_intel"] = "2026-01-18"
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("interview_intel", _labels(result["missing"]))

    def test_interview_intel_without_updated_at_is_missing(self):
        manifest = _manifest(topics={})
        manifest["artifacts"]["interview_intel"] = {"note": "recorded but undated"}
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("interview_intel", _labels(result["missing"]))

    def test_interview_intel_malformed_date_is_missing(self):
        manifest = _manifest(topics={})
        manifest["artifacts"]["interview_intel"] = {"updated_at": "2026/07/01"}
        result = cf.check_freshness(manifest, TODAY)
        self.assertIn("interview_intel", _labels(result["missing"]))


class ArtifactsMissingTest(unittest.TestCase):
    def test_no_artifacts_key_reports_both_known_as_missing(self):
        result = cf.check_freshness({"schema_version": 1}, TODAY)
        self.assertEqual(sorted(_labels(result["missing"])), ["company_research", "job_posting"])

    def test_artifacts_not_object_reports_both_known_as_missing(self):
        result = cf.check_freshness({"schema_version": 1, "artifacts": []}, TODAY)
        self.assertEqual(sorted(_labels(result["missing"])), ["company_research", "job_posting"])

    def test_root_not_object_reports_both_known_as_missing(self):
        result = cf.check_freshness(["not", "an", "object"], TODAY)
        self.assertEqual(sorted(_labels(result["missing"])), ["company_research", "job_posting"])


class CliTest(unittest.TestCase):
    def _write_tmp(self, obj) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path

    def test_main_returns_0_on_valid(self):
        path = self._write_tmp(_manifest(job_posting_days_ago=0, topics={"workstyle": 0}))
        self.assertEqual(cf.main([path, "--today", TODAY.isoformat()]), 0)

    def test_main_returns_0_on_stale(self):
        path = self._write_tmp(_manifest(job_posting_days_ago=999, topics={"workstyle": 999}))
        self.assertEqual(cf.main([path, "--today", TODAY.isoformat()]), 0)

    def test_main_returns_0_on_missing_file(self):
        missing_path = os.path.join(tempfile.gettempdir(), "does_not_exist_manifest.json")
        self.assertEqual(cf.main([missing_path, "--today", TODAY.isoformat()]), 0)

    def test_main_returns_0_on_broken_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{ not valid json ")
        self.addCleanup(os.remove, path)
        self.assertEqual(cf.main([path, "--today", TODAY.isoformat()]), 0)

    def test_main_json_flag_valid(self):
        path = self._write_tmp(_manifest(job_posting_days_ago=0, topics={"workstyle": 0}))
        self.assertEqual(cf.main([path, "--today", TODAY.isoformat(), "--json"]), 0)

    def test_main_returns_0_on_valid_with_bom(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8-sig") as f:
            json.dump(_manifest(job_posting_days_ago=0, topics={"workstyle": 0}), f, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        self.assertEqual(cf.main([path, "--today", TODAY.isoformat()]), 0)

    def test_today_injection_is_deterministic(self):
        path = self._write_tmp(_manifest(job_posting_days_ago=30, topics={}))
        # --today を明示すれば、実行時刻に依存せず同じ結果になる
        self.assertEqual(cf.main([path, "--today", TODAY.isoformat()]), 0)
        self.assertEqual(cf.main([path, "--today", TODAY.isoformat()]), 0)


class ResultShapeTest(unittest.TestCase):
    def test_result_shape(self):
        manifest = _manifest(job_posting_days_ago=0, topics={"workstyle": 0})
        result = cf.check_freshness(manifest, TODAY)
        self.assertEqual(set(result.keys()), {"fresh", "stale", "missing"})
        for bucket in ("fresh", "stale", "missing"):
            self.assertIsInstance(result[bucket], list)

    def test_immutability_of_input(self):
        manifest = _manifest(job_posting_days_ago=0, topics={"workstyle": 0})
        snapshot = copy.deepcopy(manifest)
        cf.check_freshness(manifest, TODAY)
        self.assertEqual(manifest, snapshot)


if __name__ == "__main__":
    unittest.main()
