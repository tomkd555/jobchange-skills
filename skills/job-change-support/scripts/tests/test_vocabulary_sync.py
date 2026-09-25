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


class ScreeningAxesTest(unittest.TestCase):
    """8つのスクリーニング軸の id。原本は references/screening-axes.md にある。"""

    def setUp(self):
        self.terms = _table_terms(_SCREENING_AXES_MD, "## The eight screening axes")

    def test_extraction_yields_eight_axes(self):
        # 抽出が壊れたまま空一致で通らないよう、件数そのものを確かめる。
        self.assertEqual(len(self.terms), 8, self.terms)

    def test_matches_validate_profile(self):
        self.assertEqual(tuple(self.terms), vp._SCREENING_AXES)

    def test_matches_validate_job_search_results(self):
        self.assertEqual(tuple(self.terms), vjs.SCREENING_AXES)


class QuantitativeScoreAxesTest(unittest.TestCase):
    """定量候補軸の軸キー。原本は job-change-company-research の company-score-rubric.md にある。"""

    def setUp(self):
        self.terms = _table_terms(_SCORE_RUBRIC_MD, "## Quantitative candidate axes")

    def test_extraction_yields_nine_axes(self):
        self.assertEqual(len(self.terms), 9, self.terms)

    def test_matches_validate_profile(self):
        self.assertEqual(tuple(self.terms), vp._QUANTITATIVE_SCORE_AXES)

    def test_default_selected_axis_is_a_candidate(self):
        self.assertIn(vp._DEFAULT_SELECTED_AXIS, self.terms)


class ScoreAxisKindTest(unittest.TestCase):
    """採点軸の種別（kind）。原本は company-score-rubric.md の「軸の2種類」にある。"""

    def setUp(self):
        self.terms = _table_terms(_SCORE_RUBRIC_MD, "## The two kinds of axis")

    def test_extraction_yields_two_kinds(self):
        self.assertEqual(len(self.terms), 2, self.terms)

    def test_matches_validate_profile(self):
        self.assertEqual(tuple(self.terms), vp._SCORE_AXIS_KINDS)

    def test_matches_validate_fit_assessment(self):
        self.assertEqual(tuple(self.terms), vfa._SCORE_KINDS)


class CompanySlugPatternTest(unittest.TestCase):
    """企業スラッグの形式。原本は references/company-index-format.md にある。

    原本は形式を文章で定めており、正規表現そのものは載っていない。そこで、3つの検証スクリプトが
    持つ正規表現が同一であることと、原本が挙げる例に対する可否が一致することを確かめる。
    """

    # 原本「companies エントリー」節が挙げる例。
    _ACCEPTED = ("acme-cloud", "S_アクメクラウド", "S_acme-cloud", "架空クラウドワークス")
    # 予約名 `_general` は企業スラッグとして登録できない。先頭のハイフンも不可。
    _REJECTED = ("_general", "-acme", "acme cloud", "acme/cloud", "")

    def _patterns(self) -> dict[str, str]:
        return {
            "validate_company_index": vci.SLUG_PATTERN.pattern,
            "validate_fit_assessment": vfa._SLUG_RE.pattern,
            "validate_job_search_results": vjs._SLUG_RE.pattern,
        }

    def test_all_copies_are_identical(self):
        patterns = self._patterns()
        self.assertEqual(len(set(patterns.values())), 1, patterns)

    def test_documented_examples(self):
        for name, pattern in self._patterns().items():
            compiled = re.compile(pattern)
            for slug in self._ACCEPTED:
                with self.subTest(script=name, slug=slug):
                    self.assertIsNotNone(compiled.match(slug))
            for slug in self._REJECTED:
                with self.subTest(script=name, slug=slug):
                    self.assertIsNone(compiled.match(slug))


class JobSearchSchema22Test(unittest.TestCase):
    """求人検索 2.2 の語彙（探索集合・関連情報）。原本は job-change-job-search の job-search-format.md にある。"""

    def test_matches_search_sets(self):
        terms = _table_terms(
            _JOB_SEARCH_FORMAT_MD, "### results[].search_set (string, required since 2.2)"
        )
        self.assertEqual(tuple(terms), vjs.SEARCH_SETS)

    def test_matches_role_matches(self):
        terms = _table_terms(
            _JOB_SEARCH_FORMAT_MD, "### results[].role_match (string, required since 2.2)"
        )
        self.assertEqual(tuple(terms), vjs.ROLE_MATCHES)

    def test_matches_related_info_keys(self):
        terms = _table_terms(
            _JOB_SEARCH_FORMAT_MD, "### results[].related_info (object, optional)"
        )
        self.assertEqual(tuple(terms), vjs.RELATED_INFO_KEYS)


class JobSearchSchema23Test(unittest.TestCase):
    """求人検索 2.3 の語彙（派生レーン・企業プロフィール）。原本は job-change-job-search の
    job-search-format.md・derivation-lanes.md、および job-change-company-research の
    company-score-rubric.md にある。"""

    def test_metric_units_match_company_research(self):
        self.assertEqual(vjs.COMPANY_METRIC_UNITS, vcr.QUANTITATIVE_AXIS_UNITS)

    def test_metric_keys_match_score_rubric(self):
        terms = _table_terms(_SCORE_RUBRIC_MD, "## Quantitative candidate axes")
        self.assertEqual(terms, list(vjs.COMPANY_METRIC_UNITS))

    def test_basics_keys(self):
        self.assertEqual(
            set(vjs.COMPANY_BASICS_KEYS) | set(vjs.POSTING_RELATED_INFO_KEYS), set(vjs.RELATED_INFO_KEYS)
        )

    def test_lanes_match_derivation_lanes_md(self):
        if not os.path.exists(_DERIVATION_LANES_MD):
            self.skipTest("derivation-lanes.md not yet written")
        terms = _table_terms(_DERIVATION_LANES_MD, "## Lane list")
        self.assertEqual(tuple(terms), vjs.DERIVATION_LANES)

    def test_metric_table_in_format_md(self):
        with open(_JOB_SEARCH_FORMAT_MD, encoding="utf-8") as f:
            content = f.read()
        heading = "#### Axis keys in metrics"
        if heading not in content:
            self.skipTest("job-search-format.md に #### metrics の軸キー が無い")
        terms = _table_terms(_JOB_SEARCH_FORMAT_MD, heading)
        self.assertEqual(terms, list(vjs.COMPANY_METRIC_UNITS))


if __name__ == "__main__":
    unittest.main()
