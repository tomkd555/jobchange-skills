"""job-change-decision: 意思決定記録（decision.json）の検証と派生値の計算を行うツール。

標準ライブラリのみで、比較表の数値計算（0〜1 への換算、スイング・ROC・均等の重み、候補ごとの
スコア、順位、重みの感度検査）を手計算せずに行い、記録が仕様どおりかを検査する。仕様の原本は
references/decision-format.md である。項目の型と向きは、field-catalog.md を
field_catalog.py 経由で参照する。

CLI:
    python validate_decision.py <decision.json> [--wishes <wishes.json>] [--json]
    python validate_decision.py <decision.json> --fill [--wishes <wishes.json>] [--json]

--fill は派生項目を入力から再計算して同じファイルへ書き戻し、そのあと検証する。
終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from field_catalog import is_date, load_catalog  # noqa: E402
from validate_company_index import SLUG_PATTERN  # noqa: E402

_KNOWN_SCHEMA_VERSIONS = ("1.0",)
_METHODS = ("swing", "roc", "equal")
_RANK_METHODS = ("swing", "roc", "equal", "want_count")
_FOLLOW_UP_AT = ["3m", "1y"]
_DELTA = 0.2
_DECIMALS = 4
_TOLERANCE = 0.0005
_WEIGHT_SUM_TOLERANCE = 0.001
_ID_PATTERN = re.compile(r"^([0-9]{8})-([0-9a-z][0-9a-z-]*)$")
_POSTING_ID_PATTERN = re.compile(r"^(.+)-([0-9]{8})-([0-9]{2})$")
_CRITERION_ID_PATTERN = re.compile(r"^k[0-9]{2}$")


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


# ---------------------------------------------------------------- 計算（純関数）

def scale_values(values: dict, direction: str) -> dict:
    """数値の生値を 0〜1 に換算する。向きを反映し、最悪を 0、最良を 1 とする。null は null のまま。"""
    known = [v for v in values.values() if v is not None]
    if not known:
        return {k: None for k in values}
    lo, hi = min(known), max(known)
    out: dict = {}
    for k, v in values.items():
        if v is None:
            out[k] = None
        elif hi == lo:
            out[k] = 1.0
        elif direction == "lower":
            out[k] = (hi - v) / (hi - lo)
        else:
            out[k] = (v - lo) / (hi - lo)
    return out


def scale_ratings(ratings: dict) -> dict:
    """1〜5 の評価を (評価 - 1) / 4 に換算する。"""
    return {k: (None if r is None else (r - 1) / 4) for k, r in ratings.items()}


def swing_weights(points: dict) -> dict:
    """スイングの点数を合計 1 に正規化する。"""
    total = sum(points.values())
    return {k: p / total for k, p in points.items()}


def roc_weights(order: list) -> dict:
    """順位から ROC 重みを求める。i 番目（全 n 件）は (1/n) × Σ(k=i..n) 1/k。"""
    n = len(order)
    return {cid: sum(1 / k for k in range(i, n + 1)) / n for i, cid in enumerate(order, start=1)}


def equal_weights(ids: list) -> dict:
    return {cid: 1 / len(ids) for cid in ids}


def weighted_scores(criteria: list, weights: dict, candidate_ids: list) -> dict:
    """候補ごとに重み × 換算値を合計する。換算値が null の基準は除き、残りの重みを 1 に再正規化する。"""
    out: dict = {}
    for pid in candidate_ids:
        total = wsum = 0.0
        known = False
        for c in criteria:
            s = (c.get("scaled") or {}).get(pid)
            if s is None:
                continue
            known = True
            total += weights[c["id"]] * s
            wsum += weights[c["id"]]
        out[pid] = None if not known else (total / wsum if wsum else 0.0)
    return out


def rank(scores: dict, candidate_ids: list) -> list:
    """スコアの高い順に並べる。null は最後、同点は candidates の順を保つ（sorted は安定）。"""
    def key(pid):
        s = scores.get(pid)
        return (1, 0.0) if s is None else (0, -round(s, 9))
    return sorted(candidate_ids, key=key)


def want_counts(criteria: list, candidate_ids: list, wishes: dict | None) -> dict | None:
    """want の条件に由来する基準で、候補の換算値が最良（1.0）である数。wishes が無ければ判定できないので None。"""
    if wishes is None:
        return None
    levels = {c.get("id"): c.get("level") for c in wishes.get("conditions", []) if isinstance(c, dict)}
    out = {pid: 0 for pid in candidate_ids}
    for c in criteria:
        scaled = c.get("scaled") or {}
        if c.get("condition_id") is None or levels.get(c["condition_id"]) != "want":
            continue
        for pid in candidate_ids:
            s = scaled.get(pid)
            out[pid] += 1 if s is not None and s >= 1.0 else 0
    return out


def sensitivity(decision: dict, delta=_DELTA) -> dict:
    """基準ごとにスイング重みを (1 ± delta) 倍し、残りを比例配分して首位が変わるかを調べる。"""
    ids = [c["posting_id"] for c in decision["candidates"]]
    base = decision["weights"]["swing"]
    criteria = decision["criteria"]
    first = rank(weighted_scores(criteria, base, ids), ids)[0]
    details = []
    pct = round(delta * 100)
    for c in criteria:
        for sign, label in ((-1, f"-{pct}%"), (1, f"+{pct}%")):
            # 重みは 1 を超えない。超えると他の重みが負になるため、1 で止める。
            new = min(1.0, base[c["id"]] * (1 + sign * delta))
            rest = 1 - base[c["id"]]
            w = {k: (new if k == c["id"] else (v * (1 - new) / rest if rest else v)) for k, v in base.items()}
            top = rank(weighted_scores(criteria, w, ids), ids)[0]
            details.append({"criterion_id": c["id"], "change": label, "top": top})
    return {"delta": delta, "top_changes": any(d["top"] != first for d in details), "details": details}


def _round_map(m: dict) -> dict:
    return {k: (None if v is None else round(v, _DECIMALS)) for k, v in m.items()}


def fill(decision: dict, wishes: dict | None) -> dict:
    """入力から派生項目（scaled・weights・scores・rankings・sensitivity）を再計算して返す。入力は変えない。"""
    d = copy.deepcopy(decision)
    ids = [c["posting_id"] for c in d["candidates"]]
    for c in d["criteria"]:
        c["scaled"] = scale_ratings(c["ratings"]) if c.get("ratings") is not None else scale_values(c["values"], c["direction"])
    weights = {
        "swing": swing_weights(d["swing_points"]),
        "roc": roc_weights(d["swing_order"]),
        "equal": equal_weights([c["id"] for c in d["criteria"]]),
    }
    scores = {m: weighted_scores(d["criteria"], weights[m], ids) for m in _METHODS}
    # wishes が無いときは want_count を計算できないので、記録済みの値を残す（無ければ 0）。
    existing = (decision.get("scores") or {}).get("want_count") if isinstance(decision.get("scores"), dict) else None
    counted = want_counts(d["criteria"], ids, wishes)
    scores["want_count"] = counted if counted is not None else (existing if isinstance(existing, dict) else {pid: 0 for pid in ids})
    sens = sensitivity({"candidates": d["candidates"], "criteria": d["criteria"], "weights": weights})
    d["weights"] = {m: _round_map(w) for m, w in weights.items()}
    d["scores"] = {m: (s if m == "want_count" else _round_map(s)) for m, s in scores.items()}
    d["rankings"] = {m: rank(scores[m], ids) for m in _RANK_METHODS}
    d["sensitivity"] = sens
    for c in d["criteria"]:
        c["scaled"] = _round_map(c["scaled"])
    return d


# ---------------------------------------------------------------- 検証

def _is_num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_str(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ""


def _check_candidates(d: dict, result: ValidationResult) -> list[str]:
    cands = d.get("candidates")
    if not isinstance(cands, list):
        result.add_error("candidates", "candidates は配列で書く")
        return []
    if not 2 <= len(cands) <= 5:
        result.add_error("candidates", f"候補は 2〜5 件で書く（{len(cands)} 件）")
    ids: list[str] = []
    for i, c in enumerate(cands):
        p = f"candidates[{i}]"
        if not isinstance(c, dict):
            result.add_error(p, "候補はオブジェクトで書く")
            continue
        pid = c.get("posting_id")
        m = _POSTING_ID_PATTERN.match(pid) if isinstance(pid, str) else None
        valid = False
        if m and SLUG_PATTERN.match(m.group(1)):
            try:
                datetime.strptime(m.group(2), "%Y%m%d")
                valid = True
            except ValueError:
                pass
        if not valid:
            result.add_error(f"{p}.posting_id", "posting_id は「企業スラッグ-YYYYMMDD-NN」で書く")
        elif m.group(1) != c.get("company_slug"):
            result.add_error(f"{p}.company_slug", "company_slug が posting_id のスラッグ部分と違う")
        if isinstance(pid, str):
            if pid in ids:
                result.add_error(f"{p}.posting_id", f"posting_id「{pid}」が重複している")
            ids.append(pid)
        if not isinstance(c.get("label"), str) or not 1 <= len(c["label"]) <= 2:
            result.add_error(f"{p}.label", "label は 1〜2 文字の文字列で書く")
    return ids


def _check_criteria(d: dict, ids: list[str], catalog, wishes: dict | None, result: ValidationResult) -> list[str]:
    crits = d.get("criteria")
    if not isinstance(crits, list) or not crits:
        result.add_error("criteria", "criteria は 1 件以上の配列で書く")
        return []
    cond_ids = None
    if wishes is not None:
        cond_ids = {c.get("id") for c in wishes.get("conditions", []) if isinstance(c, dict)}
    out: list[str] = []
    for i, c in enumerate(crits):
        p = f"criteria[{i}]"
        if not isinstance(c, dict):
            result.add_error(p, "基準はオブジェクトで書く")
            continue
        cid = c.get("id")
        if not isinstance(cid, str) or not _CRITERION_ID_PATTERN.match(cid):
            result.add_error(f"{p}.id", "id は k と 2 桁の数字で書く")
        elif cid in out:
            result.add_error(f"{p}.id", f"基準の id「{cid}」が重複している")
        if isinstance(cid, str):
            out.append(cid)
        fid = c.get("field_id")
        f = catalog.fields.get(fid) if isinstance(fid, str) else None
        if f is None:
            result.add_error(f"{p}.field_id", f"field_id「{fid}」が辞書にない")
        cond = c.get("condition_id")
        if cond is not None and not isinstance(cond, str):
            result.add_error(f"{p}.condition_id", "condition_id は文字列か null で書く")
        elif fid == "custom" and cond is None:
            result.add_error(f"{p}.condition_id", "custom の基準は condition_id が必須である")
        elif cond is not None and cond_ids is not None and cond not in cond_ids:
            result.add_error(f"{p}.condition_id", f"condition_id「{cond}」が wishes.json にない")
        direction = c.get("direction")
        if direction not in ("higher", "lower"):
            result.add_error(f"{p}.direction", "direction は higher か lower で書く")
        elif f is not None and f.direction in ("higher", "lower") and f.direction != direction:
            result.add_error(f"{p}.direction", f"direction が辞書の向き {f.direction} と違う")
        elif fid == "custom" and direction != "higher":
            result.add_error(f"{p}.direction", "custom の基準の direction は higher で書く")
        if f is None:
            continue
        numeric = f.type in ("integer", "number")
        key, other = ("values", "ratings") if numeric else ("ratings", "values")
        if c.get(other) is not None:
            result.add_error(f"{p}.{other}", f"この基準の {other} は null で書く")
        data = c.get(key)
        if not isinstance(data, dict):
            result.add_error(f"{p}.{key}", f"{key} は候補ごとのオブジェクトで書く")
            continue
        if set(data) != set(ids):
            result.add_error(f"{p}.{key}", f"{key} のキーが候補の posting_id と一致しない")
        for pid, v in data.items():
            if numeric:
                msg = f.check_value(v, catalog)
                if msg:
                    result.add_error(f"{p}.values.{pid}", msg)
            elif isinstance(v, bool) or not isinstance(v, int) or not 1 <= v <= 5:
                result.add_error(f"{p}.ratings.{pid}", "評価は 1〜5 の整数で書く")
    return out


def _check_swing(d: dict, crit_ids: list[str], result: ValidationResult) -> None:
    order, points = d.get("swing_order"), d.get("swing_points")
    if not isinstance(order, list) or sorted(map(str, order)) != sorted(crit_ids):
        result.add_error("swing_order", "swing_order は基準 id の並べ替えで書く")
        order = None
    if not isinstance(points, dict) or set(points) != set(crit_ids):
        result.add_error("swing_points", "swing_points のキーが基準 id と一致しない")
        return
    for k, v in points.items():
        if not _is_num(v) or not 0 <= v <= 100:
            result.add_error(f"swing_points.{k}", "点数は 0〜100 の数値で書く")
    if order and points.get(order[0]) != 100:
        result.add_error("swing_points", "swing_order の先頭の点数は 100 で書く")


def _check_follow_up(d: dict, result: ValidationResult) -> None:
    fu = d.get("follow_up")
    if not isinstance(fu, list) or len(fu) != 2 or [x.get("at") if isinstance(x, dict) else None for x in fu] != _FOLLOW_UP_AT:
        result.add_error("follow_up", "follow_up は at が 3m と 1y の 2 件で書く")
        return
    for i, x in enumerate(fu):
        if x.get("date") is not None and not is_date(x["date"]):
            result.add_error(f"follow_up[{i}].date", "date は YYYY-MM-DD か null で書く")
        s = x.get("satisfaction")
        if s is not None and (isinstance(s, bool) or not isinstance(s, int) or not 1 <= s <= 5):
            result.add_error(f"follow_up[{i}].satisfaction", "satisfaction は 1〜5 の整数か null で書く")
        if not isinstance(x.get("notes"), dict):
            result.add_error(f"follow_up[{i}].notes", "notes はオブジェクトで書く")


def _check_inputs(d: dict, catalog, wishes: dict | None, result: ValidationResult) -> bool:
    """利用者の入力部分を検査する。派生項目は見ない。入力に ERROR があれば False。"""
    before = len(result.errors)
    version = d.get("schema_version")
    if not isinstance(version, str):
        result.add_error("schema_version", "schema_version は文字列で書く")
    elif version not in _KNOWN_SCHEMA_VERSIONS:
        result.add_warning("schema_version", f"既知のバージョン（{'/'.join(_KNOWN_SCHEMA_VERSIONS)}）ではない（{version}）")
    date = d.get("date")
    if not is_date(date):
        result.add_error("date", "date は YYYY-MM-DD の実在する日付で書く")
    rid = d.get("id")
    m = _ID_PATTERN.match(rid) if isinstance(rid, str) else None
    if not m:
        result.add_error("id", "id は「YYYYMMDD-件名スラッグ」（小文字・数字・ハイフン）で書く")
    elif is_date(date) and m.group(1) != date.replace("-", ""):
        result.add_error("id", "id の日付部分が date と違う")
    if not _is_str(d.get("subject")):
        result.add_error("subject", "subject は空でない文字列で書く")
    ids = _check_candidates(d, result)
    crit_ids = _check_criteria(d, ids, catalog, wishes, result)
    _check_swing(d, crit_ids, result)
    if "chosen" not in d or (d["chosen"] is not None and d["chosen"] not in ids):
        result.add_error("chosen", "chosen は候補の posting_id か null で書く")
    for key in ("decisive_fields", "compromised_fields"):
        v = d.get(key)
        if not isinstance(v, list):
            result.add_error(key, f"{key} は基準 id の配列で書く")
        elif any(x not in crit_ids for x in v):
            result.add_error(key, f"{key} に基準 id でない要素がある")
    _check_follow_up(d, result)
    return len(result.errors) == before


def _diff(path: str, expected: Any, actual: Any, result: ValidationResult) -> None:
    """再計算した値と記録の値を比べる。数値は許容差 0.0005、それ以外は完全一致。"""
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(actual) != set(expected):
            result.add_error(path, "派生項目がない、またはキーが再計算の結果と違う（--fill で再計算する）")
            return
        for k in expected:
            _diff(f"{path}.{k}", expected[k], actual[k], result)
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            result.add_error(path, "派生項目がない、または配列が再計算の結果と違う（--fill で再計算する）")
            return
        for i, (e, a) in enumerate(zip(expected, actual)):
            _diff(f"{path}[{i}]", e, a, result)
    elif _is_num(expected):
        if not _is_num(actual) or abs(actual - expected) > _TOLERANCE:
            result.add_error(path, f"再計算した値 {round(expected, _DECIMALS)} と {actual!r} が違う")
    elif expected != actual:
        result.add_error(path, f"再計算した値 {expected!r} と {actual!r} が違う")


def validate(decision: dict, wishes: dict | None = None, catalog=None) -> ValidationResult:
    result = ValidationResult()
    if not isinstance(decision, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result
    catalog = catalog or load_catalog()
    if not _check_inputs(decision, catalog, wishes, result):
        return result

    expected = fill(decision, wishes)
    for i, (e, a) in enumerate(zip(expected["criteria"], decision["criteria"])):
        _diff(f"criteria[{i}].scaled", e["scaled"], a.get("scaled"), result)
    for key in ("weights", "sensitivity"):
        _diff(key, expected[key], decision.get(key), result)
    for key in ("scores", "rankings"):
        actual = decision.get(key)
        if not isinstance(actual, dict):
            result.add_error(key, "オブジェクトで書く（--fill で再計算する）")
            continue
        for m in _RANK_METHODS:
            if m == "want_count" and wishes is None:
                continue
            _diff(f"{key}.{m}", expected[key].get(m), actual.get(m), result)
    if wishes is None:
        result.add_warning("scores.want_count", "--wishes が無いため want_count と その順位は検査していない")
    weights = decision.get("weights")
    if isinstance(weights, dict):
        for m in _METHODS:
            w = weights.get(m)
            if isinstance(w, dict) and w and all(_is_num(v) for v in w.values()) and abs(sum(w.values()) - 1) > _WEIGHT_SUM_TOLERANCE:
                result.add_error(f"weights.{m}", "重みの合計が 1 でない")

    for i, c in enumerate(expected["criteria"]):
        if any(v is None for v in c["scaled"].values()):
            result.add_warning(f"criteria[{i}].scaled", "換算値が null の候補がある（不明な値は表に残る）")
    if decision["chosen"] is not None and not decision["decisive_fields"]:
        result.add_warning("decisive_fields", "chosen が決まっているのに decisive_fields が空である")
    if expected["sensitivity"]["top_changes"]:
        result.add_warning("sensitivity.top_changes", "重みを動かすと首位が変わる（首位は 1 つの重みに左右される）")
    return result


def format_report(result: ValidationResult) -> str:
    status = "PASS" if result.ok else "FAIL"
    lines = [f"検証結果: {status}（ERROR {len(result.errors)}件 / WARN {len(result.warnings)}件）"]
    lines.extend(result.errors)
    lines.extend(result.warnings)
    return "\n".join(lines)


def _load(path: str) -> Any:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="job-change-decision 意思決定記録の検証・計算ツール")
    parser.add_argument("decision_path", help="decision.json のファイルパス")
    parser.add_argument("--wishes", help="wishes.json のファイルパス")
    parser.add_argument("--fill", action="store_true", help="派生項目を再計算して書き戻す")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    def emit(result: ValidationResult) -> int:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2) if args.json else format_report(result))
        return 0 if result.ok else 1

    result = ValidationResult()
    try:
        decision = _load(args.decision_path)
        wishes = _load(args.wishes) if args.wishes else None
    except (OSError, ValueError) as exc:
        result.add_error(args.decision_path, f"JSON として読み込めない（{exc}）")
        return emit(result)
    if wishes is not None and not isinstance(wishes, dict):
        result.add_error(args.wishes, "wishes.json のルート要素はオブジェクトでなければならない")
        return emit(result)

    if args.fill:
        if not isinstance(decision, dict):
            result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
            return emit(result)
        if not _check_inputs(decision, load_catalog(), wishes, result):
            return emit(result)
        decision = fill(decision, wishes)
        with open(args.decision_path, "w", encoding="utf-8") as f:
            json.dump(decision, f, ensure_ascii=False, indent=2)
            f.write("\n")
    return emit(validate(decision, wishes))


if __name__ == "__main__":
    sys.exit(main())
