"""job-change-support: 利用者データを「候補 × 項目」の縦持ち CSV に書き出すツール。

データルート配下の wishes.json、各求人の posting-check.json、matches/*.json、decisions/*.json を読み、
1 行 = 1 候補 × 1 項目の CSV にする。Excel で開けるよう UTF-8（BOM 付き）で書く。
読めないファイルは標準エラーへパスを出して飛ばす。

CLI:
    python export_flat.py --data-root <dir> [--out <csv path>]

終了コード: 0 = 1 行以上を書いた、1 = 1 行も書けなかった
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jc_config  # noqa: E402
from field_catalog import load_catalog  # noqa: E402

COLUMNS = (
    "decision_id", "posting_id", "company_slug", "field_id", "value", "unit",
    "as_of", "source_url", "grade", "source_file", "condition_id",
)
_POSTING_SUFFIX = re.compile(r"-[0-9]{8}-[0-9]{2}$")


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _row(**kw: Any) -> dict[str, str]:
    return {c: _cell(kw.get(c)) for c in COLUMNS}


def _slug_of(posting_id: Any) -> str:
    return _POSTING_SUFFIX.sub("", posting_id) if isinstance(posting_id, str) else ""


def _read(path: Path) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        doc = None
    if not isinstance(doc, dict):
        print(f"読めないため飛ばす: {path}", file=sys.stderr)
        return None
    return doc


def _list(value: Any) -> list:
    return value if isinstance(value, list) else []


def wishes_rows(doc: dict, path: Path) -> list[dict[str, str]]:
    return [
        _row(field_id=c.get("field_id"), value=c.get("value"), unit=c.get("unit"),
             source_file=path, condition_id=c.get("id"))
        for c in _list(doc.get("conditions")) if isinstance(c, dict)
    ]


def posting_rows(doc: dict, path: Path) -> list[dict[str, str]]:
    rows = []
    for section in ("job", "company"):
        section_value = doc.get(section)
        for field_id, entry in (section_value.items() if isinstance(section_value, dict) else []):
            for obj in entry if isinstance(entry, list) else [entry]:
                if isinstance(obj, dict):
                    rows.append(_row(
                        posting_id=doc.get("posting_id"), company_slug=doc.get("company_slug"),
                        field_id=field_id, value=obj.get("value"), unit=obj.get("unit"),
                        as_of=obj.get("as_of"), source_url=obj.get("source_url"),
                        grade=obj.get("grade"), source_file=path,
                    ))
    return rows


def match_rows(doc: dict, path: Path) -> list[dict[str, str]]:
    pid = doc.get("posting_id")
    return [
        _row(posting_id=pid, company_slug=_slug_of(pid), field_id=m.get("basis_field_id"),
             value=m.get("result"), as_of=doc.get("checked_at"), source_file=path,
             condition_id=m.get("condition_id"))
        for m in _list(doc.get("match")) if isinstance(m, dict)
    ]


def decision_rows(doc: dict, path: Path, catalog: Any) -> list[dict[str, str]]:
    rows = []
    for crit in _list(doc.get("criteria")):
        if not isinstance(crit, dict):
            continue
        spec = catalog.fields.get(crit.get("field_id"))
        # 数値項目は values、それ以外は ratings に利用者の入力がある。
        data = crit.get("values") if isinstance(crit.get("values"), dict) else crit.get("ratings")
        if not isinstance(data, dict):
            continue
        for cand in _list(doc.get("candidates")):
            if isinstance(cand, dict):
                rows.append(_row(
                    decision_id=doc.get("id"), posting_id=cand.get("posting_id"),
                    company_slug=cand.get("company_slug"), field_id=crit.get("field_id"),
                    value=data.get(cand.get("posting_id")), unit=spec.unit if spec else None,
                    source_file=path,
                ))
    return rows


def collect(data_root: Path, private_dir: str = "career-private", companies_dir: str = "companies") -> list[dict[str, str]]:
    catalog = load_catalog()
    private = data_root / private_dir
    sources = (
        ([private / "wishes.json"], wishes_rows),
        (sorted((data_root / companies_dir).glob("*/postings/*/posting-check.json")), posting_rows),
        (sorted((private / "matches").glob("*.json")), match_rows),
        (sorted((private / "decisions").glob("*.json")),
         lambda doc, path: decision_rows(doc, path, catalog)),
    )
    rows: list[dict[str, str]] = []
    for paths, build in sources:
        for path in paths:
            doc = _read(path) if path.is_file() else None
            if doc is not None:
                rows.extend(build(doc, path))
    return rows


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="job-change-support 縦持ち CSV 書き出しツール")
    parser.add_argument("--data-root", help="利用者データの置き場所（省略時は設定ファイルの data_root）")
    parser.add_argument("--out", help="出力する CSV のパス（既定: <data-root>/export/flat.csv）")
    args = parser.parse_args(argv)

    # ディレクトリ名は設定ファイルに従う。設定が無ければ既定名を使う。
    dirs = dict(jc_config.DEFAULTS)
    config_path, _ = jc_config.find_config_path()
    if config_path is not None:
        try:
            dirs = jc_config.load_config(config_path)
        except jc_config.ConfigError as exc:
            print(f"設定ファイルが読めない: {exc}", file=sys.stderr)
    if not args.data_root and "data_root" not in dirs:
        print("--data-root か設定ファイルの data_root が必要である", file=sys.stderr)
        return 1
    data_root = Path(args.data_root or dirs["data_root"])
    out = Path(args.out) if args.out else data_root / "export" / "flat.csv"
    rows = collect(data_root, dirs["private_dir"], dirs["companies_dir"])
    if not rows:
        print("書き出す行がない", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} 行を書き出した: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
