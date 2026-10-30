"""export_flat.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_export_flat
"""
from __future__ import annotations

import contextlib
import csv
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import export_flat as ef  # noqa: E402

PID_A = "S_アクメクラウド-20261025-01"
PID_B = "B_ベータシステムズ-20261028-01"


def _value(value, unit=None, url="https://example.com/careers/123", grade="A", as_of="2026-10-25"):
    return {"value": value, "unit": unit, "source_url": url, "grade": grade, "as_of": as_of, "quote": None}


WISHES = {
    "schema_version": "1.0", "updated": "2026-11-01", "history": [], "used_in": [],
    "conditions": [
        {"id": "c001", "kind": "salary_min", "field_id": "salary_min", "operator": ">=", "text": "年収 600 万円以上",
         "value": 6000000, "unit": "円", "level": "must", "source": "user", "how_to_judge": None,
         "created": "2026-10-25", "updated": "2026-10-25", "active": True},
        {"id": "c003", "kind": "value", "field_id": "custom", "operator": None, "text": "知的な挑戦",
         "value": None, "unit": None, "level": "want", "source": "intellectual_challenge",
         "how_to_judge": "新しい技術の導入を含むか", "created": "2026-11-01", "updated": "2026-11-01", "active": True},
    ],
}
POSTING = {
    "schema_version": "1.0", "posting_id": PID_A, "company_slug": "S_アクメクラウド", "source_type": "url",
    "source_url": "https://example.com/careers/123", "fetched_at": "2026-10-25", "open_questions": [],
    "job": {
        "salary_min": _value(6500000, "円"),
        "monthly_overtime_h": {"value": None, "unit": "時間", "source_url": None, "grade": None, "as_of": None, "quote": None},
        "requirements_must": _value(["AWS", "Linux"]),
    },
    "company": {
        "avg_tenure_years": [
            _value(4.2, "年", "https://disclosure2.edinet-fsa.go.jp/x", as_of="2026-03"),
            _value(4.5, "年", "https://shokuba.mhlw.go.jp/x", as_of="2025"),
        ],
        "labor_violation_listed": _value(False),
    },
}
MATCHES = {
    "schema_version": "1.0", "posting_id": PID_A, "checked_at": "2026-10-25", "unknowns": [],
    "match": [
        {"condition_id": "c001", "result": "meets", "basis_field_id": "salary_min", "note": "下限 650 万円"},
        {"condition_id": "c003", "result": "unknown", "basis_field_id": None, "note": "意思決定で評点する"},
    ],
}
DECISION = {
    "schema_version": "1.0", "id": "20261115-infra-2sha", "date": "2026-11-15", "subject": "比較",
    "candidates": [
        {"posting_id": PID_A, "company_slug": "S_アクメクラウド", "label": "A"},
        {"posting_id": PID_B, "company_slug": "B_ベータシステムズ", "label": "B"},
    ],
    "criteria": [
        {"id": "k01", "field_id": "salary_min", "condition_id": "c001", "direction": "higher",
         "values": {PID_A: 6500000, PID_B: 7000000}, "ratings": None},
        {"id": "k03", "field_id": "custom", "condition_id": "c003", "direction": "higher",
         "values": None, "ratings": {PID_A: 4, PID_B: 2}},
    ],
}


def _write(path: Path, document) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document if isinstance(document, str) else json.dumps(document, ensure_ascii=False), encoding="utf-8")


class ExportTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        private = self.root / "career-private"
        _write(private / "wishes.json", WISHES)
        _write(self.root / "companies" / "S_アクメクラウド" / "postings" / PID_A / "posting-check.json", POSTING)
        _write(private / "matches" / f"{PID_A}.json", MATCHES)
        _write(private / "decisions" / "20261115-infra-2sha.json", DECISION)

    def _run(self, *extra: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ef.main(["--data-root", str(self.root), *extra])
        return code, out.getvalue(), err.getvalue()

    def _rows(self) -> list[dict]:
        with open(self.root / "export" / "flat.csv", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))

    def test_row_count_14_for_full_data_root(self) -> None:
        code, out, _ = self._run()
        self.assertEqual(code, 0)
        rows = self._rows()
        # wishes 2 + posting (3 job + 2 tenure + 1 violation) + match 2 + decision 2 criteria x 2 candidates
        self.assertEqual(len(rows), 2 + 6 + 2 + 4)
        self.assertIn("14 行", out)

    def test_header_matches_columns(self) -> None:
        self._run()
        rows = self._rows()
        self.assertEqual(list(rows[0]), list(ef.COLUMNS))

    def test_csv_starts_with_bom(self) -> None:
        self._run()
        self.assertTrue((self.root / "export" / "flat.csv").read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_rows_carry_values_from_each_source(self) -> None:
        self._run()
        rows = self._rows()

        def pick(**kw):
            found = [r for r in rows if all(r[k] == v for k, v in kw.items())]
            self.assertEqual(len(found), 1, kw)
            return found[0]

        wish = pick(condition_id="c001", posting_id="", decision_id="")
        self.assertEqual((wish["field_id"], wish["value"], wish["unit"]), ("salary_min", "6000000", "円"))
        tenure = pick(field_id="avg_tenure_years", as_of="2025")
        self.assertEqual((tenure["value"], tenure["grade"], tenure["posting_id"]), ("4.5", "A", PID_A))
        self.assertEqual(pick(field_id="requirements_must")["value"], '["AWS", "Linux"]')
        self.assertEqual(pick(field_id="labor_violation_listed")["value"], "false")
        match = pick(condition_id="c003", posting_id=PID_A, decision_id="")
        self.assertEqual((match["value"], match["field_id"], match["company_slug"]), ("unknown", "", "S_アクメクラウド"))
        rating = pick(decision_id="20261115-infra-2sha", field_id="custom", posting_id=PID_B)
        self.assertEqual((rating["value"], rating["unit"], rating["company_slug"]), ("2", "", "B_ベータシステムズ"))
        salary = pick(decision_id="20261115-infra-2sha", field_id="salary_min", posting_id=PID_B)
        self.assertEqual((salary["value"], salary["unit"]), ("7000000", "円"))

    def test_unparsable_file_skipped(self) -> None:
        _write(self.root / "career-private" / "matches" / "broken.json", "{ not json")
        code, _, err = self._run()
        self.assertEqual(code, 0)
        self.assertIn("broken.json", err)
        self.assertEqual(len(self._rows()), 14)

    def test_custom_out_path_writes_file(self) -> None:
        target = self.root / "elsewhere" / "out.csv"
        code, _, _ = self._run("--out", str(target))
        self.assertEqual(code, 0)
        self.assertTrue(target.is_file())

    def test_empty_root_exit_1(self) -> None:
        with tempfile.TemporaryDirectory() as empty:
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(ef.main(["--data-root", empty]), 1)
            self.assertFalse((Path(empty) / "export").exists())


if __name__ == "__main__":
    unittest.main()
