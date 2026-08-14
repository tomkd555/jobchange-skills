"""job-change-support: 企業別成果物（companies/{slug}/_manifest.json）の
機械的な（非LLM）鮮度判定ツール。

標準ライブラリのみで、_manifest.json に記録された各成果物の最終更新日と、
トピックごとの TTL（有効期限日数）を突き合わせ、fresh（TTL 内）・stale（TTL 超過）・
missing（manifest に無い既知成果物）に分類する。companies/{slug}/ は
恒久アーカイブであり、本ツールは削除・移動を行わず判定のみを提供する。仕様の原本は
references/freshness-policy.md である。

CLI:
    python check_freshness.py <_manifest.jsonのパス> [--today YYYY-MM-DD] [--json]

終了コード: 常に 0（manifest 未整備・破損時も含め、鮮度情報の提供が役割でありFAILにしない）
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from typing import Any

JOB_POSTING_TTL_DAYS = 30
TOPIC_TTL_DAYS: dict[str, int] = {
    "philosophy": 365,
    "business": 365,
    "financials": 180,
    "compensation": 180,
    "benefits": 180,
    "workstyle": 180,
    "reputation": 90,
    "selection_process": 180,
}
DEFAULT_TOPIC_TTL_DAYS = 180
KNOWN_ARTIFACTS = ("job_posting", "company_research")


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _classify(label: str, date_str: Any, ttl_days: int, today: date) -> tuple[str, dict]:
    """1件の成果物/トピックを fresh・stale・missing のいずれかへ分類する。"""
    parsed = _parse_date(date_str)
    if parsed is None:
        return "missing", {"artifact": label}
    age_days = (today - parsed).days
    entry = {
        "artifact": label,
        "last_date": date_str,
        "age_days": age_days,
        "ttl_days": ttl_days,
    }
    bucket = "fresh" if age_days <= ttl_days else "stale"
    return bucket, entry


def check_freshness(manifest: Any, today: date) -> dict[str, list[dict]]:
    """manifest（読み込み済みJSON）と基準日から鮮度分類を返す。副作用を持たない純粋関数。"""
    result: dict[str, list[dict]] = {"fresh": [], "stale": [], "missing": []}

    artifacts = manifest.get("artifacts") if isinstance(manifest, dict) else None
    if not isinstance(artifacts, dict):
        for label in KNOWN_ARTIFACTS:
            result["missing"].append({"artifact": label})
        return result

    job_posting = artifacts.get("job_posting")
    if not isinstance(job_posting, dict):
        result["missing"].append({"artifact": "job_posting"})
    else:
        bucket, entry = _classify(
            "job_posting", job_posting.get("updated_at"), JOB_POSTING_TTL_DAYS, today
        )
        result[bucket].append(entry)

    company_research = artifacts.get("company_research")
    if not isinstance(company_research, dict):
        result["missing"].append({"artifact": "company_research"})
    else:
        topics = company_research.get("topics")
        if isinstance(topics, dict):
            for topic, info in topics.items():
                last_researched = info.get("last_researched") if isinstance(info, dict) else None
                ttl_days = TOPIC_TTL_DAYS.get(topic, DEFAULT_TOPIC_TTL_DAYS)
                bucket, entry = _classify(
                    f"company_research.{topic}", last_researched, ttl_days, today
                )
                result[bucket].append(entry)
        else:
            # topics が欠落・null・オブジェクト以外なら company_research 全体を missing とする
            # （空のオブジェクトはトピック0件として判定対象にしない）
            result["missing"].append({"artifact": "company_research"})

    return result


def load_manifest(path: str) -> Any:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def format_report(result: dict[str, list[dict]]) -> str:
    lines = [
        f"鮮度判定結果: fresh {len(result['fresh'])}件 / "
        f"stale {len(result['stale'])}件 / missing {len(result['missing'])}件"
    ]
    for bucket in ("fresh", "stale", "missing"):
        for entry in result[bucket]:
            if bucket == "missing":
                lines.append(f"[MISSING] {entry['artifact']}")
            else:
                lines.append(
                    f"[{bucket.upper()}] {entry['artifact']}: "
                    f"last_date={entry['last_date']} age_days={entry['age_days']} "
                    f"ttl_days={entry['ttl_days']}"
                )
    return "\n".join(lines)


def _missing_all() -> dict[str, list[dict]]:
    return {"fresh": [], "stale": [], "missing": [{"artifact": label} for label in KNOWN_ARTIFACTS]}


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="job-change-support 企業別成果物の鮮度判定ツール")
    parser.add_argument("manifest_path", help="判定対象の _manifest.json ファイルパス")
    parser.add_argument("--today", help="基準日（YYYY-MM-DD）。未指定時は実行時点の日付を使う")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    if args.today:
        today = _parse_date(args.today)
        if today is None:
            parser.error("--today は YYYY-MM-DD 形式で指定する")
    else:
        today = date.today()

    try:
        manifest = load_manifest(args.manifest_path)
    except (OSError, json.JSONDecodeError):
        result = _missing_all()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(format_report(result))
        return 0

    result = check_freshness(manifest, today)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_report(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
