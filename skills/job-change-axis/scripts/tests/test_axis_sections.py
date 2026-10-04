"""axis_sections.py の単体テスト。標準ライブラリの unittest のみを用いる。

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

import axis_sections as axs  # noqa: E402

_ASSETS = os.path.join(_SKILLS_DIR, "job-change-support", "assets")
_EXAMPLE = os.path.join(_ASSETS, "axis_example.json")
_PROFILE_EXAMPLE = os.path.join(_ASSETS, "profile_example.json")
_SECTIONS_MD = os.path.join(_SKILL_DIR, "references", "sections.md")


def _load(path: str) -> dict:
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def _example() -> dict:
    return _load(_EXAMPLE)


def _states(document: dict) -> dict[str, str]:
    return {s["id"]: s["state"] for s in axs.report(document)["sections"]}


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
        self.assertEqual([r[0] for r in rows], axs.SECTION_IDS)
        md_initial = [sid for sid, initial in rows if initial != "skip"]
        self.assertEqual(md_initial, axs.INITIAL_SECTION_IDS)


class StateTest(unittest.TestCase):
    def test_example_is_deep_and_empty_is_missing(self) -> None:
        states = _states(_example())
        self.assertEqual(set(states.values()), {"deep"}, states)
        self.assertTrue(axs.report(_example())["initial_complete"])
        states = _states({"schema_version": "2.0"})
        self.assertEqual(set(states.values()), {"missing"}, states)
        self.assertFalse(axs.report({})["initial_complete"])

    def test_initial_scope_axis(self) -> None:
        """初回の範囲だけを埋めた axis は、初回の節が skeleton 以上、残りが missing になる。"""
        a = _example()
        a["targets"] = {}
        a["salary"] = {}
        a.pop("company_score_axes")
        for c in a["job_change_axis"]["conditions"]:
            c.pop("priority", None)
        states = _states(a)
        self.assertEqual(states["conditions"], "skeleton")
        # work_character と reasons は deep の条件が skeleton と同じである。
        self.assertEqual(states["work_character"], "deep")
        self.assertEqual(states["reasons"], "deep")
        for sid in ("score_axes", "targets", "salary"):
            self.assertEqual(states[sid], "missing", sid)
        self.assertTrue(axs.report(a)["initial_complete"])

    def test_v1_conditions_never_deep(self) -> None:
        a = {
            "schema_version": "1.0",
            "job_change_axis": {"must_conditions": ["リモート可"], "want_conditions": []},
        }
        self.assertEqual(_states(a)["conditions"], "skeleton")

    def test_salary_desired_only_is_skeleton(self) -> None:
        a = _example()
        a["salary"]["current"] = None
        self.assertEqual(_states(a)["salary"], "skeleton")

    def test_v2_profile_holding_the_axis_reads_the_same(self) -> None:
        """軸を内包する 2.0 の profile.json を渡しても、axis.json と同じ段階を返す。"""
        merged = {**_load(_PROFILE_EXAMPLE), **_example(), "schema_version": "2.0"}
        self.assertEqual(_states(merged), _states(_example()))


class MainTest(unittest.TestCase):
    def _run(self, *argv: str) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = axs.main(list(argv))
        return code, buf.getvalue()

    def test_exit_codes_and_json_keys(self) -> None:
        code, out = self._run(_EXAMPLE, "--json")
        self.assertEqual(code, 0)
        self.assertEqual([s["id"] for s in json.loads(out)["sections"]], axs.SECTION_IDS)
        # 職歴だけの profile.json は axis.json を指す案内を出して 1 を返す。
        code, out = self._run(_PROFILE_EXAMPLE)
        self.assertEqual(code, 1)
        self.assertIn("axis.json", out)
        code, _ = self._run(os.path.join(_SKILL_DIR, "no_such_file.json"))
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
