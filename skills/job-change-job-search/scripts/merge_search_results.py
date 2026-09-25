"""job-change-job-search: 並列検索担当が書いた partial ファイル群を1つの job_search_results.json へ統合するツール。

求人検索スキルは primary（必須の主検索）と、0件以上の派生レーン検索を並列の searcher エージェントへ振り
分ける。各エージェントは観測層だけを持つ job_search_results.json 形状のファイルを
`job_search_results.partial-primary.json`・`job_search_results.partial-lanes-N.json` として書き、
企業情報の収集担当（同じ検索担当の company_profile モード）は
`company_profiles.batch-N.json` を書く。本ツールはそれらを読み、重複排除・現勤務先の
除外・企業キーの付与を行ったうえで `job_search_results.json` を書き出す。判定層（`axis_judgements`・
`classification`・`classification_reasons`・`classification_override`・`slug`・
`baseline_comparison.overall`・トップレベルの `screening`）はスキル本体が別途書くため、本ツールは
これらを取り除いた状態で出力する。

CLI:
    python merge_search_results.py <search_dir> --list-companies [--profile <profile.json>] [--json]
    python merge_search_results.py <search_dir> [--profile <profile.json>] [--lanes a,b,...]
        [--stub-missing] [--json]
    python merge_search_results.py <search_dir> --cleanup [--json]

`--list-companies`（phase A）は何も書き込まず、現勤務先を除外したうえで企業の一覧を表示するだけである。
phase A を付けない実行（phase B）は統合結果を `<search_dir>/job_search_results.json` へ書き出す。
partial・batch ファイルは残す。検証（validate_job_search_results.py）が PASS した後に `--cleanup` で
削除する。検証が FAIL したときに統合をやり直せるようにするためである。

終了コード: 0 = OK（ERROR 0件。WARN があっても OK。実施できなかったレーンの報告だけでは ERROR にしない）、
1 = ERROR（1件以上。phase B では何も書き込まない）
"""
from __future__ import annotations

import argparse
import difflib
import glob
import json
import os
import re
import sys
import unicodedata
import urllib.parse
from dataclasses import dataclass, field
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validate_job_search_results import (  # noqa: E402
    COMPANY_METRIC_UNITS,
    _V23_SCHEMA_VERSION,
    collect_pii_terms,
    load_json,
    normalize_company_key,
)

_PRIMARY_PARTIAL_NAME = "job_search_results.partial-primary.json"
_PARTIAL_GLOB = "job_search_results.partial-*.json"
_BATCH_GLOB = "company_profiles.batch-*.json"

# 判定層のうち、result 1件ごとに除去するキー。screening と baseline_comparison.overall は別扱い。
_JUDGEMENT_RESULT_KEYS = (
    "axis_judgements",
    "classification",
    "classification_reasons",
    "classification_override",
    "slug",
)

# 市区町村の抽出に用いる正規表現。地名の直前にある区切り（空白・全角/半角括弧・読点）の手前までを拾う。
# ponytail: 正規表現の近似。市名に区を含む地名では切り方を誤る。重複の見逃しが問題になれば辞書へ置き換える
_MUNICIPALITY_RE = re.compile(r"[^\s（(、,]+?[市区町村]")

# 近似重複と見なす、正規化タイトルの類似度のしきい値（difflib.SequenceMatcher.ratio）。
_NEAR_DUP_RATIO_THRESHOLD = 0.8

# company_profiles[].metrics の軸キーと単位。正本は validate_job_search_results.COMPANY_METRIC_UNITS。
_METRIC_UNITS = COMPANY_METRIC_UNITS


@dataclass
class MergeResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    excluded_count: int = 0
    companies: list[dict] = field(default_factory=list)
    missing_lanes: list[str] = field(default_factory=list)
    output_path: str | None = None

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
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "excluded_count": self.excluded_count,
            "companies": list(self.companies),
            "missing_lanes": list(self.missing_lanes),
            "output_path": self.output_path,
        }


def _make_result(
    errors: list[str],
    warnings: list[str],
    excluded_count: int = 0,
    companies: list[dict] | None = None,
    missing_lanes: list[str] | None = None,
    output_path: str | None = None,
) -> MergeResult:
    return MergeResult(
        errors=list(errors),
        warnings=list(warnings),
        excluded_count=excluded_count,
        companies=list(companies or []),
        missing_lanes=list(missing_lanes or []),
        output_path=output_path,
    )


