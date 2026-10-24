"""job-change-job-search: 検索担当と Chrome 読取の partial ファイルを 1 つの job_search_results.json へ統合するツール。

検索担当は `job_search_results.partial-searcher.json`、本体セッションは Chrome で読んだページを
`job_search_results.partial-chrome.json` に書く。本ツールはそれらを読み、重複を除いて
`job_search_results.json` を書き出す。仕様の原本は references/job-search-format.md の
「Partial files and the merge」である。

CLI:
    python merge_search_results.py <search_dir> [--json]
    python merge_search_results.py <search_dir> --cleanup [--json]

`--cleanup` は partial ファイルを削除する（統合しない）。検証が PASS した後に実行する。

終了コード: 0 = 成功、1 = partial が無い、または partial を読み込めない
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from typing import Any

from validate_job_search_results import normalize_company_key

_PARTIAL_GLOB = "job_search_results.partial-*.json"
_PARTIAL_SEARCHER = "job_search_results.partial-searcher.json"
_OUTPUT = "job_search_results.json"
_HEADER_KEYS = ("schema_version", "search_id", "mode", "executed_at", "conditions", "baseline")


def _normalize_title(title: Any) -> str:
    """空白（全角・半角）を全て除き、小文字にする。"""
    return "".join(str(title).split()).lower() if title is not None else ""


def _partial_paths(search_dir: str) -> list[str]:
    # 検索担当の partial を先頭に置き、結果の並びと「最初を残す」重複排除の優先を検索担当にする。
    return sorted(glob.glob(os.path.join(search_dir, _PARTIAL_GLOB)),
                  key=lambda p: (os.path.basename(p) != _PARTIAL_SEARCHER, p))


def _load_partials(paths: list[str], errors: list[str]) -> list[tuple[str, dict]]:
    partials = []
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                doc = json.load(f)
            if not isinstance(doc, dict):
                raise ValueError("ルート要素はオブジェクトでなければならない")
        except (OSError, ValueError) as exc:
            errors.append(f"{os.path.basename(path)} を読み込めない（{exc}）")
            continue
        partials.append((path, doc))
    return partials


def merge(search_dir: str) -> dict:
    """統合して書き出し、{status, errors, warnings, result_count, removed_count, output_path} を返す。"""
    out: dict[str, Any] = {
        "status": "FAIL", "errors": [], "warnings": [],
        "result_count": 0, "removed_count": 0, "output_path": None,
    }
    paths = _partial_paths(search_dir)
    if not paths:
        out["errors"].append(f"{_PARTIAL_GLOB} が {search_dir} に無い")
        return out
    partials = _load_partials(paths, out["errors"])
    if out["errors"]:
        return out

    base = next((d for p, d in partials if os.path.basename(p) == _PARTIAL_SEARCHER), partials[0][1])
    merged: dict[str, Any] = {k: base[k] for k in _HEADER_KEYS if k in base}

    results: list[dict] = []
    seen: set[tuple[str, str]] = set()
    removed = 0
    search_log: list = []
    derivations: list = []
    lanes: set[Any] = set()
    notes: list[str] = []
    questions: list = []
    for _, doc in partials:
        for r in doc.get("results") or []:
            key = (normalize_company_key(r.get("company_name") if isinstance(r, dict) else None),
                   _normalize_title(r.get("title") if isinstance(r, dict) else None))
            if key in seen:
                removed += 1
                continue
            seen.add(key)
            results.append(r)
        search_log.extend(doc.get("search_log") or [])
        for d in doc.get("derivations") or []:
            lane = d.get("lane") if isinstance(d, dict) else None
            if lane in lanes:
                continue
            lanes.add(lane)
            derivations.append(d)
        if doc.get("coverage_notes"):
            notes.append(doc["coverage_notes"])
        for q in doc.get("open_questions") or []:
            if q not in questions:
                questions.append(q)

    coverage = "\n".join(notes)
    if removed > 0:
        coverage = (coverage + "\n" if coverage else "") + f"重複 {removed} 件を除いた"
    merged.update(
        derivations=derivations, results=results, search_log=search_log,
        coverage_notes=coverage, open_questions=questions,
    )

    output_path = os.path.join(search_dir, _OUTPUT)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write("\n")
    out.update(status="OK", result_count=len(results), removed_count=removed, output_path=output_path)
    return out


def cleanup(search_dir: str) -> dict:
    paths = _partial_paths(search_dir)
    for p in paths:
        os.remove(p)
    return {"status": "OK", "errors": [], "warnings": [], "deleted": [os.path.basename(p) for p in paths]}


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="job-change-job-search partial 統合ツール")
    parser.add_argument("search_dir", help="job_search_results.partial-*.json があるディレクトリ")
    parser.add_argument("--cleanup", action="store_true", help="partial ファイルを削除する（統合しない）")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    out = cleanup(args.search_dir) if args.cleanup else merge(args.search_dir)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif out["errors"]:
        print("統合結果: FAIL")
        for e in out["errors"]:
            print(f"[ERROR] {e}")
    elif args.cleanup:
        print(f"partial {len(out['deleted'])} 件を削除した")
    else:
        print(f"統合結果: OK（結果 {out['result_count']} 件、重複 {out['removed_count']} 件を除去）-> {out['output_path']}")
    return 1 if out["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
