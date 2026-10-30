"""語彙の二重管理を守るテスト。references の表や他の検証スクリプトの定数と validator の定数が食い違ったら失敗する。

実行:
    python -m unittest discover -s scripts/tests
"""
from __future__ import annotations

import os
import re
import sys
import unittest

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_DIR = os.path.dirname(os.path.dirname(_TESTS_DIR))
sys.path.insert(0, os.path.join(_SKILL_DIR, "scripts"))

import field_catalog  # noqa: E402
import validate_company_index as vci  # noqa: E402
import validate_job_search_results as vjs  # noqa: E402

_LANES_MD = os.path.join(_SKILL_DIR, "references", "derivation-lanes.md")
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


class VocabularySyncTest(unittest.TestCase):
    def test_derivation_lanes_match_lanes_table(self):
        terms = _table_terms(_LANES_MD, "## Lane list")
        self.assertEqual(len(terms), 10, terms)
        self.assertEqual(tuple(terms), vjs.DERIVATION_LANES)

    def test_slug_pattern_matches_company_index(self):
        self.assertEqual(vjs._SLUG_RE.pattern, vci.SLUG_PATTERN.pattern)

    def test_enums_match_catalog(self):
        catalog = field_catalog.load_catalog()
        self.assertEqual(vjs.LEGAL_CHECK_RESULTS, catalog.enum_values("legal_check_result"))
        self.assertEqual(vjs.MATCH_RESULTS, catalog.enum_values("match_result"))


if __name__ == "__main__":
    unittest.main()