def load_partials(search_dir: str) -> tuple[list[tuple[str, dict]], list[str]]:
    """search_dir から job_search_results.partial-*.json を、ソート済みグロブの順に読み込む。

    partial が1件も無い、primary が無い、JSON として読めないファイルがある場合は、
    戻り値の errors へ ERROR を積む（primary 欠落は他ファイルが読めても検査を続ける）。
    """
    errors: list[str] = []
    paths = sorted(glob.glob(os.path.join(search_dir, _PARTIAL_GLOB)))
    if not paths:
        errors.append(f"[ERROR] (partials): {_PARTIAL_GLOB} に一致するファイルが1件も無い")
        return [], errors

    names = [os.path.basename(p) for p in paths]
    if _PRIMARY_PARTIAL_NAME not in names:
        errors.append(f"[ERROR] (partials): {_PRIMARY_PARTIAL_NAME} が無い")

    partials: list[tuple[str, dict]] = []
    for path, name in zip(paths, names):
        try:
            partials.append((name, load_json(path)))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[ERROR] {name}: JSON として読み込めない（{exc}）")
    return partials, errors


def check_consistency(partials: list[tuple[str, dict]]) -> list[str]:
    """全 partial で schema_version（2.3固定）・search_id・mode・executed_at が一致するか検査する。"""
    errors: list[str] = []
    search_ids: set[Any] = set()
    modes: set[Any] = set()
    executed_ats: set[Any] = set()
    for name, doc in partials:
        if not isinstance(doc, dict):
            errors.append(f"[ERROR] {name}: ルート要素はオブジェクトでなければならない")
            continue
        version = doc.get("schema_version")
        if version != _V23_SCHEMA_VERSION:
            errors.append(f"[ERROR] {name}.schema_version: 2.3 でなければならない（実値: {version!r}）")
        search_ids.add(doc.get("search_id"))
        modes.add(doc.get("mode"))
        executed_ats.add(doc.get("executed_at"))
    if len(search_ids) > 1:
        errors.append(f"[ERROR] (partials).search_id: partial 間で一致しない（{sorted(map(repr, search_ids))}）")
    if len(modes) > 1:
        errors.append(f"[ERROR] (partials).mode: partial 間で一致しない（{sorted(map(repr, modes))}）")
    if len(executed_ats) > 1:
        errors.append(f"[ERROR] (partials).executed_at: partial 間で一致しない（{sorted(map(repr, executed_ats))}）")
    return errors


def strip_judgement(doc: dict) -> list[str]:
    """観測層のドキュメントから判定層のフィールドを取り除く（破壊的）。除去1件につき1件の WARN を返す。"""
    warnings: list[str] = []
    if "screening" in doc:
        del doc["screening"]
        warnings.append("[WARN] screening: 判定層のフィールドを除去した（判定はスキル本体が別途書く）")
    for i, item in enumerate(doc.get("results") or []):
        if not isinstance(item, dict):
            continue
        for key in _JUDGEMENT_RESULT_KEYS:
            if key in item:
                del item[key]
                warnings.append(f"[WARN] results[{i}].{key}: 判定層のフィールドを除去した")
        comparison = item.get("baseline_comparison")
        if isinstance(comparison, dict) and "overall" in comparison:
            del comparison["overall"]
            warnings.append(f"[WARN] results[{i}].baseline_comparison.overall: 判定層のフィールドを除去した")
    return warnings


def current_employer_keys(profile: Any) -> set[str]:
    """profile.json から現勤務先の company_key の集合を返す（--profile 指定時のみ呼ぶ）。"""
    terms = collect_pii_terms(profile)
    keys = {normalize_company_key(value) for label, value in terms if label == "現勤務先名"}
    keys.discard("")
    return keys


def _municipality(location: Any) -> str:
    """住所らしき文字列から市区町村までの部分を取り出す。取り出せなければ全体（空白除去）を返す。"""
    if not isinstance(location, str):
        return ""
    match = _MUNICIPALITY_RE.search(location)
    if match:
        return match.group(0)
    return location.strip()


