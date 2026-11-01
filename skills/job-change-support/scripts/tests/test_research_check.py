"""research_team/check.py の、research-team からのコピーに加えた 2 点の変更を確かめる単体テスト。

- grade は evidence-grading.md の A〜D を受け付け、それ以外を拒否する
- paper を持つ項目は拒否する（学術ルートを持たないため）

実行:
    python -m unittest discover -s scripts/tests
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "research_team"))

import check  # noqa: E402
import citation_verifier as cv  # noqa: E402

_URL = "https://example.com/ir"
_BODY = "ああああの従業員数は 1,234 人、平均勤続年数は 10.5 年である。"


def _item(**kw) -> dict:
    base = {"sq": "SQ1", "claim": "Employees: 1,234.", "quote": "従業員数は 1,234 人", "url": _URL,
            "title": "T", "publisher": "P", "date": "2026-06", "grade": "A", "cluster": "example.com",
            "stance": "supports", "kind": "figure", "doi": None, "arxiv_id": None, "paper": None}
    base.update(kw)
    return base


class LintItemTest(unittest.TestCase):
    def setUp(self) -> None:
        self.run_dir = tempfile.mkdtemp(prefix="jc-research-")
        os.makedirs(os.path.join(self.run_dir, "pages"))
        with open(os.path.join(self.run_dir, "pages", cv.cache_name(_URL)), "w", encoding="utf-8") as f:
            f.write(f"# url: {_URL}\n# accessed: 2026-11-01\n\n{_BODY}\n")

    def test_lint_item_grade_a_to_d_passes(self) -> None:
        for grade in ("A", "B", "C", "D"):
            with self.subTest(grade=grade):
                self.assertEqual(check.lint_item(self.run_dir, _item(grade=grade), {}), (None, "found"))

    def test_lint_item_grade_outside_a_to_d_rejects(self) -> None:
        reason, _ = check.lint_item(self.run_dir, _item(grade="E"), {})
        self.assertIn("unknown grade value", reason)

    def test_lint_item_paper_rejects(self) -> None:
        reason, _ = check.lint_item(self.run_dir, _item(paper="P1"), {})
        self.assertIn("paper items are outside this skill", reason)


if __name__ == "__main__":
    unittest.main()
