"""検証スクリプトの語彙定数と、references/personality-guide.md の原本との一致を確かめる単体テスト。

片方だけを直したときに、このテストが落ちる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_vocabulary_sync
"""
from __future__ import annotations

import os
import re
import sys
import unittest

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKILL_DIR = os.path.dirname(_SCRIPTS_DIR)

sys.path.insert(0, _SCRIPTS_DIR)

import validate_self_analysis as vsa  # noqa: E402

_PERSONALITY_GUIDE_MD = os.path.join(_SKILL_DIR, "references", "personality-guide.md")

_CODE_RE = re.compile(r"`([^`]+)`")


def _table_terms(md_path: str, heading: str) -> list[str]:
    """指定見出しの直後にある表から、各行の最初のバックティック囲みの用語を順に返す。

    見出し行から次の見出し行までを対象とし、区切り行（|---|）より後の行だけを表の本体とみなす。
    """
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    try:
        start = lines.index(heading) + 1
    except ValueError:
        raise AssertionError(f"{md_path} に見出し {heading!r} が無い")

    terms: list[str] = []
    in_body = False
    for line in lines[start:]:
        if line.startswith("#"):
            break
        if re.match(r"^\|\s*-{2,}", line):
            in_body = True
            continue
        if not in_body:
            continue
        if not line.startswith("|"):
            if terms:
                break
            continue
        found = _CODE_RE.search(line)
        if found:
            terms.append(found.group(1))
    return terms


class PersonalityConstructsTest(unittest.TestCase):
    """personality.markers[].construct の識別子。原本は personality-guide.md にある。"""

    def setUp(self):
        self.terms = _table_terms(_PERSONALITY_GUIDE_MD, "## Construct vocabulary")

    def test_extraction_yields_fifteen_constructs(self):
        # 抽出が壊れたまま空一致で通らないよう、件数そのものを確かめる。
        self.assertEqual(len(self.terms), 15, self.terms)

    def test_matches_validate_self_analysis(self):
        self.assertEqual(tuple(self.terms), vsa.PERSONALITY_CONSTRUCTS)


if __name__ == "__main__":
    unittest.main()