def dedup_key(item: dict) -> str:
    """重複排除に用いるキーを組み立てる。企業キー・タイトル先頭12字・市区町村・給与レンジで決める。"""
    company_key = normalize_company_key(item.get("company_name"))
    title = item.get("title")
    title_norm = unicodedata.normalize("NFKC", title).strip() if isinstance(title, str) else ""
    municipality = _municipality(item.get("location"))
    salary_range = item.get("salary_range") or ""
    return f"{company_key}|{title_norm[:12]}|{municipality}|{salary_range}"


def _source_rank(item: dict) -> int:
    """情報源の優先度を返す（数値が小さいほど優先）。直接応募系サイトを最優先、求人ボックスを最下位に置く。"""
    url = item.get("url")
    host = ""
    path = ""
    if isinstance(url, str):
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower()
        path = parsed.path or ""
    if host.endswith("hrmos.co") or host.endswith("findy-code.io"):
        return 1
    if host.endswith("herp.careers") and path.startswith("/v1/"):
        return 1
    if "xn--pckua2a7gp15o89zb.com" in host or item.get("source_site") == "求人ボックス":
        return 3
    return 2


def merge_results(
    ordered_docs: list[dict], exclude_keys: set[str]
) -> tuple[list[dict], list[str], int]:
    """複数 partial の results を統合する。

    現勤務先の求人をまず除外し（件数だけ数え、企業名は記録しない）、primary を先頭に他の partial を
    ファイル順で連結したうえで、dedup_key が衝突する求人は _source_rank が低い方（優先度が高い方）を残す。
    同順位（tie）では先に現れた方、すなわち primary 側を残す。

    戻り値: (統合後の results, coverage_notes に足す注記, 現勤務先を理由に除外した件数)。
    """
    candidates: list[dict] = []
    excluded_count = 0
    for doc in ordered_docs:
        for item in doc.get("results") or []:
            if not isinstance(item, dict):
                continue
            key = normalize_company_key(item.get("company_name"))
            if key and key in exclude_keys:
                excluded_count += 1
                continue
            candidates.append(item)

    kept: dict[str, dict] = {}
    order: list[str] = []
    dup_count = 0
    for item in candidates:
        key = dedup_key(item)
        if key not in kept:
            kept[key] = item
            order.append(key)
            continue
        dup_count += 1
        current = kept[key]
        # 主集合の求人は派生の求人に置き換えない（置き換えると求人が主集合からレーンへ移ってしまう）。
        # 同じ集合どうしでだけ、出典の優先順位が高い方を残す。
        if current.get("search_set") == "primary" and item.get("search_set") != "primary":
            continue
        if current.get("search_set") != "primary" and item.get("search_set") == "primary":
            kept[key] = item
            continue
        if _source_rank(item) < _source_rank(current):
            kept[key] = item

    results = [kept[key] for key in order]
    notes = [f"重複排除: {dup_count}件"]
    if excluded_count:
        notes.append(f"現勤務先の求人を除外: {excluded_count}件（企業名は記録しない）")
    return results, notes, excluded_count


def near_dup_notes(results: list[dict]) -> list[str]:
    """同一企業・同一市区町村でタイトルの類似度が高い（≧0.8）別求人を coverage_notes 向けの注記にする。

    dedup_key が異なる組（重複排除では拾えなかった組）だけを対象にする。両方とも results に残したまま、
    統合はしない。件数が少ない前提で総当たりする。
    """
    notes: list[str] = []
    n = len(results)
    for i in range(n):
        a = results[i]
        key_a = normalize_company_key(a.get("company_name"))
        if not key_a:
            continue
        muni_a = _municipality(a.get("location"))
        title_a = unicodedata.normalize("NFKC", a.get("title") or "").strip()
        for j in range(i + 1, n):
            b = results[j]
            if normalize_company_key(b.get("company_name")) != key_a:
                continue
            if _municipality(b.get("location")) != muni_a:
                continue
            if dedup_key(a) == dedup_key(b):
                continue
            title_b = unicodedata.normalize("NFKC", b.get("title") or "").strip()
            ratio = difflib.SequenceMatcher(None, title_a, title_b).ratio()
            if ratio >= _NEAR_DUP_RATIO_THRESHOLD:
                notes.append(f"類似の可能性: {title_a} / {title_b}（{a.get('company_name')}）")
    return notes


def _count_metric_values(profile: Any) -> int:
    """company_profiles[].metrics のうち value が非null なものの件数を返す。"""
    if not isinstance(profile, dict):
        return -1
    metrics = profile.get("metrics")
    if not isinstance(metrics, dict):
        return 0
    return sum(1 for m in metrics.values() if isinstance(m, dict) and m.get("value") is not None)


