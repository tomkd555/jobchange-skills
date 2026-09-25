"""profile_sections.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行（スキルディレクトリを作業ディレクトリにする）:
    python -m unittest discover -s scripts/tests
"""
from __future__ import annotations

import copy
import json
import os
import re
import sys
import unittest

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKILL_DIR = os.path.dirname(_SCRIPTS_DIR)
_SKILLS_DIR = os.path.dirname(_SKILL_DIR)
sys.path.insert(0, _SCRIPTS_DIR)

import profile_sections as ps  # noqa: E402

_EXAMPLE = os.path.join(_SKILLS_DIR, "job-change-support", "assets", "profile_example.json")
_SECTIONS_MD = os.path.join(_SKILL_DIR, "references", "sections.md")


def _example() -> dict:
    with open(_EXAMPLE, encoding="utf-8-sig") as f:
        return json.load(f)


def _states(profile: dict) -> dict[str, str]:
    return {s["id"]: s["state"] for s in ps.report(profile)["sections"]}


class CatalogSyncTest(unittest.TestCase):
    def test_section_ids_match_sections_md(self) -> None:
        """references/sections.md の「節の一覧」の表と、スクリプトの節 id・順序・初回の別が一致する。"""
        with open(_SECTIONS_MD, encoding="utf-8") as f:
            lines = f.read().splitlines()
        start = lines.index("## Section list")
        rows = []
        for line in lines[start + 1 :]:
            if line.startswith("## "):
                break
            m = re.match(r"^\| `([a-z_]+)` \|(?:[^|]*\|){2}([^|]*)\|", line)
            if m:
                rows.append((m.group(1), m.group(2).strip()))
        self.assertEqual([r[0] for r in rows], ps.SECTION_IDS)
        md_initial = [sid for sid, initial in rows if initial != "skip"]
        self.assertEqual(md_initial, ps.INITIAL_SECTION_IDS)


class StateTest(unittest.TestCase):
    def test_example_profile_is_deep_everywhere(self) -> None:
        states = _states(_example())
        self.assertEqual(set(states.values()), {"deep"}, states)
        self.assertTrue(ps.report(_example())["initial_complete"])

    def test_empty_profile_is_missing_everywhere(self) -> None:
        states = _states({"schema_version": "2.0"})
        self.assertEqual(set(states.values()), {"missing"}, states)
        self.assertFalse(ps.report({})["initial_complete"])

    def test_initial_scope_profile(self) -> None:
        """初回の範囲だけを埋めた profile は、初回の節が skeleton 以上、残りが missing になる。"""
        p = _example()
        p["basic"] = {"current_role": p["basic"]["current_role"]}
        for e in p["career_history"]:
            e.pop("responsibilities", None)
            e.pop("achievements", None)
        p["skills"] = {}
        p["targets"] = {}
        p["salary"] = {}
        p.pop("company_score_axes")
        for c in p["job_change_axis"]["conditions"]:
            c.pop("priority", None)
        states = _states(p)
        self.assertEqual(states["basic"], "skeleton")
        self.assertEqual(states["career"], "deep")
        self.assertEqual(states["conditions"], "skeleton")
        # work_character と reasons は deep の条件が skeleton と同じである。
        self.assertEqual(states["work_character"], "deep")
        self.assertEqual(states["reasons"], "deep")
        for sid in ("achievements", "skills", "score_axes", "targets", "salary"):
            self.assertEqual(states[sid], "missing", sid)
        self.assertTrue(ps.report(p)["initial_complete"])

    def test_career_unparseable_period_is_skeleton(self) -> None:
        p = _example()
        p["career_history"][0]["period"] = "2021年〜"
        self.assertEqual(_states(p)["career"], "skeleton")

    def test_achievements_without_metric_is_skeleton(self) -> None:
        p = _example()
        for e in p["career_history"]:
            for a in e.get("achievements", []):
                a["metric"] = None
        self.assertEqual(_states(p)["achievements"], "skeleton")

    def test_v1_conditions_never_deep(self) -> None:
        p = {
            "schema_version": "1.0",
            "job_change_axis": {"must_conditions": ["リモート可"], "want_conditions": []},
        }
        self.assertEqual(_states(p)["conditions"], "skeleton")

    def test_salary_desired_only_is_skeleton(self) -> None:
        p = copy.deepcopy(_example())
        p["salary"]["current"] = None
        self.assertEqual(_states(p)["salary"], "skeleton")


class MainTest(unittest.TestCase):
    def test_main_json(self) -> None:
        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = ps.main([_EXAMPLE, "--json"])
        self.assertEqual(code, 0)
        out = json.loads(buf.getvalue())
        self.assertEqual([s["id"] for s in out["sections"]], ps.SECTION_IDS)

    def test_main_unreadable_returns_1(self) -> None:
        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = ps.main([os.path.join(_SKILL_DIR, "no_such_file.json")])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
