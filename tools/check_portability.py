"""公開前の可搬性検査。作者の環境に固有の記述が残っていないかを調べる。

このリポジトリは他者へ配布する。特定の利用者のホームディレクトリ・データ置き場所・
ビルド生成物が残っていると、そのまま導入しても動かず、作者の環境情報も漏れる。
本ツールはそれらを機械的に検出する。

検査対象は git が追跡しているファイルに限る。公開されるのはこの範囲であり、
`.gitignore` で除外したナレッジグラフ・利用者データ・`__pycache__` は対象外である。

CLI:
    python tools/check_portability.py [--json]

終了コード: 0 = ERROR 0件（WARN は許容）、1 = ERROR 1件以上
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# 追跡されていてはならないビルド生成物のディレクトリ名
ARTIFACT_DIR_NAMES = {"__pycache__", ".pytest_cache"}
# 記入例（架空であることを確かめる対象）のパス形式
EXAMPLE_ASSET_PATTERN = re.compile(r"skills/[^/]+/assets/[^/]+\.json")
# 本文の検査対象にする拡張子
TEXT_SUFFIXES = {".md", ".json", ".py", ".txt", ".yml", ".yaml"}

# 環境依存の絶対パス。プレースホルダ（{DATA_ROOT} 等）へ置き換えられているべきもの。
ABSOLUTE_PATH_PATTERNS = [
    (re.compile(r"[A-Za-z]:[\\/]Users[\\/]"), "Windows のホームディレクトリの絶対パス"),
    (re.compile(r"[A-Za-z]:[\\/]Mycode[\\/]"), "作者の作業ディレクトリの絶対パス"),
    (re.compile(r"(?<![\w/])/Users/[a-z]"), "macOS のホームディレクトリの絶対パス"),
    (re.compile(r"(?<![\w/])/home/[a-z]"), "Linux のホームディレクトリの絶対パス"),
]
# 作者の環境に固有のディレクトリ名
ENV_SPECIFIC_NAMES = [
    (re.compile(r"転職活動[\\/]"), "作者のデータディレクトリ名（転職活動）"),
    (re.compile(r"career-data"), "旧データディレクトリ名（career-data）"),
]
# 記入例に実在の企業名が混ざっていないかの手掛かり
FICTIONAL_MARKERS = ("架空", "kakuu", "アクメ", "ベータ", "ガンマ", "acme", "beta", "gamma", "example")
# 企業を指す値を文字列リテラルから取り出すパターン。記入例・仕様・テストのどこに書かれていても拾う。
_SLUG_BODY = r"[0-9A-Za-zぁ-ヿ一-龯][0-9A-Za-zぁ-ヿ一-龯-]*"
_CORPORATE_FORMS = r"株式会社|有限会社|合同会社|Inc\.|Corporation"
COMPANY_VALUE_PATTERNS = [
    re.compile(rf'["`]([SABCD]_{_SLUG_BODY})["`]'),
    re.compile(rf'"([^"\n]*(?:{_CORPORATE_FORMS})[^"\n]*)"'),
]


def iter_files() -> list[Path]:
    """git が追跡しているファイルを返す。"""
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit("追跡ファイルの一覧を取得できない。git リポジトリの作業ツリーで実行する。")
    return sorted(REPO_ROOT / name for name in result.stdout.split("\0") if name)


def check_text(path: Path, errors: list[dict], warnings: list[dict]) -> None:
    rel = path.relative_to(REPO_ROOT).as_posix()
    # 検査ツール自身のパターン定義は検査対象から外す
    if rel == "tools/check_portability.py":
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return
    for number, line in enumerate(text.splitlines(), 1):
        for pattern, label in ABSOLUTE_PATH_PATTERNS + ENV_SPECIFIC_NAMES:
            match = pattern.search(line)
            if match is None:
                continue
            entry = {"file": rel, "line": number, "reason": label, "text": line.strip()[:160]}
            # 単体テストは、不正な設定値としてこれらの文字列を意図的に使う
            if "/tests/" in rel or rel.endswith("_test.py"):
                warnings.append(entry | {"reason": f"{label}（テストの固定値の可能性）"})
            else:
                errors.append(entry)


def check_artifacts(files: list[Path], errors: list[dict]) -> None:
    for path in files:
        rel = path.relative_to(REPO_ROOT).as_posix()
        if not ARTIFACT_DIR_NAMES.intersection(rel.split("/")[:-1]):
            continue
        errors.append(
            {
                "file": rel,
                "line": 0,
                "reason": "ビルド生成物が追跡されている（.pyc に作者のビルドパスが埋まる）",
                "text": "",
            }
        )


def _is_fictional(value: str) -> bool:
    lowered = value.lower()
    return any(marker in value or marker in lowered for marker in FICTIONAL_MARKERS)


def check_examples(files: list[Path], warnings: list[dict]) -> None:
    for path in files:
        rel = path.relative_to(REPO_ROOT).as_posix()
        if not EXAMPLE_ASSET_PATTERN.fullmatch(rel):
            continue
        if _is_fictional(path.read_text(encoding="utf-8")):
            continue
        warnings.append(
            {
                "file": rel,
                "line": 0,
                "reason": "記入例に架空であることを示す語が無い（実在の企業名の混入を確認する）",
                "text": "",
            }
        )


def check_company_values(path: Path, warnings: list[dict]) -> None:
    """企業名・企業スラッグとして書かれた値が、架空であると分かる形かを調べる。

    記入例（assets）だけでなく、仕様（references）・スキル本文・単体テストも対象にする。
    作者が実際の応募先を書き写した箇所は、この3か所に紛れ込む。
    """
    rel = path.relative_to(REPO_ROOT).as_posix()
    if rel == "tools/check_portability.py":
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return
    for number, line in enumerate(text.splitlines(), 1):
        for pattern in COMPANY_VALUE_PATTERNS:
            for value in pattern.findall(line):
                if _is_fictional(value):
                    continue
                warnings.append(
                    {
                        "file": rel,
                        "line": number,
                        "reason": f"企業名・企業スラッグ「{value}」が架空と分からない（実在企業の混入を確認する）",
                        "text": line.strip()[:160],
                    }
                )


def check_roles_sync(errors: list[dict]) -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "sync_roles.py"), "--check"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return
    errors.append(
        {
            "file": "agents/",
            "line": 0,
            "reason": "役割プロンプトと agents/ が同期していない（python tools/sync_roles.py で同期する）",
            "text": result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "",
        }
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="公開前の可搬性検査")
    parser.add_argument("--json", action="store_true", help="結果を JSON で出力する")
    args = parser.parse_args(argv)

    errors: list[dict] = []
    warnings: list[dict] = []

    files = iter_files()
    for path in files:
        if path.suffix in TEXT_SUFFIXES:
            check_text(path, errors, warnings)
            check_company_values(path, warnings)
    check_artifacts(files, errors)
    check_examples(files, warnings)
    check_roles_sync(errors)

    status = "PASS" if not errors else "FAIL"
    if args.json:
        print(
            json.dumps(
                {
                    "status": status,
                    "error_count": len(errors),
                    "warning_count": len(warnings),
                    "errors": errors,
                    "warnings": warnings,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for entry in errors:
            location = f"{entry['file']}:{entry['line']}" if entry["line"] else entry["file"]
            print(f"[ERROR] {location}: {entry['reason']}")
            if entry["text"]:
                print(f"        {entry['text']}")
        for entry in warnings:
            location = f"{entry['file']}:{entry['line']}" if entry["line"] else entry["file"]
            print(f"[WARN]  {location}: {entry['reason']}")
        print(f"可搬性検査: {status}（ERROR {len(errors)}件 / WARN {len(warnings)}件）")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