def merge_profiles(batch_docs: list[Any]) -> tuple[dict, list[str]]:
    """company_profiles.batch-*.json のドキュメント群を企業キーで統合する。

    同じキーが複数回現れた場合、metrics の非null値が多い方をまるごと残す（フィールド単位では混ぜない）。
    戻り値: (統合済み company_profiles, 重複時の注記)。
    """
    merged: dict[str, Any] = {}
    notes: list[str] = []
    for doc in batch_docs:
        profiles = doc.get("company_profiles") if isinstance(doc, dict) else None
        if not isinstance(profiles, dict):
            continue
        for key, profile in profiles.items():
            if key not in merged:
                merged[key] = profile
                continue
            if _count_metric_values(profile) > _count_metric_values(merged[key]):
                merged[key] = profile
            notes.append(f"企業プロファイルの重複: {key}（metrics の充足数が多い方を採用した）")
    return merged, notes


def _build_stub_profile(name: Any) -> dict:
    """企業研究が届かなかった企業向けのスタブプロファイルを組み立てる。9指標すべてを null で埋める。"""
    metrics = {
        axis: {
            "value": None,
            "unit": unit,
            "source_url": None,
            "grade": None,
            "as_of": None,
            "note": "収集担当が応答しなかった",
        }
        for axis, unit in _METRIC_UNITS.items()
    }
    return {
        "name": name,
        "aliases": [],
        "official_url": None,
        "careers_url": None,
        "hq_location": None,
        "industry": None,
        "business_summary": None,
        "basics": {},
        "metrics": metrics,
        "negative_checks": {
            "labor_law_violation_list": {
                "checked": False,
                "hit": None,
                "source_url": None,
                "as_of": None,
                "note": "未確認",
            }
        },
        "recent_news": [],
        "open_questions": ["企業情報を収集できなかった"],
    }


def assign_company_keys(
    results: list[dict], profiles: dict, stub_missing: bool
) -> tuple[list[str], list[str]]:
    """results[].company_key を設定し、company_profiles に無い企業を検査する。

    company_name から company_key を作れない（空になる）結果は ERROR。company_profiles に無い企業は、
    stub_missing が偽なら ERROR（該当企業を列挙する1件にまとめる）、真なら _build_stub_profile で
    profiles を直接埋め、ドキュメントの open_questions に足す文言を返す。
    """
    errors: list[str] = []
    open_questions: list[str] = []
    missing: list[str] = []
    for i, item in enumerate(results):
        name = item.get("company_name")
        key = normalize_company_key(name)
        if not key:
            errors.append(
                f"[ERROR] results[{i}].company_key: company_name「{name}」から company_key を作れない"
            )
            continue
        item["company_key"] = key
        if key in profiles:
            continue
        if stub_missing:
            if key not in profiles:
                profiles[key] = _build_stub_profile(name)
                open_questions.append(f"企業情報の未収集: {name}")
        elif key not in missing:
            missing.append(key)
    if missing:
        errors.append(
            "[ERROR] results[].company_key: company_profiles に企業情報が無い企業がある: " + ", ".join(missing)
        )
    return errors, open_questions


def _group_companies(results: list[dict], exclude_keys: set[str]) -> list[dict]:
    """results を企業キーごとにまとめる。代表名・別表記（alias）・URL一覧を返す。"""
    by_key: dict[str, dict] = {}
    order: list[str] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        name = item.get("company_name")
        key = normalize_company_key(name)
        if not key or key in exclude_keys:
            continue
        if key not in by_key:
            by_key[key] = {"company_key": key, "name": name, "aliases": [], "urls": []}
            order.append(key)
        entry = by_key[key]
        if name != entry["name"] and name not in entry["aliases"]:
            entry["aliases"].append(name)
        url = item.get("url")
        if isinstance(url, str) and url not in entry["urls"]:
            entry["urls"].append(url)
    return [by_key[key] for key in order]


