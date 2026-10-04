"""job-change-support: 1.x/2.0 の profile.json を、職歴と転職の軸の2ファイルへ分ける。

schema_version 1.0・1.1・2.0 の profile.json は職歴の事実と転職の軸を1つに持つ。
このスクリプトはそれを、職歴だけを持つ profile.json（schema_version 3.0）と、
転職の軸を持つ axis.json（元の schema_version を引き継ぐ）へ分ける。値は移すだけで、
書き換えない。仕様の原本は references/axis-format.md である。

書き込みの順序: バックアップ（profile.json.bak-{元の版}）→ axis.json → profile.json の
置き換え。途中で失敗したときは、作ったファイルを消して元の状態へ戻す。

CLI:
    python split_profile.py <profile.json> [--json]

終了コード: 0 = 分割した、1 = 分割しなかった（理由を errors に示す）
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import validate_axis as va  # noqa: E402
import validate_profile as vp  # noqa: E402

AXIS_FILENAME = "axis.json"
# 3.0 の profile.json が持つキー。これ以外のキーは profile.json に残し、報告に挙げる。
_PROFILE_KEYS = (
    "schema_version",
    "updated_at",
    "summary",
    "basic",
    "career_history",
    "career_gaps",
    "skills",
    "strengths",
    "notes",
)


def split(document: dict) -> tuple[dict, dict, list[str]]:
    """(3.0 の profile, axis, どちらの一覧にも無いキー) を返す。入力は書き換えない。"""
    axis: dict = {"schema_version": document.get("schema_version")}
    if "updated_at" in document:
        axis["updated_at"] = document["updated_at"]
    for key in vp._AXIS_KEYS:
        if key in document:
            axis[key] = document[key]

    profile = {key: value for key, value in document.items() if key not in vp._AXIS_KEYS}
    profile["schema_version"] = vp._V3_SCHEMA_VERSION
    unknown = [key for key in profile if key not in _PROFILE_KEYS]
    return profile, axis, unknown


def _write_json(path: str, document: Any) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(document, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _remove_quietly(path: str) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


def run(profile_path: str) -> dict:
    report: dict = {"status": "FAIL", "errors": []}

    try:
        document = vp.load_profile(profile_path)
    except (OSError, ValueError) as exc:
        report["errors"].append(f"{profile_path}: JSON として読み込めない（{exc}）")
        return report
    if not isinstance(document, dict):
        report["errors"].append("ルート要素はオブジェクトでなければならない")
        return report

    version = document.get("schema_version")
    if version not in vp._AXIS_SCHEMA_VERSIONS:
        report["errors"].append(
            "分割の対象は schema_version が文字列の "
            f"{'/'.join(vp._AXIS_SCHEMA_VERSIONS)} の profile.json である"
            f"（指定されたファイルは {version!r}）"
        )
        return report

    axis_path = os.path.join(os.path.dirname(os.path.abspath(profile_path)), AXIS_FILENAME)
    backup_path = f"{profile_path}.bak-{version}"
    tmp_path = f"{profile_path}.tmp"
    for existing in (axis_path, backup_path, tmp_path):
        if os.path.exists(existing):
            report["errors"].append(f"{existing} が既にある。内容を確かめて片づけてから実行する")
    if report["errors"]:
        return report

    profile, axis, unknown = split(document)

    try:
        shutil.copy2(profile_path, backup_path)
        _write_json(axis_path, axis)
        _write_json(tmp_path, profile)
        os.replace(tmp_path, profile_path)
    except Exception as exc:
        # profile.json は置き換え前なので元のまま残っている。作りかけのファイルだけ消す。
        for path in (tmp_path, axis_path, backup_path):
            _remove_quietly(path)
        report["errors"].append(f"書き込みに失敗したため、元の状態へ戻した（{exc}）")
        return report

    report.update(
        status="PASS",
        profile=os.path.abspath(profile_path),
        axis=axis_path,
        backup=os.path.abspath(backup_path),
        unknown_keys=unknown,
        profile_validation=vp.validate(profile).to_dict(),
        axis_validation=va.validate_axis(axis).to_dict(),
    )
    return report


def format_report(report: dict) -> str:
    if report["status"] != "PASS":
        return "\n".join(["分割結果: FAIL", *(f"[ERROR] {e}" for e in report["errors"])])
    lines = [
        "分割結果: PASS",
        f"profile: {report['profile']}",
        f"axis: {report['axis']}",
        f"backup: {report['backup']}",
    ]
    if report["unknown_keys"]:
        lines.append(f"profile.json に残した一覧外のキー: {', '.join(report['unknown_keys'])}")
    for label in ("profile_validation", "axis_validation"):
        validation = report[label]
        lines.append(
            f"{label}: {validation['status']}"
            f"（ERROR {validation['error_count']}件 / WARN {validation['warning_count']}件）"
        )
        lines.extend(validation["errors"])
        lines.extend(validation["warnings"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="profile.json を職歴と転職の軸の2ファイルへ分ける")
    parser.add_argument("profile_path", help="分割する profile.json（schema_version 1.0/1.1/2.0）のパス")
    parser.add_argument("--json", action="store_true", help="結果をJSON形式で出力する")
    args = parser.parse_args(argv)

    report = run(args.profile_path)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_report(report))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
