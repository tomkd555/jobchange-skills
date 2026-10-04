"""job-change-support: 転職の軸（axis.json）の機械的な（非LLM）検証ツール。

標準ライブラリのみで、転職の軸（転職理由・条件・作業特性の希望・企業スコアの軸・
志望先・年収）を機械的に検査する。検査の本体は validate_profile.py の check_axis で、
このスクリプトはその入口である。axis.json に加えて、軸を内包する schema_version
1.x/2.0 の profile.json も受け付ける。仕様の原本は references/axis-format.md である。

CLI:
    python validate_axis.py <axis.json | 1.x/2.0 の profile.json> [--json]

終了コード: 0 = PASS（ERROR 0件。WARN があっても PASS）、1 = FAIL（ERROR 1件以上）
"""
from __future__ import annotations

import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import validate_profile as vp  # noqa: E402


def validate_axis(document: Any) -> vp.ValidationResult:
    result = vp.ValidationResult()

    if not isinstance(document, dict):
        result.add_error("(root)", "ルート要素はオブジェクトでなければならない")
        return result

    version = document.get("schema_version")
    if not vp._is_nonempty_str(version):
        result.add_error("schema_version", "schema_version は必須（非空の文字列）である")
    elif version == vp._V3_SCHEMA_VERSION:
        result.add_error(
            "schema_version",
            "schema_version 3.0 は職歴だけを持つ profile.json の版である。転職の軸は axis.json を指定する",
        )
        return result

    vp.check_axis(document, result)
    vp._warn_updated_at(document, result)
    vp._warn_schema_version_known(document, result, vp._AXIS_SCHEMA_VERSIONS)

    return result


def main(argv: list[str] | None = None) -> int:
    return vp.run_cli(
        argv,
        validate_axis,
        "job-change-support 転職の軸の検証ツール",
        "検証対象の axis.json（または 1.x/2.0 の profile.json）のファイルパス",
    )


if __name__ == "__main__":
    sys.exit(main())