def list_companies(search_dir: str, profile: Any = None) -> MergeResult:
    """phase A: partial ファイル群から、統合も書き込みもせずに企業の一覧だけを組み立てる。"""
    warnings: list[str] = []
    partials, errors = load_partials(search_dir)
    if errors:
        return _make_result(errors, warnings)

    errors = check_consistency(partials)
    if errors:
        return _make_result(errors, warnings)

    if profile is not None:
        exclude_keys = current_employer_keys(profile)
    else:
        exclude_keys = set()
        warnings.append("[WARN] (root): 現勤務先の除外は未実施")

    items: list[dict] = []
    for _, doc in partials:
        items.extend(item for item in (doc.get("results") or []) if isinstance(item, dict))

    excluded_count = sum(
        1 for item in items if normalize_company_key(item.get("company_name")) in exclude_keys
    )
    companies = _group_companies(items, exclude_keys)
    return _make_result([], warnings, excluded_count, companies)


def merge(
    search_dir: str,
    profile: Any = None,
    lanes: list[str] | None = None,
    stub_missing: bool = False,
) -> MergeResult:
    """phase B: partial・batch ファイル群を統合し、job_search_results.json を書き出す。

    ERROR が1件でもあれば何も書き込まずに返す。成功時は既定で partial・batch ファイルを削除する。
    """
    warnings: list[str] = []

    partials, errors = load_partials(search_dir)
    if errors:
        return _make_result(errors, warnings)

    partials_by_name = dict(partials)
    primary_doc = partials_by_name[_PRIMARY_PARTIAL_NAME]
    other_docs = [doc for name, doc in partials if name != _PRIMARY_PARTIAL_NAME]
    ordered_docs = [primary_doc] + other_docs

    errors = check_consistency(partials)
    if errors:
        return _make_result(errors, warnings)

    for doc in ordered_docs:
        warnings.extend(strip_judgement(doc))

    derivations: list[dict] = []
    seen_lanes: set[Any] = set()
    for doc in ordered_docs:
        search_sets = doc.get("search_sets")
        entries = search_sets.get("derivations") if isinstance(search_sets, dict) else None
        for entry in entries or []:
            lane = entry.get("lane") if isinstance(entry, dict) else None
            if lane in seen_lanes:
                errors.append(f"[ERROR] search_sets.derivations: レーン「{lane}」が複数の partial に重複している")
                continue
            seen_lanes.add(lane)
            derivations.append(entry)
    if errors:
        return _make_result(errors, warnings)

    if profile is not None:
        exclude_keys = current_employer_keys(profile)
    else:
        exclude_keys = set()
        warnings.append("[WARN] (root): 現勤務先の除外は未実施")

    results, merge_notes, excluded_count = merge_results(ordered_docs, exclude_keys)
    dup_notes = near_dup_notes(results)

    batch_paths = sorted(glob.glob(os.path.join(search_dir, _BATCH_GLOB)))
    batch_docs: list[Any] = []
    for path in batch_paths:
        name = os.path.basename(path)
        try:
            batch_docs.append(load_json(path))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[ERROR] {name}: JSON として読み込めない（{exc}）")
    if errors:
        return _make_result(errors, warnings, excluded_count)

    profiles, profile_notes = merge_profiles(batch_docs)
    warnings.extend(f"[WARN] company_profiles: {note}" for note in profile_notes)

    assign_errors, stub_open_questions = assign_company_keys(results, profiles, stub_missing)
    errors.extend(assign_errors)

    missing_lanes: list[str] = []
    lane_notes: list[str] = []
    for lane in lanes or []:
        if lane not in seen_lanes:
            missing_lanes.append(lane)
            lane_notes.append(f"レーン {lane} は検索担当が応答せず未実施")

    if errors:
        return _make_result(errors, warnings, excluded_count, missing_lanes=missing_lanes)

    open_questions = list(primary_doc.get("open_questions") or [])
    for doc in other_docs:
        open_questions.extend(doc.get("open_questions") or [])
    open_questions.extend(stub_open_questions)
    seen_oq: set[str] = set()
    deduped_open_questions: list[str] = []
    for question in open_questions:
        if question not in seen_oq:
            seen_oq.add(question)
            deduped_open_questions.append(question)

    search_log: list[Any] = list(primary_doc.get("search_log") or [])
    for doc in other_docs:
        search_log.extend(doc.get("search_log") or [])

    coverage_lines: list[str] = []
    for doc in ordered_docs:
        note = doc.get("coverage_notes")
        if isinstance(note, str) and note.strip():
            coverage_lines.append(note)
    coverage_lines.extend(merge_notes)
    coverage_lines.extend(dup_notes)
    coverage_lines.extend(profile_notes)
    coverage_lines.extend(lane_notes)

    merged_doc: dict[str, Any] = {
        "schema_version": _V23_SCHEMA_VERSION,
        "search_id": primary_doc.get("search_id"),
        "mode": primary_doc.get("mode"),
        "executed_at": primary_doc.get("executed_at"),
        "conditions": primary_doc.get("conditions"),
    }
    if "baseline" in primary_doc:
        merged_doc["baseline"] = primary_doc["baseline"]
    if "improvement_axes" in primary_doc:
        merged_doc["improvement_axes"] = primary_doc["improvement_axes"]
    merged_doc["search_sets"] = {
        "primary": (primary_doc.get("search_sets") or {}).get("primary"),
        "derivations": derivations,
        "exploration": None,
    }
    merged_doc["results"] = results
    merged_doc["search_log"] = search_log
    merged_doc["coverage_notes"] = "\n".join(coverage_lines)
    merged_doc["open_questions"] = deduped_open_questions
    merged_doc["company_profiles"] = profiles

    output_path = os.path.join(search_dir, "job_search_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_doc, f, ensure_ascii=False, indent=2)
        f.write("\n")

    companies = _group_companies(results, exclude_keys)
    return _make_result([], warnings, excluded_count, companies, missing_lanes, output_path)


def cleanup(search_dir: str) -> MergeResult:
    """統合後の partial・batch ファイルを削除する。job_search_results.json が無ければ ERROR にして何も消さない。"""
    result = MergeResult()
    output_path = os.path.join(search_dir, "job_search_results.json")
    if not os.path.isfile(output_path):
        result.add_error(output_path, "job_search_results.json が無い。統合と検証を済ませてから削除する")
        return result
    paths = sorted(glob.glob(os.path.join(search_dir, _PARTIAL_GLOB))) + sorted(
        glob.glob(os.path.join(search_dir, _BATCH_GLOB))
    )
    for path in paths:
        try:
            os.remove(path)
        except OSError as exc:
            result.add_warning(path, f"削除できなかった（{exc}）")
    result.output_path = output_path
    return result


def format_report(result: MergeResult) -> str:
    status = "OK" if result.ok else "FAIL"
    lines = [f"統合結果: {status}（ERROR {len(result.errors)}件 / WARN {len(result.warnings)}件）"]
    lines.extend(result.errors)
    lines.extend(result.warnings)
    lines.append(f"現勤務先を理由に除外した件数: {result.excluded_count}")
    lines.append(f"企業件数: {len(result.companies)}")
    if result.missing_lanes:
        lines.append(f"未実施のレーン: {', '.join(result.missing_lanes)}")
    if result.output_path:
        lines.append(f"出力先: {result.output_path}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="job-change-job-search 求人検索結果 統合ツール")
    parser.add_argument("search_dir", help="partial・batch ファイル群を置いた job-search/{search_id}/ ディレクトリ")
    parser.add_argument(
        "--list-companies",
        action="store_true",
        help="統合せず、現勤務先を除外した企業一覧だけを表示する（phase A）",
    )
    parser.add_argument("--profile", help="現勤務先の除外に用いる profile.json パス（ローカルでのみ読み取る）")
    parser.add_argument("--lanes", help="実施を期待する派生レーン id のカンマ区切り一覧")
    parser.add_argument(
        "--stub-missing",
        action="store_true",
        help="company_profiles に無い企業へスタブのプロファイルを補って続行する",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="統合と検証が済んだ後に partial・batch ファイルを削除する（統合はしない）",
    )
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    profile: Any = None
    if args.profile:
        try:
            profile = load_json(args.profile)
        except (OSError, json.JSONDecodeError) as exc:
            result = MergeResult()
            result.add_error(args.profile, f"profile.json を読み込めない（{exc}）")
            _print_result(result, args.json)
            return 1

    if args.cleanup:
        result = cleanup(args.search_dir)
    elif args.list_companies:
        result = list_companies(args.search_dir, profile)
    else:
        lanes = [s.strip() for s in args.lanes.split(",") if s.strip()] if args.lanes else None
        result = merge(
            args.search_dir,
            profile=profile,
            lanes=lanes,
            stub_missing=args.stub_missing,
        )

    _print_result(result, args.json)
    return 0 if result.ok else 1


def _print_result(result: MergeResult, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    sys.exit(main())
