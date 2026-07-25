"""job-change-support: 利用者データの置き場所を定める設定ファイルの解決ツール。

転職支援スキル群は、利用者データ（profile.json・企業別成果物・求人検索結果）の
置き場所を設定ファイルだけで決める。既定の置き場所を持たず、設定が無ければ
hub（job-change-support）が対話で作る。設定ファイルの探索順序は次のとおりである。

    1. 環境変数 JOB_CHANGE_CONFIG が指すファイル
    2. カレントディレクトリから上位へ辿った最初の .job-change/config.json
    3. ~/.job-change/config.json

標準ライブラリのみを用いる。仕様の詳細は docs/configuration.md にある。

CLI:
    python jc_config.py --show
    python jc_config.py --init --data-root <絶対パス>
    python jc_config.py --path <キー>

終了コード:
    0 = 成功
    1 = 設定は見つかったが内容が不正、または --init で既存の設定を上書きしなかった
    2 = 設定ファイルが見つからない（未設定）
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

ENV_VAR = "JOB_CHANGE_CONFIG"
CONFIG_DIRNAME = ".job-change"
CONFIG_FILENAME = "config.json"
CONFIG_SCHEMA_VERSION = "1.0"

DIRECTORY_KEYS = ("private_dir", "companies_dir", "job_search_dir")
DEFAULTS: dict[str, str] = {
    "private_dir": "career-private",
    "companies_dir": "companies",
    "job_search_dir": "job-search",
    "python": "python",
}
# private_dir 配下に置く、原本が1つだけのファイル。
PRIVATE_FILES: dict[str, str] = {
    "profile": "profile.json",
    "company_index": "company_index.json",
    "self_analysis": "self_analysis.json",
    "commute": "commute.json",
}
PATH_KEYS = ("data_root", "private", "companies", "job_search", *PRIVATE_FILES)


class ConfigError(Exception):
    """設定ファイルの内容が不正であることを表す。"""


def _home(home: Path | None) -> Path:
    return Path(home) if home is not None else Path.home()


def find_config_path(
    env: dict[str, str] | None = None,
    start_dir: Path | str | None = None,
    home: Path | str | None = None,
) -> tuple[Path | None, str]:
    """設定ファイルを探索順序に従って探し、(パス, 由来) を返す。

    見つからない場合は (None, "") を返す。由来は env・project・home のいずれかである。
    """
    env = os.environ if env is None else env
    explicit = env.get(ENV_VAR)
    if explicit:
        candidate = Path(explicit).expanduser()
        if candidate.is_file():
            return candidate, "env"

    current = Path(start_dir).resolve() if start_dir is not None else Path.cwd().resolve()
    for directory in (current, *current.parents):
        candidate = directory / CONFIG_DIRNAME / CONFIG_FILENAME
        if candidate.is_file():
            return candidate, "project"

    candidate = _home(home) / CONFIG_DIRNAME / CONFIG_FILENAME
    if candidate.is_file():
        return candidate, "home"

    return None, ""


def searched_locations(
    env: dict[str, str] | None = None,
    start_dir: Path | str | None = None,
    home: Path | str | None = None,
) -> list[str]:
    """未設定を報告するときに提示する、探索した場所の一覧を返す。"""
    env = os.environ if env is None else env
    current = Path(start_dir).resolve() if start_dir is not None else Path.cwd().resolve()
    locations = [f"${ENV_VAR}={env.get(ENV_VAR, '')}".rstrip("=")]
    locations.append(str(current / CONFIG_DIRNAME / CONFIG_FILENAME) + "（上位ディレクトリも探索）")
    locations.append(str(_home(home) / CONFIG_DIRNAME / CONFIG_FILENAME))
    return locations


def load_config(path: Path | str, home: Path | str | None = None) -> dict[str, Any]:
    """設定ファイルを読み、既定値を補って返す。不正なら ConfigError を送出する。"""
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"設定ファイルを読めない: {path}（{exc}）") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"設定ファイルが JSON として壊れている: {path}（{exc}）") from exc

    if not isinstance(raw, dict):
        raise ConfigError(f"設定ファイルの最上位がオブジェクトでない: {path}")

    data_root = raw.get("data_root")
    if not isinstance(data_root, str) or not data_root.strip():
        raise ConfigError("data_root が無い。利用者データの置き場所を絶対パスで指定する")

    if data_root.startswith("~"):
        expanded = _home(home) / data_root[1:].lstrip("/\\")
    else:
        expanded = Path(data_root)
    if not expanded.is_absolute():
        raise ConfigError(f"data_root が絶対パスでない: {data_root}")

    config: dict[str, Any] = dict(DEFAULTS)
    config.update({k: v for k, v in raw.items() if k in DEFAULTS})
    config["schema_version"] = raw.get("schema_version", CONFIG_SCHEMA_VERSION)
    config["data_root"] = str(expanded)
    config["config_path"] = str(path)

    for key in DIRECTORY_KEYS:
        value = config[key]
        if not isinstance(value, str) or not value.strip():
            raise ConfigError(f"{key} が空である")
        if "/" in value or "\\" in value or value in (".", ".."):
            raise ConfigError(f"{key} は data_root 直下の単純なディレクトリ名で指定する: {value}")

    if not isinstance(config["python"], str) or not config["python"].strip():
        raise ConfigError("python が空である")

    return config


def resolve_paths(config: dict[str, Any]) -> dict[str, str]:
    """設定から、各データの絶対パスを組み立てる。ディレクトリは作らない。"""
    data_root = Path(config["data_root"])
    private = data_root / config["private_dir"]
    paths = {
        "data_root": str(data_root),
        "private": str(private),
        "companies": str(data_root / config["companies_dir"]),
        "job_search": str(data_root / config["job_search_dir"]),
    }
    for key, filename in PRIVATE_FILES.items():
        paths[key] = str(private / filename)
    return paths


def init_config(data_root: str, home: Path | str | None = None) -> Path:
    """~/.job-change/config.json を作る。既存があれば ConfigError を送出する。"""
    expanded = Path(data_root).expanduser()
    if not expanded.is_absolute():
        raise ConfigError(f"data_root は絶対パスで指定する: {data_root}")

    path = _home(home) / CONFIG_DIRNAME / CONFIG_FILENAME
    if path.exists():
        raise ConfigError(f"設定ファイルが既にある: {path}")

    payload = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "data_root": str(expanded),
        **DEFAULTS,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _emit(stream: Any, payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=stream)


def main(
    argv: list[str] | None = None,
    env: dict[str, str] | None = None,
    start_dir: Path | str | None = None,
    home: Path | str | None = None,
    stream: Any = None,
) -> int:
    parser = argparse.ArgumentParser(description="job-change 設定ファイルの解決ツール")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--show", action="store_true", help="解決した設定と各パスを JSON で出力する")
    group.add_argument("--init", action="store_true", help="設定ファイルを新規作成する")
    group.add_argument("--path", metavar="KEY", choices=PATH_KEYS, help="個別のパスを1行で出力する")
    parser.add_argument("--data-root", help="--init で使う利用者データの置き場所（絶対パス）")
    args = parser.parse_args(argv)
    stream = sys.stdout if stream is None else stream

    if args.init:
        if not args.data_root:
            _emit(stream, {"status": "invalid", "errors": ["--init には --data-root が要る"]})
            return 1
        try:
            path = init_config(args.data_root, home=home)
        except ConfigError as exc:
            status = "exists" if "既にある" in str(exc) else "invalid"
            _emit(stream, {"status": status, "errors": [str(exc)]})
            return 1
        _emit(stream, {"status": "created", "config_path": str(path)})
        return 0

    found, source = find_config_path(env=env, start_dir=start_dir, home=home)
    if found is None:
        _emit(
            stream,
            {
                "status": "unconfigured",
                "searched": searched_locations(env=env, start_dir=start_dir, home=home),
                "hint": "python jc_config.py --init --data-root <絶対パス> で作成する",
            },
        )
        return 2

    try:
        config = load_config(found, home=home)
    except ConfigError as exc:
        _emit(stream, {"status": "invalid", "config_path": str(found), "errors": [str(exc)]})
        return 1

    paths = resolve_paths(config)
    if args.path:
        print(paths[args.path], file=stream)
        return 0

    _emit(
        stream,
        {
            "status": "ok",
            "source": source,
            "config_path": config["config_path"],
            "data_root": config["data_root"],
            "python": config["python"],
            "paths": paths,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
