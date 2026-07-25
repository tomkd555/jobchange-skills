"""job-change-company-research: company_research.json の決定的（非LLM）検証ツール。

標準ライブラリのみで、企業研究の中間成果物である company_research.json を機械検査する。
すべての主張（claim）が出典・証拠グレード・確度を伴い、必須トピックを網羅し、低グレード
（C・D）のみの根拠で断定（confidence=high）していないかを、ERROR（成果物として成立しない
欠落・ルール違反）と WARN（成立するが根拠が弱い点）に分けて報告する。仕様の原本は
references/company-research-format.md、証拠グレードの原本は references/evidence-grading.md
である。

CLI:
    python validate_company_research.py <company_research.json> [--json]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any

VALID_TOPICS = {
    "philosophy", "business", "financials", "compensation",
    "benefits", "workstyle", "reputation", "selection_process",
}
# 必須トピック（各1件以上の claim を要求する）。selection_process は WARN 扱いのため除く。
REQUIRED_TOPICS = [
    "philosophy", "business", "financials", "compensation",
    "benefits", "workstyle", "reputation",
]
VALID_GRADES = {"A", "B", "C", "D"}
HIGH_GRADES = {"A", "B"}
LOW_GRADES = {"C", "D"}
VALID_CONFIDENCE = {"high", "medium", "low"}
REQUIRED_CLAIM_FIELDS = ("id", "topic", "statement", "evidence", "confidence")
# workstyle_metrics の5キー。各値は {value(number), source_url(str), grade(A〜D)} または null。
WORKSTYLE_METRIC_KEYS = (
    "annual_holidays",
    "monthly_overtime_h",
    "paid_leave_rate",
    "avg_paid_leave_days_taken",
    "avg_annual_salary",
)
# tier（企業品質の格付け）。仕様の原本は references/tier-rubric.md。
TIER_AXES = ("financial_soundness", "growth", "tech_advancement", "compensation_level")
VALID_TIER_LEVELS = {"S", "A", "B", "C"}
VALID_AXIS_RATINGS = {"high", "medium", "low", "unknown"}
RATED_AXIS_RATINGS = {"high", "medium", "low"}


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


def _is_nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _is_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float))


def _validate_workstyle_metrics(document: dict, result: ValidationResult) -> None:
    """任意フィールド workstyle_metrics を検査する（加算的・後方互換）。

    - workstyle_metrics 全体の欠落は WARN（後方互換。既存スキーマは必須にしない）。
    - workstyle_metrics が存在してオブジェクトでない場合は ERROR。
    - 各メトリックは {value(number), source_url(str), grade(A〜D)} または null。
      欠落・null は WARN。存在時の型・グレード不正は ERROR。
    """
    if "workstyle_metrics" not in document:
        result.add_warning(
            "workstyle_metrics",
            "働き方数値の構造化（workstyle_metrics）が無い。可能な範囲で構造化することを推奨する",
        )
        return
    metrics = document.get("workstyle_metrics")
    if not isinstance(metrics, dict):
        result.add_error("workstyle_metrics", "workstyle_metrics はオブジェクトでなければならない")
        return
    for key in WORKSTYLE_METRIC_KEYS:
        path = f"workstyle_metrics.{key}"
        if key not in metrics or metrics[key] is None:
            result.add_warning(path, f"{key} が未設定（null）である")
            continue
        entry = metrics[key]
        if not isinstance(entry, dict):
            result.add_error(
                path,
                "{value, source_url, grade} のオブジェクトまたは null でなければならない",
            )
            continue
        if not _is_number(entry.get("value")):
            result.add_error(f"{path}.value", "value は数値でなければならない")
        url = entry.get("source_url")
        if not isinstance(url, str) or not url.startswith("http"):
            result.add_error(
                f"{path}.source_url",
                f"source_url は http で始まる文字列でなければならない（実値: {url!r}）",
            )
        grade = entry.get("grade")
        if grade not in VALID_GRADES:
            result.add_error(
                f"{path}.grade",
                f"grade は A・B・C・D のいずれかでなければならない（実値: {grade!r}）",
            )


def _validate_tier(
    document: dict, result: ValidationResult, claim_ids_present: set[str]
) -> None:
    """必須フィールド tier（企業品質の格付け）の構造・列挙・参照を検査する。

    格付けそのものの妥当性（rating が証拠グレードに照らして妥当か、level が4軸から
    基準どおり導かれているか）は機械検査せず、独立監査（job-change-research-auditor）の
    領分とする。仕様の原本は references/tier-rubric.md。
    """
    if "tier" not in document:
        result.add_error(
            "tier",
            "tier（企業品質の格付け）は必須である。references/tier-rubric.md に従って付す",
        )
        return
    tier = document.get("tier")
    if not isinstance(tier, dict):
        result.add_error("tier", "tier はオブジェクトでなければならない")
        return

    level = tier.get("level")
    if level not in VALID_TIER_LEVELS:
        result.add_error(
            "tier.level",
            f"level は S・A・B・C のいずれかでなければならない（実値: {level!r}）",
        )

    if not isinstance(tier.get("provisional"), bool):
        result.add_error(
            "tier.provisional",
            f"provisional は真偽値でなければならない（実値: {tier.get('provisional')!r}）",
        )

    if not _is_nonempty_str(tier.get("rationale")):
        result.add_error("tier.rationale", "rationale は必須（非空）である")

    if "rubric_version" not in tier:
        result.add_warning("tier.rubric_version", "rubric_version が未設定である")
    if not _is_nonempty_str(tier.get("assessed_date")):
        result.add_warning("tier.assessed_date", "assessed_date が未設定である")

    axes = tier.get("axes")
    if not isinstance(axes, dict):
        result.add_error("tier.axes", "axes はオブジェクトが必須である（4軸すべてを持つ）")
        return

    for axis in TIER_AXES:
        apath = f"tier.axes.{axis}"
        if axis not in axes:
            result.add_error(apath, f"軸 {axis} が無い（4軸すべてが必須である）")
            continue
        entry = axes[axis]
        if not isinstance(entry, dict):
            result.add_error(
                apath, "各軸は {rating, basis, claim_ids} のオブジェクトでなければならない"
            )
            continue

        rating = entry.get("rating")
        if rating not in VALID_AXIS_RATINGS:
            result.add_error(
                f"{apath}.rating",
                f"rating は high・medium・low・unknown のいずれかでなければならない（実値: {rating!r}）",
            )
        if not _is_nonempty_str(entry.get("basis")):
            result.add_error(f"{apath}.basis", "basis は必須（非空）である")

        claim_ids = entry.get("claim_ids")
        if not isinstance(claim_ids, list):
            result.add_error(f"{apath}.claim_ids", "claim_ids は配列でなければならない")
        else:
            for cid in claim_ids:
                if cid not in claim_ids_present:
                    result.add_error(
                        f"{apath}.claim_ids",
                        f"claims に存在しない claim id を参照している（{cid!r}）",
                    )
            if rating in RATED_AXIS_RATINGS and not claim_ids:
                result.add_warning(
                    f"{apath}.claim_ids",
                    f"rating={rating} の軸に根拠 claim_ids が無い。根拠 claim の id を1件以上示すことを推奨する",
                )


def _validate_company(document: dict, result: ValidationResult) -> None:
    company = document.get("company")
    if not isinstance(company, dict):
        result.add_error("company", "company はオブジェクトが必須である")
        return
    if not _is_nonempty_str(company.get("name")):
        result.add_error("company.name", "company.name は必須（非空）である")


def _validate_evidence(evidence: Any, claim_path: str, result: ValidationResult) -> dict:
    """evidence 配列を検査し、有効グレードの集約情報を返す。

    返す dict:
        valid_grades: A〜D のうち有効値だったグレードの一覧
        has_high:     A または B のグレードが1件以上あるか
    """
    if not isinstance(evidence, list) or not evidence:
        result.add_error(f"{claim_path}.evidence", "evidence は1件以上必要である")
        return {"valid_grades": [], "has_high": False}

    valid_grades: list[str] = []
    has_high = False
    for i, ev in enumerate(evidence):
        ev_path = f"{claim_path}.evidence[{i}]"
        if not isinstance(ev, dict):
            result.add_error(ev_path, "evidence の各要素はオブジェクトでなければならない")
            continue

        url = ev.get("source_url")
        if not isinstance(url, str) or not url.startswith("http"):
            result.add_error(
                f"{ev_path}.source_url",
                f"source_url は http で始まる文字列でなければならない（実値: {url!r}）",
            )

        grade = ev.get("grade")
        if grade not in VALID_GRADES:
            result.add_error(
                f"{ev_path}.grade",
                f"grade は A・B・C・D のいずれかでなければならない（実値: {grade!r}）",
            )
        else:
            valid_grades.append(grade)
            if grade in HIGH_GRADES:
                has_high = True

        if not _is_nonempty_str(ev.get("quote")):
            result.add_error(f"{ev_path}.quote", "quote は必須（非空。引用）である")

    return {"valid_grades": valid_grades, "has_high": has_high}


def _validate_claim(claim: Any, index: int, result: ValidationResult) -> dict | None:
    """1件の claim を検査し、集約に必要な {topic, low_only} を返す。"""
    if not isinstance(claim, dict):
        result.add_error(f"claims[{index}]", "claim はオブジェクトでなければならない")
        return None

    raw_id = claim.get("id")
    path = raw_id if _is_nonempty_str(raw_id) else f"claims[{index}]"

    if not _is_nonempty_str(raw_id):
        result.add_error(path, "id は必須（非空）である")
    if not _is_nonempty_str(claim.get("statement")):
        result.add_error(path, "statement は必須（非空。反証可能な命題）である")

    topic = claim.get("topic")
    valid_topic: str | None = None
    if not _is_nonempty_str(topic):
        result.add_error(path, "topic は必須（非空）である")
    elif topic not in VALID_TOPICS:
        result.add_error(
            path,
            f"topic は次の8種のいずれかでなければならない {sorted(VALID_TOPICS)}（実値: {topic!r}）",
        )
    else:
        valid_topic = topic

    confidence = claim.get("confidence")
    if not _is_nonempty_str(confidence):
        result.add_error(path, "confidence は必須（非空）である")
    elif confidence not in VALID_CONFIDENCE:
        result.add_error(
            path,
            f"confidence は high・medium・low のいずれかでなければならない（実値: {confidence!r}）",
        )

    ev_info = _validate_evidence(claim.get("evidence"), path, result)

    # C・Dのみを根拠とする claim（有効グレードが存在し、そのすべてが C・D）
    low_only = bool(ev_info["valid_grades"]) and not ev_info["has_high"]
    if low_only and confidence == "high":
        result.add_error(
            path,
            "グレードC・Dのみを根拠とする claim に confidence=high を与えてはならない",
        )

    return {"topic": valid_topic, "low_only": low_only}


def validate(document: Any) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(document, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result

    _validate_company(document, result)

    if not _is_nonempty_str(document.get("research_date")):
        result.add_warning("research_date", "research_date が未設定である")

    _validate_workstyle_metrics(document, result)

    claims = document.get("claims")
    # tier の claim_ids 参照検査に使う、実在する claim id の集合。
    claim_ids_present: set[str] = set()
    if not isinstance(claims, list) or not claims:
        result.add_error("claims", "claims は1件以上必要である")
    else:
        # トピックごとに、そのトピックを持つ claim の low_only 判定を集める。
        topic_low_only: dict[str, list[bool]] = {}
        for i, claim in enumerate(claims):
            info = _validate_claim(claim, i, result)
            if isinstance(claim, dict) and _is_nonempty_str(claim.get("id")):
                claim_ids_present.add(claim["id"])
            if info is None or info["topic"] is None:
                continue
            topic_low_only.setdefault(info["topic"], []).append(info["low_only"])

        present_topics = set(topic_low_only.keys())

        # 必須7トピックの網羅（各1件以上）。
        for t in REQUIRED_TOPICS:
            if t not in present_topics:
                result.add_error(
                    "claims",
                    f"必須トピック {t!r} の claim が1件も無い",
                )

        # あるトピックの claim がすべてグレードC・Dのみの根拠であれば WARN。
        for t, flags in topic_low_only.items():
            if flags and all(flags):
                result.add_warning(
                    f"claims(topic={t})",
                    "このトピックの claim がすべてグレードC・Dのみの根拠である。"
                    "一次・二次（A・B）の裏付けを追加することを推奨する",
                )

        # selection_process の claim が0件であれば WARN（下流の面接対策が根拠に使う）。
        if "selection_process" not in present_topics:
            result.add_warning(
                "claims(topic=selection_process)",
                "selection_process の claim が0件である。"
                "選考プロセス・面接体験記の収集を推奨する（面接対策の根拠になる）",
            )

    _validate_tier(document, result, claim_ids_present)

    return result


def load_research(path: str) -> Any:
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

    parser = argparse.ArgumentParser(description="job-change-company-research 企業研究データ検証ツール")
    parser.add_argument("research_path", help="検証対象の company_research.json ファイルパス")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    try:
        document = load_research(args.research_path)
    except (OSError, json.JSONDecodeError) as exc:
        result = ValidationResult()
        result.add_error(args.research_path, f"JSON として読み込めない（{exc}）")
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(format_report(result))
        return 1

    result = validate(document)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(result))

    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
