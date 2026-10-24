"""job-change-job-search: 求人検索結果（job_search_results.json、schema 3.0）の機械的な（非LLM）検証ツール。

標準ライブラリのみで、求人検索の成果物を ERROR（成果物として成立しない欠落・矛盾）と
WARN（成立するが情報が不足する点）に分けて報告する。仕様の原本は
references/job-search-format.md である。

CLI:
    python validate_job_search_results.py <job_search_results.json> [--json]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from typing import Any

KNOWN_SCHEMA_VERSIONS = ("3.0",)
VALID_MODES = ("fuzzy", "similar_better")
# derivation-lanes.md の「Lane list」表の順。test_vocabulary_sync.py が表との一致を守る。
DERIVATION_LANES = (
    "adjacent_role",
    "industry_widen",
    "seniority_shift",
    "remote_widen",
    "region_widen",
    "better_salary",
    "better_holidays",
    "better_workstyle",
    "company_type",
    "direct_careers",
)
LEGAL_CHECK_KEYS = (
    "scope_of_change_duties",
    "scope_of_change_location",
    "contract_renewal_cap",
    "posted_at",
    "salary_range",
)
LEGAL_CHECK_RESULTS = ("stated", "missing", "not_applicable")
MATCH_RESULTS = ("meets", "not_meets", "unknown")
READ_VIA = ("webfetch", "chrome")

# validate_company_index.SLUG_PATTERN と同じ正規表現（test_vocabulary_sync.py が一致を守る）。
_SLUG_RE = re.compile(
    r"^([A-Z]_)?"
    r"[0-9A-Za-z぀-ヿ㐀-鿿＀-￯]"
    r"[0-9A-Za-z぀-ヿ㐀-鿿＀-￯-]*$"
)
_SEARCH_ID_RE = re.compile(r"^[0-9]{8}-[0-9a-z][0-9a-z-]*$")
_CONDITION_ID_RE = re.compile(r"^c[0-9]{3}$")
_POSTING_ID_RE = re.compile(r"^(.+)-[0-9]{8}-[0-9]{2}$")
_DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
# 1 レーンあたりの検索件数の目安（derivation-lanes.md の「up to 3」）。
_MAX_QUERIES_PER_LANE = 3

# company_key の正規化で先頭・末尾から取り除く法人格の表記。NFKC 後の形で書く。
_LEGAL_ENTITY_TOKENS = (
    "株式会社",
    "有限会社",
    "合同会社",
    "合資会社",
    "合名会社",
    "一般社団法人",
    "一般財団法人",
    "公益社団法人",
    "公益財団法人",
    "(株)",
    "(有)",
    "(同)",
)


def normalize_company_key(name: Any) -> str:
    """企業名を company_key へ正規化する。merge_search_results.py と共用する唯一の実装である。

    NFKC 正規化（全角英数→半角、（株）・㈱→(株)）→ 空白の全除去 → 先頭・末尾の法人格表記の除去
    （中間の表記は残す）→ ASCII の小文字化。法人格だけの名前は空文字を返す。
    """
    if not isinstance(name, str):
        return ""
    s = unicodedata.normalize("NFKC", name)
    s = "".join(s.split())
    changed = True
    while changed and s:
        changed = False
        for token in _LEGAL_ENTITY_TOKENS:
            if s.startswith(token):
                s = s[len(token):]
                changed = True
            if s.endswith(token):
                s = s[: -len(token)]
                changed = True
    return s.lower()


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, path: str, message: str) -> None:
        self.errors.append(f"[ERROR] {path}: {message}")

    def add_warning(self, path: str, message: str) -> None:
        self.warnings.append(f"[WARN] {path}: {message}")

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {
            "status": "PASS" if self.ok else "FAIL",
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_date(value: Any) -> bool:
    if not isinstance(value, str) or not _DATE_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _check_date(value: Any, path: str, result: ValidationResult, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not _is_date(value):
        result.add_error(path, "YYYY-MM-DD 形式の実在する日付でなければならない")


def _validate_root(doc: dict, result: ValidationResult) -> tuple[list[dict], set[str]]:
    """ルート項目を検査し、(conditions の有効な要素, derivations の lane 集合) を返す。"""
    types = {
        "schema_version": str, "search_id": str, "mode": str, "executed_at": str,
        "conditions": list, "derivations": list, "results": list, "search_log": list,
    }
    for key, typ in types.items():
        if key not in doc:
            result.add_error(key, "必須項目が無い")
        elif not isinstance(doc[key], typ):
            result.add_error(key, f"{typ.__name__} でなければならない")

    if isinstance(doc.get("schema_version"), str) and doc["schema_version"] not in KNOWN_SCHEMA_VERSIONS:
        result.add_warning("schema_version", f"既知の版 {KNOWN_SCHEMA_VERSIONS} の外である")

    executed_at = doc.get("executed_at")
    if isinstance(executed_at, str):
        _check_date(executed_at, "executed_at", result)
    search_id = doc.get("search_id")
    if isinstance(search_id, str):
        if not _SEARCH_ID_RE.match(search_id):
            result.add_error("search_id", "^[0-9]{8}-[0-9a-z][0-9a-z-]*$ に合わない")
        elif _is_date(executed_at) and search_id[:8] != executed_at.replace("-", ""):
            result.add_error("search_id", "日付部分が executed_at と一致しない")

    mode = doc.get("mode")
    if isinstance(mode, str) and mode not in VALID_MODES:
        result.add_error("mode", f"{VALID_MODES} のいずれかでなければならない")
        mode = None

    baseline = doc.get("baseline")
    if baseline is not None:
        pid = baseline.get("posting_id") if isinstance(baseline, dict) else None
        if not _nonempty(pid):
            result.add_error("baseline", "posting_id 文字列を持つオブジェクトまたは null でなければならない")
        else:
            m = _POSTING_ID_RE.match(pid)
            if not m or not _SLUG_RE.match(m.group(1)):
                result.add_error("baseline.posting_id", "{slug}-{YYYYMMDD}-{NN} 形式でなければならない")
        if mode == "fuzzy":
            result.add_warning("baseline", "fuzzy では baseline を持たない")
    elif mode == "similar_better":
        result.add_warning("baseline", "similar_better では baseline が必要である")

    if not isinstance(doc.get("coverage_notes", ""), (str, type(None))):
        result.add_error("coverage_notes", "文字列でなければならない")
    oq = doc.get("open_questions")
    if oq is not None and (not isinstance(oq, list) or not all(isinstance(q, str) for q in oq)):
        result.add_error("open_questions", "文字列の配列でなければならない")

    conditions: list[dict] = []
    if isinstance(doc.get("conditions"), list):
        if not doc["conditions"]:
            result.add_warning("conditions", "conditions が空である")
        for i, c in enumerate(doc["conditions"]):
            path = f"conditions[{i}]"
            if not isinstance(c, dict):
                result.add_error(path, "オブジェクトでなければならない")
                continue
            if not (isinstance(c.get("condition_id"), str) and _CONDITION_ID_RE.match(c["condition_id"])):
                result.add_error(f"{path}.condition_id", "^c[0-9]{3}$ に合わない")
            for k in ("kind", "text", "level"):
                if not _nonempty(c.get(k)):
                    result.add_error(f"{path}.{k}", "空でない文字列でなければならない")
            conditions.append(c)

    lanes: set[str] = set()
    if isinstance(doc.get("derivations"), list):
        for i, d in enumerate(doc["derivations"]):
            path = f"derivations[{i}]"
            if not isinstance(d, dict):
                result.add_error(path, "オブジェクトでなければならない")
                continue
            lane = d.get("lane")
            if lane not in DERIVATION_LANES:
                result.add_error(f"{path}.lane", f"{DERIVATION_LANES} のいずれかでなければならない")
            elif lane in lanes:
                result.add_error(f"{path}.lane", f"lane {lane} が重複している")
            else:
                lanes.add(lane)
            cc = d.get("changed_conditions")
            if not isinstance(cc, list) or not all(_nonempty(x) for x in cc):
                result.add_error(f"{path}.changed_conditions", "空でない文字列の配列でなければならない")
            if not _nonempty(d.get("rationale")):
                result.add_error(f"{path}.rationale", "空でない文字列でなければならない")
    return conditions, lanes


def _validate_legal_check(lc: Any, path: str, result: ValidationResult) -> int:
    """legal_check を検査し、missing の件数を返す。"""
    if not isinstance(lc, dict):
        result.add_error(path, "オブジェクトでなければならない")
        return 0
    for key in LEGAL_CHECK_KEYS:
        if key not in lc:
            result.add_error(f"{path}.{key}", "必須のキーが無い")
    for key in lc:
        if key not in LEGAL_CHECK_KEYS:
            result.add_error(f"{path}.{key}", "仕様に無いキーである")
    missing = 0
    for key in LEGAL_CHECK_KEYS:
        if key not in lc:
            continue
        item = lc[key]
        p = f"{path}.{key}"
        if not isinstance(item, dict) or "result" not in item or "quote" not in item:
            result.add_error(p, "result と quote を持つオブジェクトでなければならない")
            continue
        if item["result"] not in LEGAL_CHECK_RESULTS:
            result.add_error(f"{p}.result", f"{LEGAL_CHECK_RESULTS} のいずれかでなければならない")
        elif item["result"] == "stated" and not _nonempty(item["quote"]):
            result.add_error(f"{p}.quote", "result が stated のとき quote は空にできない")
        elif item["result"] == "missing":
            missing += 1
    return missing


def _validate_must_match(mm: Any, must_ids: set[str], path: str, result: ValidationResult) -> None:
    if not isinstance(mm, list):
        result.add_error(path, "配列でなければならない")
        return
    seen: list[Any] = []
    for i, m in enumerate(mm):
        p = f"{path}[{i}]"
        if not isinstance(m, dict):
            result.add_error(p, "オブジェクトでなければならない")
            continue
        seen.append(m.get("condition_id"))
        if m.get("result") not in MATCH_RESULTS:
            result.add_error(f"{p}.result", f"{MATCH_RESULTS} のいずれかでなければならない")
        elif m["result"] in ("meets", "not_meets") and not _nonempty(m.get("basis")):
            result.add_error(f"{p}.basis", "result が meets / not_meets のとき basis は空にできない")
    for cid in sorted(must_ids - set(seen)):
        result.add_error(path, f"must 条件 {cid} の判定が無い")
    for cid in seen:
        if cid not in must_ids:
            result.add_error(path, f"condition_id {cid!r} は must 条件に無い")
    if len(seen) != len(set(seen)):
        result.add_error(path, "condition_id が重複している")


_NULLABLE_STR_KEYS = ("salary_range", "location", "remote_policy", "employment_type")
_NULLABLE_KEYS = _NULLABLE_STR_KEYS + ("annual_holidays", "posted_at", "lane", "considering")


def _validate_results(doc: dict, conditions: list[dict], lanes: set[str], result: ValidationResult) -> set[str]:
    """results を検査し、results が名指す lane の集合を返す。"""
    must_ids = {
        c["condition_id"] for c in conditions
        if c.get("level") == "must" and isinstance(c.get("condition_id"), str)
    }
    results = doc.get("results")
    used: set[str] = set()
    if not isinstance(results, list):
        return used
    if not results:
        result.add_warning("results", "results が空である")
    considerings = []
    for i, r in enumerate(results):
        path = f"results[{i}]"
        if not isinstance(r, dict):
            result.add_error(path, "オブジェクトでなければならない")
            continue
        for key in ("title", "company_name", "source_site", "quote", "match_notes"):
            if key not in r:
                result.add_error(f"{path}.{key}", "必須項目が無い")
            elif not _nonempty(r[key]):
                result.add_error(f"{path}.{key}", "空でない文字列でなければならない")
        if "url" not in r:
            result.add_error(f"{path}.url", "必須項目が無い")
        elif not (isinstance(r["url"], str) and r["url"].startswith("http")):
            result.add_error(f"{path}.url", "http で始まる文字列でなければならない")
        if "read_via" not in r:
            result.add_error(f"{path}.read_via", "必須項目が無い")
        elif r["read_via"] not in READ_VIA:
            result.add_error(f"{path}.read_via", f"{READ_VIA} のいずれかでなければならない")
        for key in _NULLABLE_KEYS:
            if key not in r:
                result.add_error(f"{path}.{key}", "必須項目が無い（値が無いときは null）")
        for key in _NULLABLE_STR_KEYS:
            if key in r and not isinstance(r[key], (str, type(None))):
                result.add_error(f"{path}.{key}", "文字列または null でなければならない")
        if r.get("annual_holidays") is not None and not _is_int(r["annual_holidays"]):
            result.add_error(f"{path}.annual_holidays", "整数または null でなければならない")
        if "posted_at" in r:
            _check_date(r["posted_at"], f"{path}.posted_at", result, nullable=True)
        if r.get("lane") is not None:
            if r["lane"] not in lanes:
                result.add_error(f"{path}.lane", "derivations に無い lane である")
            else:
                used.add(r["lane"])
        if "considering" in r:
            considerings.append(r["considering"])
            if r["considering"] not in (True, False, None):
                result.add_error(f"{path}.considering", "true / false / null のいずれかでなければならない")
        if "legal_check" not in r:
            result.add_error(f"{path}.legal_check", "必須項目が無い")
        elif _validate_legal_check(r["legal_check"], f"{path}.legal_check", result) >= 2:
            result.add_warning(f"{path}.legal_check", "missing が 2 件以上ある（必須の記載項目を複数欠く求人）")
        if "must_match" not in r:
            result.add_error(f"{path}.must_match", "必須項目が無い")
        else:
            _validate_must_match(r["must_match"], must_ids, f"{path}.must_match", result)
    if considerings and all(c is None for c in considerings):
        result.add_warning("results", "considering が全件 null である（利用者がまだ印を付けていない）")
    return used


def _validate_search_log(doc: dict, lanes: set[str], used_lanes: set[str], result: ValidationResult) -> None:
    log = doc.get("search_log")
    if not isinstance(log, list):
        return
    if not log:
        result.add_error("search_log", "空にできない")
        return
    per_lane: dict[str, int] = {}
    for i, e in enumerate(log):
        path = f"search_log[{i}]"
        if not isinstance(e, dict):
            result.add_error(path, "オブジェクトでなければならない")
            continue
        for key in ("query", "source", "url", "fetched_at", "hit_count", "adopted_count", "lane"):
            if key not in e:
                result.add_error(f"{path}.{key}", "必須項目が無い")
        for key in ("query", "source"):
            if key in e and not _nonempty(e[key]):
                result.add_error(f"{path}.{key}", "空でない文字列でなければならない")
        if e.get("url") is not None and not (isinstance(e["url"], str) and e["url"].startswith("http")):
            result.add_error(f"{path}.url", "http で始まる文字列または null でなければならない")
        if "fetched_at" in e:
            _check_date(e["fetched_at"], f"{path}.fetched_at", result, nullable=True)
        for key in ("hit_count", "adopted_count"):
            if e.get(key) is not None and not (_is_int(e[key]) and e[key] >= 0):
                result.add_error(f"{path}.{key}", "0 以上の整数または null でなければならない")
        lane = e.get("lane")
        if lane is not None:
            if lane not in lanes:
                result.add_error(f"{path}.lane", "derivations に無い lane である")
            else:
                per_lane[lane] = per_lane.get(lane, 0) + 1
    # 主検索（lane が null）は件数を数えない。上限の目安は派生レーンの検索に対するものである。
    for lane, n in per_lane.items():
        if n > _MAX_QUERIES_PER_LANE:
            result.add_warning("search_log", f"lane {lane} の検索が {n} 件ある（目安は {_MAX_QUERIES_PER_LANE} 件まで）")
    for lane in sorted(used_lanes - set(per_lane)):
        result.add_error("search_log", f"results が名指す lane {lane} を持つ search_log が無い")


def validate(document: Any) -> ValidationResult:
    result = ValidationResult()
    if not isinstance(document, dict):
        result.add_error("$", "ルートはオブジェクトでなければならない")
        return result
    conditions, lanes = _validate_root(document, result)
    used = _validate_results(document, conditions, lanes, result)
    _validate_search_log(document, lanes, used, result)
    return result


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def format_report(result: ValidationResult) -> str:
    status = "PASS" if result.ok else "FAIL"
    lines = [f"検証結果: {status}（ERROR {len(result.errors)}件 / WARN {len(result.warnings)}件）"]
    lines.extend(result.errors)
    lines.extend(result.warnings)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="job-change-job-search 求人検索結果検証ツール")
    parser.add_argument("results_path", help="検証対象の job_search_results.json ファイルパス")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    try:
        result = validate(load_json(args.results_path))
    except (OSError, ValueError) as exc:
        result = ValidationResult()
        result.add_error(args.results_path, f"JSON として読み込めない（{exc}）")

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
