"""job-change-fit-assessment: 拘束時間・実質時給の決定的（非LLM）算定ツール。

標準ライブラリのみで、求人票・企業研究・利用者入力から得た数値をもとに、1日および
年間の拘束時間、年間労働時間、実質時給を決定的に算定し、time_analysis.json を生成する。
未指定の入力には官公庁の一次統計に基づく統計フォールバック定数（FALLBACKS）を適用し、
適用した項目を fallbacks_used と assumptions に記録する。仕様の原本は
references/time-analysis-format.md、フォールバック定数の原本は本ファイルの FALLBACKS /
STATUTORY_DEFAULTS である。

CLI:
    python calculate_time_analysis.py \
        [--scheduled-hours H] [--break-minutes M] [--overtime-h-month H] \
        [--annual-holidays D] [--paid-leave-rate R] [--paid-leave-granted D] \
        [--paid-leave-taken D] [--commute-oneway-min M] [--salary YEN] \
        [--sources-json PATH] [--out PATH] [--json]

終了コード: 0 = 正常、2 = 入力の矛盾（年間休日>365 等）。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any

# --- 統計フォールバック定数（官公庁の一次統計に基づく。値・調査名・調査年・出典URLをデータとして保持する） ---
#
# 各定数は一次資料（官公庁ドメイン: mhlw.go.jp / stat.go.jp）の最新公表値で裏取りした。
# value を CLI 引数未指定時に適用し、fallbacks_used と assumptions に記録する。
FALLBACKS: dict[str, dict[str, Any]] = {
    "annual_holidays": {
        "value": 116.6,
        "survey": "就労条件総合調査",
        "survey_year": 2025,
        "source_url": "https://www.mhlw.go.jp/toukei/itiran/roudou/jikan/syurou/25/dl/gaikyou.pdf",
        "note": "令和7年調査（令和6年＝2024年実績）。労働者1人平均の年間休日総数",
    },
    "paid_leave_rate": {
        "value": 0.669,
        "survey": "就労条件総合調査",
        "survey_year": 2025,
        "source_url": "https://www.mhlw.go.jp/toukei/itiran/roudou/jikan/syurou/25/dl/gaikyou.pdf",
        "note": "令和7年調査。年次有給休暇の取得率66.9%",
    },
    "paid_leave_granted": {
        "value": 18.1,
        "survey": "就労条件総合調査",
        "survey_year": 2025,
        "source_url": "https://www.mhlw.go.jp/toukei/itiran/roudou/jikan/syurou/25/dl/gaikyou.pdf",
        "note": "令和7年調査。労働者1人平均の年次有給休暇の付与日数",
    },
    "monthly_overtime_h": {
        "value": 13.5,
        "survey": "毎月勤労統計調査",
        "survey_year": 2024,
        "source_url": "https://www.mhlw.go.jp/toukei/itiran/roudou/monthly/r06/24cp/dl/pdf24cp.pdf",
        "note": "令和6年速報・事業所規模5人以上・一般労働者の月間所定外労働時間",
    },
    "commute_oneway_min": {
        "value": 33.5,
        "survey": "社会生活基本調査",
        "survey_year": 2021,
        "source_url": "https://www.stat.go.jp/data/shakai/2021/pdf/youyakua.pdf",
        "note": "令和3年調査。有業者（在宅勤務以外）の通勤・通学時間 往復1時間7分の片道換算",
    },
}

# --- 法定の既定値（統計ではなく労働基準法に基づく。所定労働時間・休憩の未指定時に適用する） ---
STATUTORY_DEFAULTS: dict[str, dict[str, Any]] = {
    "scheduled_hours": {
        "value": 8.0,
        "basis": "労働基準法第32条（法定労働時間 1日8時間）",
        "source_url": "https://laws.e-gov.go.jp/law/322AC0000000049",
    },
    "break_minutes": {
        "value": 60.0,
        "basis": "労働基準法第34条（労働時間が8時間を超える場合は少なくとも60分の休憩）",
        "source_url": "https://laws.e-gov.go.jp/law/322AC0000000049",
    },
}

_SENS_OVERTIME_DELTA_H = 10.0  # 感度分析: 月残業の増減幅（時間/月）
_SENS_COMMUTE_DELTA_MIN = 15.0  # 感度分析: 通勤片道の増減幅（分）


class CalcError(Exception):
    """入力の矛盾を表す。main で捕捉して終了コード2を返す。"""


@dataclass
class Analysis:
    """丸めを一切かけない算定結果。出力時にのみ丸める。"""

    month_workdays: float
    daily_scheduled_hours: float
    daily_break_h: float
    daily_overtime_h: float
    commute_oneway_h: float
    daily_binding_hours: float
    annual_working_days: float
    paid_leave_taken_days: float
    annual_binding_hours: float
    annual_labor_hours: float


def _check_range(name: str, value: float, *, low: float | None = None,
                 high: float | None = None) -> None:
    if low is not None and value < low:
        raise CalcError(f"{name} が下限（{low}）を下回っている: {value}")
    if high is not None and value > high:
        raise CalcError(f"{name} が上限（{high}）を超えている: {value}")


def analyze(
    scheduled_hours: float,
    break_minutes: float,
    monthly_overtime_h: float,
    annual_holidays: float,
    paid_leave_rate: float,
    paid_leave_granted: float,
    commute_oneway_min: float,
    paid_leave_taken: float | None = None,
) -> Analysis:
    """定義式に従って拘束時間・労働時間を算定する純粋関数。丸めをかけない。

    入力の矛盾は CalcError を送出する。
    """
    _check_range("annual_holidays", annual_holidays, low=0)
    if annual_holidays >= 365:
        raise CalcError(f"annual_holidays が365以上で実出勤日が無い: {annual_holidays}")
    _check_range("scheduled_hours", scheduled_hours, low=0, high=24)
    _check_range("break_minutes", break_minutes, low=0)
    _check_range("monthly_overtime_h", monthly_overtime_h, low=0)
    _check_range("paid_leave_rate", paid_leave_rate, low=0, high=1)
    _check_range("paid_leave_granted", paid_leave_granted, low=0)
    _check_range("commute_oneway_min", commute_oneway_min, low=0)
    if paid_leave_taken is not None:
        _check_range("paid_leave_taken", paid_leave_taken, low=0)

    month_workdays = (365 - annual_holidays) / 12
    daily_overtime_h = monthly_overtime_h / month_workdays
    break_h = break_minutes / 60
    commute_oneway_h = commute_oneway_min / 60
    daily_binding_hours = (
        scheduled_hours + break_h + daily_overtime_h + commute_oneway_h * 2
    )

    if paid_leave_taken is not None:
        taken_days = paid_leave_taken
    else:
        taken_days = paid_leave_granted * paid_leave_rate

    annual_working_days = 365 - annual_holidays - taken_days
    if annual_working_days <= 0:
        raise CalcError(
            f"年間実出勤日数が0以下になる（年間休日{annual_holidays}日 + "
            f"有給取得{taken_days}日 が365日以上）"
        )

    annual_binding_hours = annual_working_days * daily_binding_hours
    annual_labor_hours = annual_working_days * (scheduled_hours + daily_overtime_h)

    return Analysis(
        month_workdays=month_workdays,
        daily_scheduled_hours=scheduled_hours,
        daily_break_h=break_h,
        daily_overtime_h=daily_overtime_h,
        commute_oneway_h=commute_oneway_h,
        daily_binding_hours=daily_binding_hours,
        annual_working_days=annual_working_days,
        paid_leave_taken_days=taken_days,
        annual_binding_hours=annual_binding_hours,
        annual_labor_hours=annual_labor_hours,
    )


def effective_hourly_wage(
    salary: float | None,
    annual_binding_hours: float,
    annual_labor_hours: float,
) -> dict[str, int] | None:
    """実質時給を算定する。グレード付き想定年収が無ければ None を返す。"""
    if salary is None:
        return None
    return {
        "binding_basis": round(salary / annual_binding_hours),
        "labor_basis": round(salary / annual_labor_hours),
    }


def sensitivity(
    scheduled_hours: float,
    break_minutes: float,
    monthly_overtime_h: float,
    annual_holidays: float,
    paid_leave_rate: float,
    paid_leave_granted: float,
    commute_oneway_min: float,
    paid_leave_taken: float | None = None,
) -> dict[str, float]:
    """月残業±10h・通勤片道±15分それぞれの年間拘束時間の増減（丸め前）を返す。"""
    base = analyze(
        scheduled_hours, break_minutes, monthly_overtime_h, annual_holidays,
        paid_leave_rate, paid_leave_granted, commute_oneway_min, paid_leave_taken,
    ).annual_binding_hours

    def binding_with(overtime: float, commute: float) -> float:
        return analyze(
            scheduled_hours, break_minutes, overtime, annual_holidays,
            paid_leave_rate, paid_leave_granted, commute, paid_leave_taken,
        ).annual_binding_hours

    return {
        "overtime_plus10h": binding_with(
            monthly_overtime_h + _SENS_OVERTIME_DELTA_H, commute_oneway_min) - base,
        "overtime_minus10h": binding_with(
            monthly_overtime_h - _SENS_OVERTIME_DELTA_H, commute_oneway_min) - base,
        "commute_plus15min": binding_with(
            monthly_overtime_h, commute_oneway_min + _SENS_COMMUTE_DELTA_MIN) - base,
        "commute_minus15min": binding_with(
            monthly_overtime_h, commute_oneway_min - _SENS_COMMUTE_DELTA_MIN) - base,
    }


def _source_meta(
    key: str,
    provided: bool,
    sources: dict[str, Any],
    fallback_url: str | None,
) -> dict[str, Any]:
    """入力1件の {source, source_url, grade} を決める。"""
    if not provided:
        return {"source": "fallback", "source_url": fallback_url, "grade": None}
    meta = sources.get(key)
    if isinstance(meta, dict):
        source = meta.get("source", "user")
        return {
            "source": source if source in ("posting", "research", "user", "fallback") else "user",
            "source_url": meta.get("source_url"),
            "grade": meta.get("grade"),
        }
    return {"source": "user", "source_url": None, "grade": None}


def build_time_analysis(
    provided: dict[str, Any],
    sources: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """CLI から渡された値（未指定はフォールバック適用）を time_analysis.json 構造に組み立てる。

    provided は各入力キー→値の辞書。値が None または欠落の場合はフォールバックを適用する。
    salary は None のとき effective_hourly_wage を null にする（フォールバックしない）。
    """
    sources = sources or {}
    fallbacks_used: list[dict[str, Any]] = []
    assumptions: list[str] = []
    inputs: dict[str, Any] = {}

    def resolve_survey(key: str) -> float:
        """FALLBACKS 由来の統計値を解決し、未指定なら記録する。"""
        val = provided.get(key)
        if val is None:
            fb = FALLBACKS[key]
            fallbacks_used.append({
                "field": key,
                "value": fb["value"],
                "survey": fb["survey"],
                "survey_year": fb["survey_year"],
                "source_url": fb["source_url"],
            })
            assumptions.append(
                f"{key} は未指定のため統計フォールバックを適用した："
                f"{fb['value']}（{fb['survey']} {fb['survey_year']}年・{fb['note']}、{fb['source_url']}）"
            )
            return float(fb["value"])
        return float(val)

    def resolve_statutory(key: str) -> float:
        """STATUTORY_DEFAULTS 由来の法定既定値を解決し、未指定なら記録する。"""
        val = provided.get(key)
        if val is None:
            sd = STATUTORY_DEFAULTS[key]
            fallbacks_used.append({
                "field": key,
                "value": sd["value"],
                "basis": sd["basis"],
                "source_url": sd["source_url"],
            })
            assumptions.append(
                f"{key} は未指定のため法定既定値を適用した："
                f"{sd['value']}（{sd['basis']}、{sd['source_url']}）"
            )
            return float(sd["value"])
        return float(val)

    scheduled_hours = resolve_statutory("scheduled_hours")
    break_minutes = resolve_statutory("break_minutes")
    monthly_overtime_h = resolve_survey("monthly_overtime_h")
    annual_holidays = resolve_survey("annual_holidays")
    commute_oneway_min = resolve_survey("commute_oneway_min")

    taken_provided = provided.get("paid_leave_taken") is not None
    if taken_provided:
        paid_leave_taken: float | None = float(provided["paid_leave_taken"])
        paid_leave_rate = None
        paid_leave_granted = None
    else:
        paid_leave_taken = None
        paid_leave_rate = resolve_survey("paid_leave_rate")
        paid_leave_granted = resolve_survey("paid_leave_granted")

    result = analyze(
        scheduled_hours, break_minutes, monthly_overtime_h, annual_holidays,
        paid_leave_rate if paid_leave_rate is not None else 0.0,
        paid_leave_granted if paid_leave_granted is not None else 0.0,
        commute_oneway_min, paid_leave_taken,
    )

    salary = provided.get("salary")
    salary = float(salary) if salary is not None else None
    wage = effective_hourly_wage(salary, result.annual_binding_hours, result.annual_labor_hours)
    if salary is None:
        assumptions.append(
            "グレード付き想定年収が無いため、実質時給（effective_hourly_wage）は算定しない（null）。"
        )

    sens = sensitivity(
        scheduled_hours, break_minutes, monthly_overtime_h, annual_holidays,
        paid_leave_rate if paid_leave_rate is not None else 0.0,
        paid_leave_granted if paid_leave_granted is not None else 0.0,
        commute_oneway_min, paid_leave_taken,
    )

    # inputs（使用した全数値。丸めない生値）
    def add_input(key: str, value: float, is_survey: bool) -> None:
        fb_url = None
        if is_survey and key in FALLBACKS:
            fb_url = FALLBACKS[key]["source_url"]
        elif key in STATUTORY_DEFAULTS:
            fb_url = STATUTORY_DEFAULTS[key]["source_url"]
        meta = _source_meta(key, provided.get(key) is not None, sources, fb_url)
        inputs[key] = {"value": value, **meta}

    add_input("scheduled_hours", scheduled_hours, is_survey=False)
    add_input("break_minutes", break_minutes, is_survey=False)
    add_input("monthly_overtime_h", monthly_overtime_h, is_survey=True)
    add_input("annual_holidays", annual_holidays, is_survey=True)
    add_input("commute_oneway_min", commute_oneway_min, is_survey=True)
    if taken_provided:
        add_input("paid_leave_taken", paid_leave_taken, is_survey=False)
        assumptions.append(
            f"有給取得日数は入力値 {paid_leave_taken} 日を用いた。"
        )
    else:
        add_input("paid_leave_rate", paid_leave_rate, is_survey=True)
        add_input("paid_leave_granted", paid_leave_granted, is_survey=True)
        assumptions.append(
            f"有給取得日数は付与日数×取得率で推計した"
            f"（付与 {paid_leave_granted} 日 × 取得率 {paid_leave_rate}）。"
        )
    if salary is not None:
        meta = _source_meta("salary", True, sources, None)
        inputs["salary"] = {"value": salary, **meta}

    return {
        "inputs": inputs,
        "daily": {
            "scheduled_hours": round(result.daily_scheduled_hours, 1),
            "break_h": round(result.daily_break_h, 1),
            "daily_overtime_h": round(result.daily_overtime_h, 1),
            "commute_oneway_h": round(result.commute_oneway_h, 1),
            "binding_hours": round(result.daily_binding_hours, 1),
        },
        "annual": {
            "working_days": round(result.annual_working_days),
            "paid_leave_taken_days": round(result.paid_leave_taken_days),
            "binding_hours": round(result.annual_binding_hours, 1),
            "labor_hours": round(result.annual_labor_hours, 1),
        },
        "effective_hourly_wage": wage,
        "sensitivity": {k: round(v, 1) for k, v in sens.items()},
        "assumptions": assumptions,
        "fallbacks_used": fallbacks_used,
    }


def _load_sources(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="job-change-fit-assessment 拘束時間・実質時給の算定ツール"
    )
    parser.add_argument("--scheduled-hours", type=float, default=None, help="1日の所定労働時間")
    parser.add_argument("--break-minutes", type=float, default=None, help="1日の休憩時間（分）")
    parser.add_argument("--overtime-h-month", type=float, default=None, help="月平均の残業時間")
    parser.add_argument("--annual-holidays", type=float, default=None, help="年間休日総数")
    parser.add_argument("--paid-leave-rate", type=float, default=None, help="有給取得率（0〜1）")
    parser.add_argument("--paid-leave-granted", type=float, default=None, help="有給付与日数")
    parser.add_argument("--paid-leave-taken", type=float, default=None, help="有給取得日数の実績")
    parser.add_argument("--commute-oneway-min", type=float, default=None, help="通勤片道（分）")
    parser.add_argument("--salary", type=float, default=None, help="想定年収（円）")
    parser.add_argument("--sources-json", default=None, help="各入力の出典メタJSONパス")
    parser.add_argument("--out", default=None, help="出力先パス（親ディレクトリは自動作成）")
    parser.add_argument("--json", action="store_true", help="結果をJSONで標準出力へ書き出す")
    args = parser.parse_args(argv)

    provided = {
        "scheduled_hours": args.scheduled_hours,
        "break_minutes": args.break_minutes,
        "monthly_overtime_h": args.overtime_h_month,
        "annual_holidays": args.annual_holidays,
        "paid_leave_rate": args.paid_leave_rate,
        "paid_leave_granted": args.paid_leave_granted,
        "paid_leave_taken": args.paid_leave_taken,
        "commute_oneway_min": args.commute_oneway_min,
        "salary": args.salary,
    }

    try:
        sources = _load_sources(args.sources_json)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] --sources-json を読み込めない（{exc}）", file=sys.stderr)
        return 2

    try:
        analysis = build_time_analysis(provided, sources)
    except CalcError as exc:
        print(f"[ERROR] 入力の矛盾: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(analysis, ensure_ascii=False, indent=2)

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
