"""job-change-fit-assessment: 企業スコア（0〜100点）の決定的（非LLM）算出ツール。

標準ライブラリのみで、企業研究（company_research.json）の実測値（company_metrics）と、
利用者プロファイル（profile.json）の採点軸・重み・基準（company_score_axes）から、軸ごとの
点数・総合点・判定できた軸の重みの合計（coverage）・暫定フラグ（provisional）を決定的に
算出し、fit_assessment.json の company_score オブジェクトを組み立てる。定性軸の判定は
求人票と企業研究の事実を読んで決まるため機械では決められず、fit-assessor が判定した結果を
--qualitative-json で受け取る。採点規則の原本は job-change-company-research の
references/company-score-rubric.md、出力形式の原本は references/fit-format.md である。

定量軸の統計由来の既定基準の原本は、本ファイルの定数 DEFAULT_THRESHOLDS である。各項目は
官公庁ドメイン（mhlw.go.jp / stat.go.jp / e-stat.go.jp 等）の一次統計から裏取りして設定し、
本文書の外へ数値を重複して書かない。

総合点は利用者が選んだ軸と重みに依存するため、profile.json を読める本スキルが担う。

CLI:
    python calculate_company_score.py --research PATH --profile PATH \
        [--qualitative-json PATH] [--out PATH] [--json]

終了コード: 0 = 正常、2 = 入力の矛盾（採点軸の形式違反・判定条件に無い点数・入力の読み込み失敗）。
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Any

# --- 統計由来の既定基準（官公庁ドメインの一次統計から裏取りして設定する。値の原本は本定数） ---
#
# 軸キー → {p0, p100, unit, direction, survey, survey_year, source_url, coverage}。
# p0 は 0 点、p100 は 100 点に相当する水準であり、値が小さいほど良い軸では p0 > p100 になる。
# 既定を持たない軸は、利用者が profile の thresholds を書くまで採点しない（推測した基準で
# 点数を作らない）。
#
# derivation には p0・p100 をどの公表値からどう決めたかを、confidence には基準の確からしさ
# （high=度数分布から分位を補間、medium=階級分布の一部から読み取り、low=産業別の両端で代用）
# を書く。
#
# 処遇水準（compensation_level）は既定を持たない。企業単位の年収分布を持つ公的統計が無く、
# 個人単位の分布（パート・アルバイトを含む）を企業の平均年間給与へ当てると水準がずれるためで
# ある。この軸は利用者の現年収と希望年収を基準に聞く。
DEFAULT_THRESHOLDS: dict[str, dict[str, Any]] = {
    "annual_holidays": {
        "p0": 97,
        "p100": 127,
        "unit": "日",
        "direction": "higher_is_better",
        "survey": "就労条件総合調査",
        "survey_year": "令和7年（2025年）",
        "source_url": "https://www.mhlw.go.jp/toukei/itiran/roudou/jikan/syurou/25/dl/gaikyou.pdf",
        "coverage": "常用労働者30人以上の民営企業（16大産業）。1企業平均は112.4日",
        "derivation": "年間休日総数階級別の企業割合を累積し、階級内を線形補間して下位10%点と上位10%点を算出した",
        "confidence": "medium",
    },
    "paid_leave_rate": {
        "p0": 50.7,
        "p100": 75.2,
        "unit": "%",
        "direction": "higher_is_better",
        "survey": "就労条件総合調査",
        "survey_year": "令和7年（2025年）",
        "source_url": "https://www.mhlw.go.jp/toukei/itiran/roudou/jikan/syurou/25/dl/gaikyou.pdf",
        "coverage": "常用労働者30人以上の民営企業。労働者1人平均の取得率は66.9%",
        "derivation": "分位が非公表のため、産業別取得率の最低（宿泊業・飲食サービス業）と最高（電気・ガス・熱供給・水道業）で代用した",
        "confidence": "low",
    },
    "turnover_rate": {
        "p0": 19.0,
        "p100": 7.0,
        "unit": "%",
        "direction": "lower_is_better",
        "survey": "雇用動向調査",
        "survey_year": "令和6年（2024年）",
        "source_url": "https://www.mhlw.go.jp/toukei/itiran/roudou/koyou/doukou/25-2/dl/kekka_gaiyo-02.pdf",
        "coverage": "常用労働者5人以上の事業所。一般労働者の産業計は11.5%",
        "derivation": "分位が非公表のため、産業別離職率の最高（サービス業〈他に分類されないもの〉）と最低（複合サービス事業）で代用した",
        "confidence": "low",
    },
    "monthly_overtime": {
        "p0": 24.1,
        "p100": 6.7,
        "unit": "時間",
        "direction": "lower_is_better",
        "survey": "毎月勤労統計調査（全国調査）",
        "survey_year": "令和7年（2025年）分結果確報",
        "source_url": "https://www.mhlw.go.jp/toukei/itiran/roudou/monthly/r07/25cr/dl/pdf25cr.pdf",
        "coverage": "事業所規模5人以上の事業所。一般労働者（パートタイム労働者を除く）の調査産業計は13.2時間",
        "derivation": "分位が非公表のため、産業別の所定外労働時間の最大（運輸業・郵便業）と最小（医療・福祉）で代用した",
        "confidence": "low",
    },
    "male_childcare_leave_rate": {
        "p0": 0,
        "p100": 85,
        "unit": "%",
        "direction": "higher_is_better",
        "survey": "雇用均等基本調査（事業所調査）",
        "survey_year": "令和6年度（2024年度）",
        "source_url": "https://www.mhlw.go.jp/toukei/list/dl/71-r06/06.pdf",
        "coverage": "常用労働者5人以上の民営事業所。全体の取得率は40.5%",
        "derivation": "産業別の両端は小標本の影響が大きいため用いず、取得者なしを0点、同資料に併記された政府目標（令和12年85%）を100点とした",
        "confidence": "low",
    },
    "revenue_growth": {
        "p0": -7.1,
        "p100": 12.2,
        "unit": "%",
        "direction": "higher_is_better",
        "survey": "年次別法人企業統計調査",
        "survey_year": "令和6年度（2024年度）",
        "source_url": "https://www.mof.go.jp/pri/reference/ssc/results/r6.pdf",
        "coverage": "金融業・保険業を除く全産業の営利法人等。全産業の対前年度増加率は3.6%",
        "derivation": "分位が非公表のため、業種別の売上高増加率の最小（はん用機械）と最大（電気業）で代用した",
        "confidence": "low",
    },
    "operating_margin": {
        "p0": 0.6,
        "p100": 12.2,
        "unit": "%",
        "direction": "higher_is_better",
        "survey": "年次別法人企業統計調査",
        "survey_year": "令和6年度（2024年度）",
        "source_url": "https://www.mof.go.jp/pri/reference/ssc/results/r6.pdf",
        "coverage": "金融業・保険業を除く全産業の営利法人等。全産業は6.8%",
        "derivation": "分位が非公表のため、業種別の売上高営業利益率の最小（石油・石炭製品）と最大（不動産業）で代用した",
        "confidence": "low",
    },
    "equity_ratio": {
        "p0": 18.7,
        "p100": 52.4,
        "unit": "%",
        "direction": "higher_is_better",
        "survey": "法人企業統計調査（財務総合政策研究所による整理）",
        "survey_year": "平成30年度（2018年度）",
        "source_url": "https://www.mof.go.jp/pri/reference/ssc/japan/japan02_09.pdf",
        "coverage": "金融業・保険業を除く。同年度の全産業・全規模は42.0%（直近の四半期別調査では全産業44.5%）",
        "derivation": "業種と資本金階層のクロス表の最小（非製造業・資本金1,000万円未満）と最大（製造業・資本金10億円以上）で代用した",
        "confidence": "low",
    },
}

# 判定できた軸の重みの合計がこの値を下回るとき、総合点を暫定（provisional）として扱う。
COVERAGE_THRESHOLD = 70

# 軸の2種類（原本は company-score-rubric.md）。
_KINDS = ("quantitative", "qualitative")


class CalcError(Exception):
    """入力の矛盾を表す。main で捕捉して終了コード2を返す。"""


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _round_half_up(value: float) -> int:
    """0.5 を切り上げる四捨五入。Python の round は偶数丸めのため用いる。"""
    return int(math.floor(value + 0.5))


def declared_axes(profile: Any) -> list[dict[str, Any]]:
    """profile.json の company_score_axes を、申告順の軸定義の配列で返す。

    申告が無い（フィールドの欠落・空配列）場合は空リストを返す。
    """
    if not isinstance(profile, dict):
        raise CalcError("profile.json のルートがオブジェクトでない")
    declared = profile.get("company_score_axes")
    if declared is None:
        return []
    if not isinstance(declared, list):
        raise CalcError("company_score_axes は配列でなければならない")

    axes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, entry in enumerate(declared):
        path = f"company_score_axes[{i}]"
        if not isinstance(entry, dict):
            raise CalcError(f"{path} はオブジェクトでなければならない")
        axis = entry.get("axis")
        if not isinstance(axis, str) or not axis.strip():
            raise CalcError(f"{path}.axis は非空の文字列でなければならない")
        if axis in seen:
            raise CalcError(f"company_score_axes で軸「{axis}」が重複している")
        kind = entry.get("kind")
        if kind not in _KINDS:
            raise CalcError(f"{path}.kind が {'/'.join(_KINDS)} のいずれでもない: {kind!r}")
        weight = entry.get("weight")
        if not _is_int(weight) or not (1 <= weight <= 100):
            raise CalcError(f"{path}.weight は1以上100以下の整数でなければならない: {weight!r}")
        seen.add(axis)
        axes.append(entry)
    return axes


def score_from_value(value: float, zero: float, full: float) -> int:
    """実測値を 0〜100 点へ線形に写す。

    score = 100 × (value − zero) ÷ (full − zero) を 0〜100 でクリップし、四捨五入する。
    値が小さいほど良い軸（zero > full）でも同じ式のまま成り立つ。
    """
    if zero == full:
        raise CalcError(f"点数の基準は zero と full を異なる値にしなければならない: {zero}")
    raw = 100 * (value - zero) / (full - zero)
    return _round_half_up(min(100.0, max(0.0, raw)))


def _user_thresholds(entry: dict, axis: str) -> dict[str, float] | None:
    """profile の軸定義から基準の上書きを取り出す。書かれていなければ None を返す。"""
    thresholds = entry.get("thresholds")
    if not isinstance(thresholds, dict):
        return None
    zero = thresholds.get("zero")
    full = thresholds.get("full")
    if not _is_number(zero) or not _is_number(full):
        return None
    if zero == full:
        raise CalcError(f"軸「{axis}」の thresholds は zero と full を異なる値にしなければならない")
    return {"zero": zero, "full": full}


def _default_thresholds(axis: str) -> dict[str, float] | None:
    """DEFAULT_THRESHOLDS から基準を取り出す。既定を持たない軸は None を返す。"""
    default = DEFAULT_THRESHOLDS.get(axis)
    if not isinstance(default, dict):
        return None
    zero = default.get("p0")
    full = default.get("p100")
    if not _is_number(zero) or not _is_number(full) or zero == full:
        return None
    return {"zero": zero, "full": full}


def _text_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _quantitative_axis(entry: dict, axis: str, metric: dict) -> dict[str, Any]:
    """定量軸1件の内訳を組み立てる。実測値と基準がそろって初めて点数を付ける。"""
    raw_value = metric.get("value")
    value = raw_value if _is_number(raw_value) else None

    unit = _text_or_none(metric.get("unit"))
    default = DEFAULT_THRESHOLDS.get(axis)
    if unit is None and isinstance(default, dict):
        unit = _text_or_none(default.get("unit"))

    thresholds = _user_thresholds(entry, axis)
    threshold_source = "user" if thresholds is not None else None
    if thresholds is None:
        thresholds = _default_thresholds(axis)
        threshold_source = "statistic" if thresholds is not None else None

    result: dict[str, Any] = {
        "axis": axis,
        "kind": "quantitative",
        "weight": entry["weight"],
        "value": value,
        "unit": unit,
        "score": None,
        "threshold_source": threshold_source,
        "thresholds": thresholds,
        "grade": _text_or_none(metric.get("grade")),
        "source_url": _text_or_none(metric.get("source_url")),
    }

    if value is None and thresholds is None:
        result["reason"] = "実測値も点数の基準も無い"
    elif value is None:
        result["reason"] = "企業研究に実測値が無い"
    elif thresholds is None:
        result["reason"] = "点数の基準が利用者の申告にも統計の既定値にも無い"
    else:
        result["score"] = score_from_value(value, thresholds["zero"], thresholds["full"])
    return result


def _judgment_scores(entry: dict, axis: str) -> list[int]:
    """定性軸の判定条件から、取りうる点数の一覧を返す。"""
    judgment = entry.get("judgment")
    if not isinstance(judgment, list) or not judgment:
        raise CalcError(f"定性軸「{axis}」に判定条件（judgment）が無い。採点に入れる前に条件を決める")
    scores: list[int] = []
    for i, condition in enumerate(judgment):
        if not isinstance(condition, dict):
            raise CalcError(f"軸「{axis}」の judgment[{i}] はオブジェクトでなければならない")
        score = condition.get("score")
        if not _is_int(score) or not (0 <= score <= 100):
            raise CalcError(
                f"軸「{axis}」の judgment[{i}].score は0以上100以下の整数でなければならない: {score!r}"
            )
        scores.append(score)
    return scores


def _qualitative_axis(entry: dict, axis: str, judged: Any) -> dict[str, Any]:
    """定性軸1件の内訳を組み立てる。点数は fit-assessor の判定結果をそのまま使う。"""
    allowed = _judgment_scores(entry, axis)

    matched: Any = None
    evidence: str | None = None
    if isinstance(judged, dict):
        matched = judged.get("matched_score")
        evidence = _text_or_none(judged.get("evidence"))

    result: dict[str, Any] = {
        "axis": axis,
        "kind": "qualitative",
        "weight": entry["weight"],
        "value": None,
        "unit": None,
        "score": None,
        "threshold_source": None,
        "thresholds": None,
        "grade": None,
        "source_url": None,
        "evidence": evidence,
    }

    if matched is None:
        if isinstance(judged, dict):
            result["reason"] = "判定条件のいずれにも合致しない"
        else:
            result["reason"] = "判定結果が渡されていない"
        return result

    if not _is_int(matched) or matched not in allowed:
        raise CalcError(
            f"定性軸「{axis}」の matched_score が判定条件の score に無い: {matched!r}"
            f"（取りうる値: {'・'.join(str(s) for s in allowed)}）"
        )
    result["score"] = matched
    return result


def build_rationale(
    axes: list[dict[str, Any]], total: int | None, coverage: int, provisional: bool
) -> str:
    """総合点に至った根拠を、同じ入力から同じ文字列になるよう組み立てる。"""
    judged = [a for a in axes if a["score"] is not None]
    unjudged = [a for a in axes if a["score"] is None]

    sentences: list[str] = []
    if judged:
        detail = "、".join(f"{a['axis']}（重み{a['weight']}・{a['score']}点）" for a in judged)
        sentences.append(f"総合点 {total} 点は、判定できた軸（{detail}）の加重平均である。")
    elif axes:
        sentences.append("判定できた軸が1つも無いため、総合点は算出しない。")
    else:
        sentences.append("採点する軸の申告が無いため、総合点は算出しない。軸と重みを仮定して採点しない。")

    if unjudged:
        detail = "、".join(f"{a['axis']}（重み{a['weight']}・{a['reason']}）" for a in unjudged)
        sentences.append(f"判定できなかった軸は次のとおりである: {detail}。")

    sentences.append(f"判定できた軸の重みの合計は {coverage} である。")
    if provisional:
        sentences.append(
            f"重みの合計が {COVERAGE_THRESHOLD} を下回るため、暫定の点数として扱う。"
        )
    return "".join(sentences)


def build_company_score(
    research: Any, profile: Any, qualitative: Any = None
) -> dict[str, Any]:
    """fit_assessment.json の company_score オブジェクトを組み立てる。"""
    if not isinstance(research, dict):
        raise CalcError("company_research.json のルートがオブジェクトでない")
    metrics = research.get("company_metrics")
    metrics = metrics if isinstance(metrics, dict) else {}
    judgements = qualitative if isinstance(qualitative, dict) else {}

    axes: list[dict[str, Any]] = []
    for entry in declared_axes(profile):
        axis = entry["axis"]
        if entry["kind"] == "quantitative":
            metric = metrics.get(axis)
            axes.append(_quantitative_axis(entry, axis, metric if isinstance(metric, dict) else {}))
        else:
            axes.append(_qualitative_axis(entry, axis, judgements.get(axis)))

    judged = [a for a in axes if a["score"] is not None]
    coverage = sum(a["weight"] for a in judged)
    total = (
        _round_half_up(sum(a["score"] * a["weight"] for a in judged) / coverage)
        if judged
        else None
    )
    provisional = total is None or coverage < COVERAGE_THRESHOLD

    return {
        "total": total,
        "coverage": coverage,
        "provisional": provisional,
        "axes": axes,
        "rationale": build_rationale(axes, total, coverage, provisional),
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
        description="job-change-fit-assessment 企業スコア（0〜100点）の算出ツール"
    )
    parser.add_argument("--research", required=True, help="company_research.json のパス")
    parser.add_argument("--profile", required=True, help="profile.json のパス")
    parser.add_argument(
        "--qualitative-json",
        default=None,
        help="定性軸の判定結果 JSON のパス（軸キー→{matched_score, evidence}）",
    )
    parser.add_argument("--out", default=None, help="出力先パス（親ディレクトリは自動作成）")
    parser.add_argument("--json", action="store_true", help="結果をJSONで標準出力へ書き出す")
    args = parser.parse_args(argv)

    try:
        research = _load_json(args.research)
        profile = _load_json(args.profile)
        qualitative = _load_json(args.qualitative_json) if args.qualitative_json else None
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] 入力を読み込めない（{exc}）", file=sys.stderr)
        return 2

    try:
        company_score = build_company_score(research, profile, qualitative)
    except CalcError as exc:
        print(f"[ERROR] 入力の矛盾: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(company_score, ensure_ascii=False, indent=2)

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
