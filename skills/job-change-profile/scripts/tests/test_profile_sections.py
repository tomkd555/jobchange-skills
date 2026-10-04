"""profile_sections.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行（スキルディレクトリを作業ディレクトリにする）:
    python -m unittest discover -s scripts/tests
"""
from __future__ import annotations

import contextlib
import io
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
    def test_example_is_deep_and_empty_is_missing(self) -> None:
        states = _states(_example())
        self.assertEqual(set(states.values()), {"deep"}, states)
        self.assertTrue(ps.report(_example())["initial_complete"])
        states = _states({"schema_version": "3.0"})
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
        states = _states(p)
        self.assertEqual(states["basic"], "skeleton")
        self.assertEqual(states["career"], "deep")
        for sid in ("achievements", "skills"):
            self.assertEqual(states[sid], "missing", sid)
        self.assertTrue(ps.report(p)["initial_complete"])

    def test_v2_profile_reports_the_career_sections(self) -> None:
        """軸を内包する 2.0 の profile.json を渡しても、職歴の節だけを報告する。"""
        p = _example()
        p["schema_version"] = "2.0"
        p["job_change_axis"] = {"reasons": ["裁量の拡大"]}
        self.assertEqual(list(_states(p)), ps.SECTION_IDS)
        self.assertEqual(set(_states(p).values()), {"deep"})

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


class MainTest(unittest.TestCase):
    def _run(self, *argv: str) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = ps.main(list(argv))
        return code, buf.getvalue()

    def test_exit_codes_and_json_keys(self) -> None:
        code, out = self._run(_EXAMPLE, "--json")
        self.assertEqual(code, 0)
        self.assertEqual([s["id"] for s in json.loads(out)["sections"]], ps.SECTION_IDS)
        code, _ = self._run(os.path.join(_SKILL_DIR, "no_such_file.json"))
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
