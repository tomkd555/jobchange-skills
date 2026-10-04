"""check_freshness.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_check_freshness
"""
from __future__ import annotations

import contextlib
import io
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
    artifacts: dict = {
        "job_posting": None
        if job_posting_days_ago is None
        else {"updated_at": _date_str(job_posting_days_ago)},
        "company_research": None
        if topics is None
        else {
            "updated_at": _date_str(0),
            "topics": {n: {"last_researched": _date_str(d)} for n, d in topics.items()},
        },
    }
    return {"schema_version": 1, "artifacts": artifacts}


def _labels(entries: list[dict]) -> list[str]:
    return [e["artifact"] for e in entries]


def _all_labels(result: dict) -> list[str]:
    return [l for bucket in ("fresh", "stale", "missing") for l in _labels(result[bucket])]


class FreshnessTest(unittest.TestCase):
    def test_ttl_boundaries(self):
        # (ラベル, 経過日数 → manifest, 成果物名, TTL)。TTL ちょうどは fresh、1日超過は stale
        rows = [
            ("job_posting", lambda d: _manifest(d, topics={}), "job_posting", 30),
            ("reputation", lambda d: _manifest(topics={"reputation": d}), "company_research.reputation", 90),
            ("workstyle", lambda d: _manifest(topics={"workstyle": d}), "company_research.workstyle", 180),
            ("philosophy", lambda d: _manifest(topics={"philosophy": d}), "company_research.philosophy", 365),
            ("未知トピックは既定 180", lambda d: _manifest(topics={"custom": d}), "company_research.custom", 180),
            (
                "interview_intel",
                lambda d: {**_manifest(topics={}), "artifacts": {**_manifest(topics={})["artifacts"], "interview_intel": {"updated_at": _date_str(d)}}},
                "interview_intel",
                180,
            ),
        ]
        for label, build, name, ttl in rows:
            for days, bucket in ((ttl, "fresh"), (ttl + 1, "stale")):
                with self.subTest(f"{label} {days}日 -> {bucket}"):
                    result = cf.check_freshness(build(days), TODAY)
                    entries = [e for e in result[bucket] if e["artifact"] == name]
                    self.assertEqual(len(entries), 1)
                    self.assertEqual(entries[0]["age_days"], days)
                    self.assertEqual(entries[0]["ttl_days"], ttl)

    def test_missing_decisions(self):
        # (ラベル, manifest, missing に出る成果物, 判定対象から外れる成果物)
        def with_topics(topics):
            m = _manifest(topics={})
            m["artifacts"]["company_research"]["topics"] = topics
            return m

        def with_optional(value):
            m = _manifest(topics={})
            m["artifacts"]["interview_intel"] = value
            return m

        both = ["company_research", "job_posting"]
        rows = [
            ("job_posting が null", _manifest(None, topics={}), ["job_posting"]),
            ("job_posting の日付が不正形式", {**_manifest(topics={}), "artifacts": {**_manifest(topics={})["artifacts"], "job_posting": {"updated_at": "2026/07/01"}}}, ["job_posting"]),
            ("トピックに last_researched が無い", with_topics({"benefits": {}}), ["company_research.benefits"]),
            ("company_research が null", _manifest(topics=None), ["company_research"]),
            ("topics が null", with_topics(None), ["company_research"]),
            ("topics が空なら判定対象なし", with_topics({}), []),
            ("artifacts キーが無い", {"schema_version": 1}, both),
            ("artifacts がオブジェクトでない", {"schema_version": 1, "artifacts": []}, both),
            ("ルートがオブジェクトでない", ["x"], both),
            ("任意成果物が日付なし", with_optional({"note": "undated"}), ["interview_intel"]),
            ("任意成果物がオブジェクトでない", with_optional("2026-01-18"), ["interview_intel"]),
            ("任意成果物が未記録（null）", with_optional(None), []),
            ("任意成果物が未記録（キー無し）", _manifest(topics={}), []),
        ]
        for label, manifest, expected_missing in rows:
            with self.subTest(label):
                result = cf.check_freshness(manifest, TODAY)
                self.assertEqual(sorted(_labels(result["missing"])), expected_missing)
                if label.startswith("任意成果物が未記録"):
                    self.assertNotIn("interview_intel", _all_labels(result))

    def test_optional_artifact_alone_reports_known_artifacts_missing(self):
        manifest = {"schema_version": 1, "artifacts": {"interview_intel": {"updated_at": _date_str(0)}}}
        result = cf.check_freshness(manifest, TODAY)
        self.assertEqual(sorted(_labels(result["missing"])), ["company_research", "job_posting"])
        self.assertEqual(_labels(result["fresh"]), ["interview_intel"])


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
            code = cf.main(argv)
        return code, buf.getvalue()

    def test_exit_code_is_always_0(self):
        fresh = json.dumps(_manifest(0, topics={"workstyle": 0}))
        rows = [
            ("fresh", self._write(fresh)),
            ("BOM 付き", self._write(fresh, "utf-8-sig")),
            ("stale", self._write(json.dumps(_manifest(999, topics={"workstyle": 999})))),
            ("壊れた JSON", self._write("{ not valid json ")),
            ("存在しないファイル", os.path.join(tempfile.gettempdir(), "no-such-manifest.json")),
        ]
        for label, path in rows:
            with self.subTest(label):
                self.assertEqual(self._run([path, "--today", TODAY.isoformat()])[0], 0)

    def test_json_output_buckets(self):
        path = self._write(json.dumps(_manifest(31, topics={"workstyle": 0})))
        code, out = self._run([path, "--today", TODAY.isoformat(), "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(sorted(data), ["fresh", "missing", "stale"])
        self.assertEqual(_labels(data["stale"]), ["job_posting"])
        self.assertEqual(_labels(data["fresh"]), ["company_research.workstyle"])

    def test_broken_json_reports_known_artifacts_missing(self):
        path = self._write("{ not valid json ")
        _, out = self._run([path, "--json"])
        self.assertEqual(_labels(json.loads(out)["missing"]), ["job_posting", "company_research"])

    def test_invalid_today_is_rejected(self):
        path = self._write(json.dumps(_manifest(0, topics={})))
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            cf.main([path, "--today", "2026/07/17"])


if __name__ == "__main__":
    unittest.main()
