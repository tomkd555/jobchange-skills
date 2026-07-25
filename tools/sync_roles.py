"""役割プロンプト（skills/*/references/roles/*.md）から、Claude Code 用の
エージェント定義（agents/*.md）を生成・検査する。

役割プロンプトが原本であり、agents/ はその写しである。出力ファイル名は役割プロンプトの
frontmatter の `name` に一致させる。写しを置く理由は、Claude Code がプラグイン直下の
agents/ しかエージェント定義として読まないためである。サブエージェントを持たない
ハーネス（Codex ほか）は agents/ を使わず、各スキルの references/roles/ を直接読む。

CLI:
    python tools/sync_roles.py            # 生成（差分があれば書き換える）
    python tools/sync_roles.py --check    # 検査のみ。差分があれば終了コード 1

終了コード: 0 = 一致（または生成成功）、1 = 差分あり（--check 時）、2 = 原本の不備
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
AGENTS_DIR = REPO_ROOT / "agents"

NAME_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
NAME_FIELD = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)


def role_files() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/references/roles/*.md"))


def agent_name(path: Path) -> str:
    """役割プロンプトの frontmatter から name を取り出す。"""
    text = path.read_text(encoding="utf-8")
    match = NAME_PATTERN.match(text)
    if match is None:
        raise ValueError(f"frontmatter が無い: {path}")
    name_match = NAME_FIELD.search(match.group(1))
    if name_match is None:
        raise ValueError(f"frontmatter に name が無い: {path}")
    return name_match.group(1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="役割プロンプトから agents/ を生成・検査する")
    parser.add_argument("--check", action="store_true", help="生成せず、差分の有無だけを検査する")
    args = parser.parse_args(argv)

    sources = role_files()
    if not sources:
        print(f"[ERROR] 役割プロンプトが1件も無い: {SKILLS_DIR}/*/references/roles/*.md")
        return 2

    expected: dict[str, Path] = {}
    for source in sources:
        try:
            name = agent_name(source)
        except ValueError as exc:
            print(f"[ERROR] {exc}")
            return 2
        if name in expected:
            print(f"[ERROR] name が重複している: {name}（{expected[name]} と {source}）")
            return 2
        expected[name] = source

    stale = []
    if AGENTS_DIR.is_dir():
        for existing in sorted(AGENTS_DIR.glob("*.md")):
            if existing.stem not in expected:
                stale.append(existing)

    differences = []
    for name, source in expected.items():
        target = AGENTS_DIR / f"{name}.md"
        wanted = source.read_text(encoding="utf-8")
        current = target.read_text(encoding="utf-8") if target.is_file() else None
        if current == wanted:
            continue
        differences.append((target, source, wanted, current is None))

    if args.check:
        for target, source, _, missing in differences:
            reason = "未生成" if missing else "内容が原本と異なる"
            print(f"[DIFF] {target.relative_to(REPO_ROOT)}: {reason}（原本: {source.relative_to(REPO_ROOT)}）")
        for extra in stale:
            print(f"[DIFF] {extra.relative_to(REPO_ROOT)}: 対応する原本が無い")
        if differences or stale:
            print(f"差分 {len(differences) + len(stale)} 件。python tools/sync_roles.py で同期する")
            return 1
        print(f"一致（{len(expected)} 件）")
        return 0

    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    for target, source, wanted, _ in differences:
        target.write_text(wanted, encoding="utf-8")
        print(f"[WRITE] {target.relative_to(REPO_ROOT)} ← {source.relative_to(REPO_ROOT)}")
    for extra in stale:
        extra.unlink()
        print(f"[DELETE] {extra.relative_to(REPO_ROOT)}（対応する原本が無い）")
    print(f"同期完了（原本 {len(expected)} 件 / 書き換え {len(differences)} 件 / 削除 {len(stale)} 件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
