"""検証スクリプトの語彙定数と、references の原本との一致を確かめる単体テスト。

同じ語彙が原本（references の Markdown）と検証スクリプトの定数の両方にある組を対象とする。
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
_SKILLS_DIR = os.path.dirname(_SKILL_DIR)

sys.path.insert(0, _SCRIPTS_DIR)
# 語彙のコピーは他スキルの検証スクリプトにもある。それらも同じ原本と突き合わせる。
sys.path.insert(0, os.path.join(_SKILLS_DIR, "job-change-fit-assessment", "scripts"))
sys.path.insert(0, os.path.join(_SKILLS_DIR, "job-change-job-search", "scripts"))
sys.path.insert(0, os.path.join(_SKILLS_DIR, "job-change-company-research", "scripts"))

import validate_company_index as vci  # noqa: E402
import validate_company_research as vcr  # noqa: E402
import validate_fit_assessment as vfa  # noqa: E402
import validate_job_search_results as vjs  # noqa: E402
import validate_profile as vp  # noqa: E402

_SCREENING_AXES_MD = os.path.join(_SKILL_DIR, "references", "screening-axes.md")
_SCORE_RUBRIC_MD = os.path.join(
    _SKILLS_DIR, "job-change-company-research", "references", "company-score-rubric.md"
)
_JOB_SEARCH_FORMAT_MD = os.path.join(
    _SKILLS_DIR, "job-change-job-search", "references", "job-search-format.md"
)
_DERIVATION_LANES_MD = os.path.join(
    _SKILLS_DIR, "job-change-job-search", "references", "derivation-lanes.md"
)

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
    """原本の表と、各検証スクリプトの定数が一致すること。件数も確かめ、抽出が壊れて空一致で通ることを防ぐ。"""

    def _assert_table(self, md_path, heading, count, *copies):
        terms = _table_terms(md_path, heading)
        if count is not None:
            self.assertEqual(len(terms), count, terms)
        for name, copy in copies:
            with self.subTest(heading=heading, copy=name):
                self.assertEqual(tuple(terms), tuple(copy))
        return terms

    def test_screening_axes(self):
        self._assert_table(
            _SCREENING_AXES_MD,
            "## The eight screening axes",
            8,
            ("validate_profile", vp._SCREENING_AXES),
            ("validate_job_search_results", vjs.SCREENING_AXES),
        )

    def test_quantitative_score_axes(self):
        terms = self._assert_table(
            _SCORE_RUBRIC_MD,
            "## Quantitative candidate axes",
            9,
            ("validate_profile", vp._QUANTITATIVE_SCORE_AXES),
            ("validate_job_search_results の metric 軸", vjs.COMPANY_METRIC_UNITS),
        )
        self.assertIn(vp._DEFAULT_SELECTED_AXIS, terms)
        # 求人検索の書式の表も同じ軸キーを挙げる
        self._assert_table(
            _JOB_SEARCH_FORMAT_MD, "#### Axis keys in metrics", None, ("求人検索の書式", vjs.COMPANY_METRIC_UNITS)
        )

    def test_metric_units_match_company_research(self):
        self.assertEqual(vjs.COMPANY_METRIC_UNITS, vcr.QUANTITATIVE_AXIS_UNITS)

    def test_score_axis_kinds(self):
        self._assert_table(
            _SCORE_RUBRIC_MD,
            "## The two kinds of axis",
            2,
            ("validate_profile", vp._SCORE_AXIS_KINDS),
            ("validate_fit_assessment", vfa._SCORE_KINDS),
        )

    def test_job_search_vocabularies(self):
        fmt = _JOB_SEARCH_FORMAT_MD
        self._assert_table(
            fmt, "### results[].search_set (string, required since 2.2)", None, ("SEARCH_SETS", vjs.SEARCH_SETS)
        )
        self._assert_table(
            fmt, "### results[].role_match (string, required since 2.2)", None, ("ROLE_MATCHES", vjs.ROLE_MATCHES)
        )
        self._assert_table(
            fmt, "### results[].related_info (object, optional)", None, ("RELATED_INFO_KEYS", vjs.RELATED_INFO_KEYS)
        )
        self._assert_table(_DERIVATION_LANES_MD, "## Lane list", None, ("DERIVATION_LANES", vjs.DERIVATION_LANES))
        self.assertEqual(
            set(vjs.COMPANY_BASICS_KEYS) | set(vjs.POSTING_RELATED_INFO_KEYS), set(vjs.RELATED_INFO_KEYS)
        )

    def test_company_slug_pattern(self):
        """原本は形式を文章で定めており、正規表現は載っていない。3つの写しが同一であることと、
        原本が挙げる例の可否が一致することを確かめる。"""
        patterns = {
            "validate_company_index": vci.SLUG_PATTERN.pattern,
            "validate_fit_assessment": vfa._SLUG_RE.pattern,
            "validate_job_search_results": vjs._SLUG_RE.pattern,
        }
        self.assertEqual(len(set(patterns.values())), 1, patterns)
        compiled = re.compile(vci.SLUG_PATTERN.pattern)
        for slug in ("acme-cloud", "S_アクメクラウド", "S_acme-cloud", "架空クラウドワークス"):
            with self.subTest(accepted=slug):
                self.assertIsNotNone(compiled.match(slug))
        # 予約名 `_general` と先頭のハイフンは登録できない
        for slug in ("_general", "-acme", "acme cloud", "acme/cloud", ""):
            with self.subTest(rejected=slug):
                self.assertIsNone(compiled.match(slug))


if __name__ == "__main__":
    unittest.main()
