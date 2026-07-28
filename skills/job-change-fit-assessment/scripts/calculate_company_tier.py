"""job-change-fit-assessment: 企業品質 Tier の総合格付けの決定的（非LLM）算出ツール。

標準ライブラリのみで、企業研究（company_research.json）の軸ごとの評価と、利用者
プロファイル（profile.json）の重視段階から、総合の格付け（level）と暫定フラグ
（provisional）を決定的に算出し、fit_assessment.json の company_tier オブジェクトを
組み立てる。格付け規則の原本は job-change-company-research の
references/tier-rubric.md、出力形式の原本は references/fit-format.md である。

総合の格付けは利用者が重んじる軸に依存するため、profile.json を読める本スキルが担う。

CLI:
    python calculate_company_tier.py --research PATH --profile PATH [--out PATH] [--json]

終了コード: 0 = 正常、2 = 入力の矛盾（候補軸に無い軸キー・未知の重視段階・入力の読み込み失敗）。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

# --- 語彙（原本は job-change-company-research/references/tier-rubric.md） ---
CANDIDATE_AXES = (
    "compensation_level",
    "financial_soundness",
    "retention",
    "work_style",
    "employment_stability",
    "growth",
    "tech_advancement",
)
AXIS_LABELS = {
    "compensation_level": "処遇水準",
    "financial_soundness": "財務健全性・規模",
    "retention": "定着",
    "work_style": "働き方",
    "employment_stability": "雇用の安定性",
    "growth": "成長性",
    "tech_advancement": "技術先進性",
}
EMPHASIS_VALUES = ("top", "high", "reference")
RATING_VALUES = ("high", "medium", "low", "unknown")
RUBRIC_VERSION = 2

# 格付けの集計に入れる重視段階。reference は集計に入れず、報告のために併記する。
_AGGREGATED_EMPHASES = ("top", "high")


class CalcError(Exception):
    """入力の矛盾を表す。main で捕捉して終了コード2を返す。"""


def declared_axes(profile: Any) -> list[dict[str, str]]:
    """profile.json の company_quality_axes を、申告順の {axis, emphasis} で返す。

    申告が無い（フィールドの欠落・空配列）場合は空リストを返す。
    """
    if not isinstance(profile, dict):
        raise CalcError("profile.json のルートがオブジェクトでない")
    declared = profile.get("company_quality_axes")
    if declared is None:
        return []
    if not isinstance(declared, list):
        raise CalcError("company_quality_axes は配列でなければならない")

    axes: list[dict[str, str]] = []
    seen: set[str] = set()
    for i, entry in enumerate(declared):
        path = f"company_quality_axes[{i}]"
        if not isinstance(entry, dict):
            raise CalcError(f"{path} はオブジェクトでなければならない")
        axis = entry.get("axis")
        if axis not in CANDIDATE_AXES:
            raise CalcError(f"{path}.axis が候補軸のいずれでもない: {axis!r}")
        if axis in seen:
            raise CalcError(f"company_quality_axes で軸「{axis}」が重複している")
        emphasis = entry.get("emphasis")
        if emphasis not in EMPHASIS_VALUES:
            raise CalcError(f"{path}.emphasis が {'/'.join(EMPHASIS_VALUES)} のいずれでもない: {emphasis!r}")
        seen.add(axis)
        axes.append({"axis": axis, "emphasis": emphasis})
    return axes


def axis_ratings(research: Any) -> dict[str, str]:
    """company_research.json の tier.axes から軸ごとの rating を取り出す。

    tier が無い、または評価されていない軸は結果に含めない（呼び手が unknown として扱う）。
    """
    if not isinstance(research, dict):
        raise CalcError("company_research.json のルートがオブジェクトでない")
    tier = research.get("tier")
    if not isinstance(tier, dict):
        return {}
    axes = tier.get("axes")
    if not isinstance(axes, dict):
        return {}

    ratings: dict[str, str] = {}
    for axis, body in axes.items():
        if axis not in CANDIDATE_AXES:
            continue
        rating = body.get("rating") if isinstance(body, dict) else None
        ratings[axis] = rating if rating in RATING_VALUES else "unknown"
    return ratings


def _emphasized(axes: list[dict[str, str]]) -> list[dict[str, str]]:
    return [a for a in axes if a["emphasis"] in _AGGREGATED_EMPHASES]


def decide_level(axes: list[dict[str, str]]) -> str | None:
    """C・S・A・B の順に当てはめて総合の格付けを決める。

    対象軸は、段階が top または high の軸のうち rating が unknown でないものである。
    重視する軸（top・high）の申告が無い場合と、対象軸が1件も無い場合は、
    重みも評価も仮定せず None を返す。
    """
    emphasized = _emphasized(axes)
    if not emphasized:
        return None

    top = [a for a in emphasized if a["emphasis"] == "top"]
    rated = [a for a in emphasized if a["rating"] != "unknown"]
    if not rated:
        return None
    lows = [a for a in rated if a["rating"] == "low"]
    highs = [a for a in rated if a["rating"] == "high"]

    if any(a["rating"] == "low" for a in top) or len(lows) >= 2:
        return "C"
    if top and all(a["rating"] == "high" for a in top) and not lows:
        return "S"
    if len(highs) >= 2 and not lows:
        return "A"
    return "B"


def decide_provisional(axes: list[dict[str, str]]) -> bool:
    """対象にできたはずの軸の unknown が2以上か、top の軸に unknown があれば true を返す。

    対象軸が1件も無い場合も、証拠が集まり次第の見直しを前提とするため true を返す。
    """
    emphasized = _emphasized(axes)
    if not emphasized:
        return False
    unknown = [a for a in emphasized if a["rating"] == "unknown"]
    if len(unknown) == len(emphasized):
        return True
    return len(unknown) >= 2 or any(a["emphasis"] == "top" for a in unknown)


def _labels(axes: list[dict[str, str]]) -> str:
    return "・".join(AXIS_LABELS[a["axis"]] for a in axes)


def build_rationale(axes: list[dict[str, str]], level: str | None, provisional: bool) -> str:
    """総合の格付けに至った根拠を、同じ入力から同じ文字列になるよう組み立てる。"""
    if level is None:
        if _emphasized(axes):
            return (
                "重視する軸のうち評価できた軸が無い（すべて unknown）ため、"
                "総合の格付けは算出しない。企業研究で軸の評価を得てから見直す。"
            )
        return (
            "重視する軸（top・high）の申告が無いため、総合の格付けは算出しない。"
            "重みを仮定した格付けはしない。"
        )

    emphasized = _emphasized(axes)
    top = [a for a in emphasized if a["emphasis"] == "top"]
    rated = [a for a in emphasized if a["rating"] != "unknown"]
    lows = [a for a in rated if a["rating"] == "low"]
    highs = [a for a in rated if a["rating"] == "high"]

    if level == "C":
        top_lows = [a for a in top if a["rating"] == "low"]
        if top_lows:
            head = f"最重視の軸「{_labels(top_lows)}」の評価が low であるため C とする。"
        else:
            head = f"重視する軸のうち「{_labels(lows)}」の{len(lows)}軸が low であるため C とする。"
    elif level == "S":
        head = (
            f"最重視の軸「{_labels(top)}」が {'いずれも ' if len(top) > 1 else ''}high であり、"
            "重視する軸に low が無いため S とする。"
        )
    elif level == "A":
        head = (
            f"重視する軸のうち「{_labels(highs)}」の{len(highs)}軸が high であり、"
            "low が無いため A とする。"
        )
    else:
        head = (
            f"重視する軸の評価は high が{len(highs)}軸・low が{len(lows)}軸であり、"
            "C・S・A のいずれの条件にも当たらないため B とする。"
        )

    sentences = [head]
    unknown = [a for a in emphasized if a["rating"] == "unknown"]
    if provisional and unknown:
        sentences.append(
            f"重視する軸のうち「{_labels(unknown)}」を評価できていないため、暫定の格付けとする。"
        )
    references = [a for a in axes if a["emphasis"] == "reference"]
    if references:
        sentences.append(f"参考として申告された「{_labels(references)}」は格付けに反映していない。")
    return "".join(sentences)


def build_company_tier(research: Any, profile: Any) -> dict[str, Any]:
    """fit_assessment.json の company_tier オブジェクトを組み立てる。"""
    axes = declared_axes(profile)
    ratings = axis_ratings(research)
    for entry in axes:
        entry["rating"] = ratings.get(entry["axis"], "unknown")

    level = decide_level(axes)
    provisional = decide_provisional(axes)

    tier = research.get("tier") if isinstance(research, dict) else None
    tier = tier if isinstance(tier, dict) else {}
    rubric_version = tier.get("rubric_version")
    assessed_date = tier.get("assessed_date")

    return {
        "level": level,
        "provisional": provisional,
        "rubric_version": (
            rubric_version
            if isinstance(rubric_version, int) and not isinstance(rubric_version, bool)
            else RUBRIC_VERSION
        ),
        "assessed_date": assessed_date if isinstance(assessed_date, str) and assessed_date.strip() else None,
        "axes": [
            {"axis": a["axis"], "emphasis": a["emphasis"], "rating": a["rating"]} for a in axes
        ],
        "rationale": build_rationale(axes, level, provisional),
    }


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="job-change-fit-assessment 企業品質 Tier の総合格付け算出ツール"
    )
    parser.add_argument("--research", required=True, help="company_research.json のパス")
    parser.add_argument("--profile", required=True, help="profile.json のパス")
    parser.add_argument("--out", default=None, help="出力先パス（親ディレクトリは自動作成）")
    parser.add_argument("--json", action="store_true", help="結果をJSONで標準出力へ書き出す")
    args = parser.parse_args(argv)

    try:
        research = _load_json(args.research)
        profile = _load_json(args.profile)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] 入力を読み込めない（{exc}）", file=sys.stderr)
        return 2

    try:
        company_tier = build_company_tier(research, profile)
    except CalcError as exc:
        print(f"[ERROR] 入力の矛盾: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(company_tier, ensure_ascii=False, indent=2)

    if args.out:
        parent = os.path.dirname(os.path.abspath(args.out))
        os.makedirs(parent, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(payload + "\n")

    if args.json or not args.out:
        print(payload)

    return 0


if __name__ == "__main__":
    sys.exit(main())
